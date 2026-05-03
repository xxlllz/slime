#!/bin/bash

# for rerun the task
pkill -9 sglang
sleep 3
ray stop --force
pkill -9 ray
pkill -9 python
sleep 3
pkill -9 ray
pkill -9 python

set -ex

export PYTHONBUFFERED=16

NVLINK_COUNT=$(nvidia-smi topo -m 2>/dev/null | grep -o 'NV[0-9][0-9]*' | wc -l)
if [ "$NVLINK_COUNT" -gt 0 ]; then
    HAS_NVLINK=1
else
    HAS_NVLINK=0
fi
echo "HAS_NVLINK: $HAS_NVLINK (detected $NVLINK_COUNT NVLink references)"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
SLIME_DIR="$(cd -- "${SCRIPT_DIR}/../.." &>/dev/null && pwd)"
source "${SLIME_DIR}/scripts/models/qwen3-4B.sh"

require_path() {
   local var_name="$1"
   local path_value="$2"
   if [ -z "${path_value}" ]; then
      echo "ERROR: ${var_name} is required." >&2
      exit 1
   fi
   if [ ! -e "${path_value}" ]; then
      echo "ERROR: ${var_name} does not exist: ${path_value}" >&2
      exit 1
   fi
}

HF_CHECKPOINT="${HF_CHECKPOINT:-}"
REF_LOAD="${REF_LOAD:-}"
SAVE_DIR="${SAVE_DIR:-${SLIME_DIR}/outputs/spectro/qwen3-4b-spectro-rl}"
SPECTRO_DATA_PATH="${SPECTRO_DATA_PATH:-${SLIME_DIR}/examples/spectro/data/merged.jsonl}"
SPECTRO_SKILLS_DIR="${SPECTRO_SKILLS_DIR:-${SLIME_DIR}/examples/spectro/spectra_skills}"
MEGATRON_PATH="${MEGATRON_PATH:-}"

require_path HF_CHECKPOINT "${HF_CHECKPOINT}"
require_path REF_LOAD "${REF_LOAD}"
require_path SPECTRO_DATA_PATH "${SPECTRO_DATA_PATH}"
require_path SPECTRO_SKILLS_DIR "${SPECTRO_SKILLS_DIR}"
require_path MEGATRON_PATH "${MEGATRON_PATH}"
mkdir -p "${SAVE_DIR}"

CKPT_ARGS=(
   --hf-checkpoint "${HF_CHECKPOINT}"
   --ref-load "${REF_LOAD}"
   --save "${SAVE_DIR}"
   --save-interval 20
   --rotary-base 5000000
)

ROLLOUT_ARGS=(
   --prompt-data "${SPECTRO_DATA_PATH}"
   --input-key prompt
   --label-key label
   --rollout-shuffle
   --reward-key score
   --num-rollout 3000
   --rollout-batch-size 16
   --n-samples-per-prompt 8
   --rollout-max-response-len 12288
   --rollout-max-context-len 16384
   --rollout-temperature 1

   --global-batch-size 128
   --balance-data
)

EVAL_ARGS=(
   --eval-interval 50
)

PERF_ARGS=(
   --tensor-model-parallel-size 2
   --sequence-parallel
   --pipeline-model-parallel-size 1
   --context-parallel-size 1
   --expert-model-parallel-size 1
   --expert-tensor-parallel-size 1

   --recompute-granularity full
   --recompute-method uniform
   --recompute-num-layers 1

   --use-dynamic-batch-size
   --max-tokens-per-gpu 16384
)

GRPO_ARGS=(
   --advantage-estimator grpo
   --use-kl-loss
   --kl-loss-coef 0.00
   --kl-loss-type low_var_kl
   --entropy-coef 0.00
   --eps-clip 0.2
   --eps-clip-high 0.28
)

OPTIMIZER_ARGS=(
   --optimizer adam
   --lr 1e-6
   --lr-decay-style constant
   --weight-decay 0.1
   --adam-beta1 0.9
   --adam-beta2 0.98
)

WANDB_ARGS=()
if [ -n "${WANDB_KEY:-}" ]; then
   WANDB_ARGS=(
      --use-wandb
      --wandb-project slime-spectro
      --wandb-group qwen3-4B-spectro-rl
      --wandb-key "${WANDB_KEY}"
   )
fi

SGLANG_ARGS=(
   --rollout-num-gpus-per-engine 2
   --sglang-mem-fraction-static 0.7
)

MISC_ARGS=(
   --attention-dropout 0.0
   --hidden-dropout 0.0
   --accumulate-allreduce-grads-in-fp32
   --attention-softmax-in-fp32
   --attention-backend flash
)

CUSTOM_ARGS=(
   --custom-generate-function-path generate_with_spectro.generate
   --custom-rm-path generate_with_spectro.reward_func
)

# launch ray
export MASTER_ADDR=${MASTER_ADDR:-"127.0.0.1"}
ray start --head --node-ip-address ${MASTER_ADDR} --num-gpus 4 --disable-usage-stats --dashboard-host=0.0.0.0 --dashboard-port=8265

RUNTIME_ENV_JSON="{
  \"env_vars\": {
    \"PYTHONPATH\": \"${MEGATRON_PATH}:${SCRIPT_DIR}:${SLIME_DIR}:${PYTHONPATH:-}\",
    \"CUDA_DEVICE_MAX_CONNECTIONS\": \"1\",
    \"NCCL_NVLS_ENABLE\": \"${HAS_NVLINK}\",
    \"SPECTRO_SKILLS_DIR\": \"${SPECTRO_SKILLS_DIR}\"
  }
}"

ray job submit --address="http://127.0.0.1:8265" \
   --runtime-env-json="${RUNTIME_ENV_JSON}" \
   -- python3 "${SLIME_DIR}/train.py" \
   --actor-num-nodes 1 \
   --actor-num-gpus-per-node 4 \
   --colocate \
   ${MODEL_ARGS[@]} \
   ${CKPT_ARGS[@]} \
   ${ROLLOUT_ARGS[@]} \
   ${OPTIMIZER_ARGS[@]} \
   ${GRPO_ARGS[@]} \
   ${WANDB_ARGS[@]} \
   ${PERF_ARGS[@]} \
   ${EVAL_ARGS[@]} \
   ${SGLANG_ARGS[@]} \
   ${MISC_ARGS[@]} \
   ${CUSTOM_ARGS[@]}
