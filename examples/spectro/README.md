# Spectroscopy Agentic RL Training

Train a language model (Qwen3-4B) to use tools for molecular structure elucidation from spectral data via reinforcement learning (GRPO).

## Overview

The model learns a multi-turn agentic workflow:

```
User: [spectrum data + analysis request]
  ↓
Assistant: <think>reasoning</think>
  → tool_call: read_skill("h_nmr")        # load domain knowledge
  ← tool_response: [NMR interpretation rules]
  ↓
Assistant: <think>apply rules</think>
  → tool_call: run_code("classify peaks...") # execute analysis code
  ← tool_response: [classification results]
  ↓
Assistant: <think>combine evidence</think>
  → <SMILES>CCO</SMILES>                   # predict molecular structure
```

The RL reward compares predicted SMILES against ground truth using RDKit canonical matching + Tanimoto similarity.

## Architecture

Built on slime's pluggable rollout system, following the same pattern as `examples/retool/`, with an additional
step-level GRPO credit assignment path for multi-turn tool trajectories:

| File | Purpose |
|------|---------|
| `spectro_tool_sandbox.py` | Tool registry: `read_skill` (load domain knowledge) + `run_code` (Python sandbox) |
| `generate_with_spectro.py` | Custom async generate function (multi-turn tool loop), reward function (SMILES comparison), step-level advantage preprocessing |
| `spectro_qwen3_4b_rl.sh` | Training launch script for 8-GPU setup |
| `slime/ray/rollout.py` | Passes `precomputed_advantages` through data-parallel rollout partitioning |
| `slime/backends/megatron_utils/data.py` | Skips non-scalar `precomputed_advantages` during rollout metric logging |

### Tools

**`read_skill(name)`** — Reads a spectroscopy analysis skill guide (markdown). Available skills:

| Skill | Content |
|-------|---------|
| `h_nmr` | 1H NMR chemical shifts, multiplicities, J-coupling |
| `c_nmr` | 13C NMR carbon type classification |
| `hsqc` | 2D 1H-13C correlation assignments |
| `ir` | Infrared functional group identification |
| `raman` | Raman spectroscopy interpretation |
| `uv` | UV-Vis electronic transitions |
| `msms` | Tandem mass spectrometry fragmentation |
| `simnmr` | Simulated NMR (computational) interpretation |
| `reasoning` | Structure elucidation logic and assembly rules |

Skill files are loaded from `SPECTRO_SKILLS_DIR`. Each file must be named `skill_{name}.md`, for example `skill_h_nmr.md`.

**`run_code(code)`** — Executes Python code in a sandboxed subprocess (120s timeout, 4GB memory limit). Used by the model to classify spectral peaks, compute molecular properties, etc.

### Reward Function

The reward has two surfaces:

- `score`: scalar final-answer score used for logging and pass-rate metrics.
- `spectro_step_rewards`: per-step process rewards used by the custom step-level GRPO advantage path.

Final-answer score:

| Condition | Score |
|-----------|-------|
| Valid predicted SMILES | Morgan fingerprint Tanimoto similarity to ground truth |
| Exact or fingerprint-identical SMILES | 1.0 |
| Missing or invalid SMILES | -1.0 |
| Reward-function exception while parsing/scoring | -1.0 |

Process step rewards:

| Step | Score |
|------|-------|
| `read_skill` with a correct spectrum skill | 1.0 |
| `read_skill` with a wrong skill, unknown skill, missing skill file, or other tool error | -1.0 |
| `run_code` success | 1.0 |
| `run_code` execution error, timeout, traceback, empty code, or sandbox failure | -1.0 |
| Invalid action, context length stop, or max tool-call stop | -1.0 |
| Final answer after all required skills were read | Morgan fingerprint Tanimoto similarity |
| Final answer before all required skills were read | -1.0 |

The expected skill set is inferred from the prompt. Single-spectrum examples expect one skill, such as `h_nmr`,
`c_nmr`, `hsqc`, `ir`, `raman`, `uv`, or `msms`. Multi-spectrum inputs expect all matching skills; for example, a
joint NMR prompt containing 13C NMR, 1H NMR, and HSQC expects `c_nmr`, `h_nmr`, and `hsqc` before the final answer.

### Step-Level GRPO Credit Assignment

This example uses a custom step-level GRPO variant for agentic trajectories. The goal is to train assistant actions
inside the tool loop, not only the final answer turn.

The generator records one trainable step for each assistant-generated turn:

