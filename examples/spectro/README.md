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

Built on slime's pluggable rollout system, following the same pattern as `examples/retool/`:

| File | Purpose |
|------|---------|
| `spectro_tool_sandbox.py` | Tool registry: `read_skill` (load domain knowledge) + `run_code` (Python sandbox) |
| `generate_with_spectro.py` | Custom async generate function (multi-turn tool loop) + reward function (SMILES comparison) |
| `spectro_qwen3_4b_rl.sh` | Training launch script for 4-GPU setup |

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

| Condition | Score |
|-----------|-------|
| Exact canonical SMILES match | 1.0 |
| Tanimoto similarity >= 0.85 | 0.5 |
| Tanimoto similarity >= 0.6 | 0.2 |
| Valid but wrong SMILES | -0.5 |
| Invalid or missing SMILES | -1.0 |

Tool usage bonus: incorrect answers with 2+ tool calls get reduced penalty (encourages tool use).

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

- 4x GPU (A100/H100 recommended)
- TP=2 for training, 2 GPUs for sglang rollout engine
- ~16K max context length per sample

### Key Training Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `rollout-batch-size` | 16 | Longer responses than math (skill content) |
| `n-samples-per-prompt` | 8 | GRPO needs multiple samples per prompt |
| `rollout-max-response-len` | 12288 | Skill reads (~1-8K tokens) + code + reasoning |
| `rollout-max-context-len` | 16384 | Prompt (~4K) + response (12K) |
| `global-batch-size` | 128 | Adjusted for longer sequences |
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