```text
assistant step 1: read_skill / run_code / invalid action / final answer
tool observation: loss_mask = 0
assistant step 2: read_skill / run_code / invalid action / final answer
tool observation: loss_mask = 0
assistant step 3: final answer
```

Only assistant tokens receive policy-gradient loss. Tool observation tokens remain in the model context but have
`loss_mask = 0`.

Each assistant step gets its own process reward. Tool observation tokens are kept in the context with `loss_mask = 0`.
Step returns are then computed as reward-to-go:

```text
G_t = r_t + gamma * G_{t+1}
```

By default `gamma` is `args.gamma` from the training config. It can be overridden without changing the script:

```bash
export SPECTRO_STEP_GAMMA=1.0
```

Advantage normalization is done per prompt group and per step index:

```text
A_{sample, step} = normalize_over_rollouts(G_{sample, step})
```

For example, all first tool-call steps from the same prompt group are compared with each other, all second steps are
compared with each other, and so on. The resulting step advantage is copied to every assistant token in that step span.

Important behavior:

- This is a step-index approximation. Histories before step `t` can differ across rollouts, but they are still compared
  within the same prompt group and step index.
- If all rollouts have the same return for a step, the normalized advantage for that step becomes zero.
- Do not enable `--normalize-advantages` unless you explicitly want another global masked whitening pass after the
  step-level GRPO normalization. The current implementation already normalizes at the step level.
- `rewards` and `raw_reward` are still emitted for logging and pass-rate metrics; the actual policy-gradient signal is
  supplied through `precomputed_advantages`.

The launch script enables this path with:

```bash
--custom-convert-samples-to-train-data-path generate_with_spectro.convert_samples_to_train_data
--custom-advantage-function-path generate_with_spectro.apply_precomputed_step_advantages
```

## Data

**Training prompts**: pass the JSONL path with `SPECTRO_DATA_PATH`.

Each sample:
```json
{
  "prompt": "You are a spectroscopy analysis agent... Analyze the following 1H NMR spectrum...",
  "label": {
    "ground_truth": ["CCOC(=O)CC1CCCC(Cl)C1=O"],
    "spectrum_type": "538"
  }
}
```

Covers: 1H NMR, 13C NMR, HSQC, IR, Raman, UV-Vis, MS/MS (multiple databases).

**Reference trajectories** (for SFT if needed): store them outside the repo and pass the path from your own training script.

## Usage

### Prerequisites

```bash
pip install jinja2 psutil rdkit-pypi
```

### Training

1. Export the required paths:
```bash
export HF_CHECKPOINT=/path/to/Qwen3-4B
export REF_LOAD=/path/to/Qwen3-4B_torch_dist
export MEGATRON_PATH=/path/to/Megatron-LM
export SPECTRO_DATA_PATH=/path/to/merged.jsonl
export SPECTRO_SKILLS_DIR=/path/to/spectra_skills
export SAVE_DIR=/path/to/output/checkpoints
```

Set `WANDB_KEY` only if using W&B. If `WANDB_KEY` is unset, W&B logging is disabled.

2. Launch:
```bash
cd /path/to/slime
bash examples/spectro/spectro_qwen3_4b_rl.sh
```

The script resolves `train.py` from the repository root, so it can also be launched from another working directory.

### Hardware Requirements

- 8x GPU (A100/H100 recommended)
- 6 GPUs for actor training, 2 GPUs for the sglang rollout engine
- TP=2, CP=1 in the default script
- ~16K max context length per sample

### Key Training Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `rollout-batch-size` | 24 | Longer responses than math (skill content) |
| `n-samples-per-prompt` | 8 | GRPO needs multiple samples per prompt |
| `rollout-max-response-len` | 12288 | Skill reads (~1-8K tokens) + code + reasoning |
| `rollout-max-context-len` | 16384 | Prompt (~4K) + response (12K) |
| `global-batch-size` | 192 | `rollout-batch-size * n-samples-per-prompt` |
| `lr` | 1e-6 | Conservative for RL fine-tuning |

## Differences from retool

| Aspect | retool (math) | spectro |
|--------|--------------|---------|
| Tools | `code_interpreter` only | `read_skill` + `run_code` |
| Answer format | `Answer: \boxed{...}` | `<SMILES>...</SMILES>` |
| Reward | String match via math_dapo | RDKit canonical SMILES + Tanimoto |
| Sandbox | Strict import whitelist | Relaxed (subprocess isolation) |
| Response length | ~8K tokens | ~12K tokens (skill content is large) |
| `sample.label` | Plain string | Dict with `ground_truth` list |
