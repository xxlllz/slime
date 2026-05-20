import json
import os
import re
from typing import Any

try:
    from jinja2 import Template
except ImportError as e:
    raise ImportError("Jinja2 is required. Please install it with: pip install jinja2") from e

from spectro_tool_sandbox import SEMAPHORE, TOOL_CONFIGS, tool_registry

# Qwen3 tool-calling template (same as retool)
TOOL_TEMPLATE = """<|im_start|>system
{%- if messages[0]['role'] == 'system' %}
{{ messages[0]['content'] }}
{%- else %}
You are a helpful assistant.
{%- endif %}
{%- if tools %}
# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{% for tool in tools %}
{{ tool | tojson }}
{% endfor %}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call>
{%- endif %}
<|im_end|>
{%- for message in messages %}
{%- if message['role'] == 'user' %}
<|im_start|>user
{{ message['content'] }}<|im_end|>
{%- elif message['role'] == 'assistant' %}
<|im_start|>assistant
{{ message['content'] }}<|im_end|>
{%- endif %}
{%- endfor %}
<|im_start|>assistant
"""

def format_conversation_with_tools(
    prompt: str, tools: list[dict[str, Any]] = None, system_prompt: str = None, messages: list[dict[str, Any]] = None
) -> str:
    template = Template(TOOL_TEMPLATE)
    messages_to_render = []
    if system_prompt:
        messages_to_render.append({"role": "system", "content": system_prompt})
    if prompt:
        messages_to_render.append({"role": "user", "content": prompt})
    if messages:
        messages_to_render.extend(messages)
    return template.render(messages=messages_to_render, tools=tools or [])


def postprocess_predictions(prediction: str):
    # 1. Check for <SMILES>...</SMILES> (final answer)
    smiles_match = re.search(r"<SMILES>(.*?)</SMILES>", prediction, re.DOTALL)
    if smiles_match:
        return "answer", smiles_match.group(1).strip()

    # 2. Check for <tool_call> tags
    tool_call_match = re.search(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", prediction, re.DOTALL)
    if tool_call_match:
        try:
            json_str = tool_call_match.group(1)
            tool_call_data = json.loads(json_str)
            tool_name = tool_call_data.get("name")
            arguments = tool_call_data.get("arguments", {})
            if tool_name == "read_skill":
                return "read_skill", arguments.get("name", "")
            elif tool_name == "run_code":
                return "run_code", arguments.get("code", "")
        except (json.JSONDecodeError, KeyError, AttributeError):
            pass

    return None, ""


def postprocess_responses(resp: str) -> str:
    if "<SMILES>" in resp and "</SMILES>" in resp:
        return resp[: resp.index("</SMILES>") + len("</SMILES>")]

    if "<tool_call>" in resp:
        matches = list(re.finditer(r"<tool_call>\s*\{.*?\}\s*</tool_call>", resp, re.DOTALL))
        if matches:
            return resp[: matches[-1].end()]

    return resp


def format_tool_observation(content: str) -> str:
    return (
        "\n"
        "<|im_start|>user\n"
        "<tool_response>\n"
        f"{content}\n"
        "</tool_response><|im_end|>\n"
        "<|im_start|>assistant\n"
    )


_TOOL_ERRORS = (
    "Error: Unknown skill",
    "Error: SPECTRO_SKILLS_DIR is not set",
    "Error: Skill file not found",
    "Error: Memory usage too high",
    "Error: Process exited with code",
    "Error: Code execution timed out",
    "Error: Failed to execute code",
    "Error: No code provided",
    "Error: Your previous action was invalid",
)

_PRECOMPUTED_ADVANTAGE_KEY = "precomputed_advantages"
_SPECTRO_STEP_SPANS_KEY = "spectro_step_token_spans"
_SPECTRO_STEP_ACTIONS_KEY = "spectro_step_actions"
_SPECTRO_STEP_REWARDS_KEY = "spectro_step_rewards"


def has_tool_error(text: str) -> bool:
    return any(err in text for err in _TOOL_ERRORS)


async def execute_predictions(prediction: str) -> tuple[str, bool]:
    action, content = postprocess_predictions(prediction)

    if action == "read_skill":
        result = await tool_registry.execute_tool("read_skill", {"name": content.strip()})
        return format_tool_observation(result), False

    elif action == "run_code":
        code = content.strip()
        if code:
            async with SEMAPHORE:
                result = await tool_registry.execute_tool("run_code", {"code": code})
            return format_tool_observation(result), False
        else:
            return format_tool_observation("Error: No code provided"), False

    elif action == "answer":
        return "", True

    else:
        return format_tool_observation(
            "Error: Your previous action was invalid. "
            "Use read_skill to load domain knowledge, "
            "run_code to execute Python analysis code, "
            "or provide your final answer in <SMILES>...</SMILES> tags.\n"
        ), False


async def generate(args, sample, sampling_params):
    from slime.rollout.sglang_rollout import GenerateState
    from slime.utils.http_utils import post
    from slime.utils.types import Sample

    assert not args.partial_rollout, "Partial rollout is not supported for this function."

    state = GenerateState(args)
    url = f"http://{args.sglang_router_ip}:{args.sglang_router_port}/generate"

    tool_specs = tool_registry.get_tool_specs()
    prompt = format_conversation_with_tools(prompt=sample.prompt, tools=tool_specs)

    prompt_tokens_ids = state.tokenizer(prompt, add_special_tokens=False)["input_ids"]
    response = ""
    response_token_ids = []
    loss_masks = []
    tool_call_count = 0
    step_spans = []
    step_actions = []
    finish_reason_type = "stop"

    for turn in range(TOOL_CONFIGS["max_turns"]):
        total_length = len(prompt_tokens_ids) + len(response_token_ids)
        if args.rollout_max_context_len is not None:
            max_context_length = args.rollout_max_context_len
        else:
            max_context_length = args.context_parallel_size * args.max_tokens_per_gpu
        if total_length >= max_context_length:
            sample.status = Sample.Status.TRUNCATED
            finish_reason_type = "length"
            break

        current_token_ids = prompt_tokens_ids + response_token_ids
        payload = {
            "input_ids": current_token_ids,
            "sampling_params": sampling_params,
            "return_logprob": True,
        }

        output = await post(url, payload)
        finish_reason_type = output["meta_info"]["finish_reason"]["type"]

        if finish_reason_type == "abort":
            sample.status = Sample.Status.ABORTED
            return sample

        if "output_token_logprobs" in output["meta_info"]:
            cur_response_token_ids = [item[1] for item in output["meta_info"]["output_token_logprobs"]]
            cur_response = state.tokenizer.decode(cur_response_token_ids)
            cur_log_probs = [item[0] for item in output["meta_info"]["output_token_logprobs"]]
            if sample.rollout_log_probs is None:
                sample.rollout_log_probs = []
            sample.rollout_log_probs += cur_log_probs
        else:
            cur_response = output["text"]
            cur_response = postprocess_responses(cur_response)
            cur_response_token_ids = state.tokenizer(cur_response, add_special_tokens=False)["input_ids"]

        action, _ = postprocess_predictions(cur_response)
        cur_start = len(response_token_ids)
        response += cur_response
        response_token_ids += cur_response_token_ids
        cur_end = len(response_token_ids)
        loss_masks += [1] * len(cur_response_token_ids)

        if finish_reason_type == "length":
            if cur_end > cur_start:
                step_spans.append((cur_start, cur_end))
                step_actions.append("length")
            break

        next_obs, done = await execute_predictions(cur_response)
        if cur_end > cur_start:
            if done:
                step_action = "answer"
            elif action not in {"read_skill", "run_code"}:
                step_action = "invalid"
            elif has_tool_error(next_obs):
                step_action = "tool_error"
            else:
                step_action = action
            step_spans.append((cur_start, cur_end))
            step_actions.append(step_action)

        if done:
            break

        if "<tool_response>" in next_obs:
            tool_call_count += 1

        assert next_obs != "", "Next observation should not be empty."
        obs_tokens_ids = state.tokenizer(next_obs, add_special_tokens=False)["input_ids"]
        response += next_obs
        response_token_ids += obs_tokens_ids
        loss_masks += [0] * len(obs_tokens_ids)

        if sample.rollout_log_probs is not None:
            sample.rollout_log_probs += [0.0] * len(obs_tokens_ids)
            assert len(response_token_ids) == len(sample.rollout_log_probs), (
                f"Token/logp length mismatch at turn {turn}: "
                f"{len(response_token_ids)} tokens vs {len(sample.rollout_log_probs)} logps"
            )

        if tool_call_count >= TOOL_CONFIGS["max_tool_calls"]:
            if step_actions:
                step_actions[-1] = "max_tool_calls"
            break

    sample.tokens = prompt_tokens_ids + response_token_ids
    sample.response_length = len(response_token_ids)
    sample.response = response
    sample.loss_mask = loss_masks
    sample.tool_call_count = tool_call_count
    sample.train_metadata = {
        _SPECTRO_STEP_SPANS_KEY: step_spans,
        _SPECTRO_STEP_ACTIONS_KEY: step_actions,
    }

    match finish_reason_type:
        case "length":
            sample.status = Sample.Status.TRUNCATED
        case "abort":
            sample.status = Sample.Status.ABORTED
        case "stop":
            sample.status = Sample.Status.COMPLETED

    return sample


def _attach_step_rewards(sample, final_score: float) -> None:
    metadata = dict(sample.train_metadata or {})
    step_spans = metadata.get(_SPECTRO_STEP_SPANS_KEY) or []
    step_actions = metadata.get(_SPECTRO_STEP_ACTIONS_KEY) or []
    step_rewards = [0.0] * len(step_spans)

    if step_rewards:
        answer_indices = [i for i, action in enumerate(step_actions) if action == "answer"]
        reward_index = answer_indices[-1] if answer_indices else len(step_rewards) - 1
        step_rewards[reward_index] = float(final_score)

    metadata[_SPECTRO_STEP_REWARDS_KEY] = step_rewards
    metadata["spectro_final_score"] = float(final_score)
    sample.train_metadata = metadata


def _reward_to_go(step_rewards: list[float], gamma: float) -> list[float]:
    returns = [0.0] * len(step_rewards)
    running = 0.0
    for i in range(len(step_rewards) - 1, -1, -1):
        running = float(step_rewards[i]) + gamma * running
        returns[i] = running
    return returns


def _post_process_scalar_rewards(args, samples):
    import torch

    raw_rewards = [sample.get_reward_value(args) for sample in samples]
    if (
        args.advantage_estimator in ["grpo", "gspo", "reinforce_plus_plus_baseline"]
        and args.rewards_normalization
    ):
        rewards = torch.tensor(raw_rewards, dtype=torch.float)
        if rewards.shape[-1] == args.n_samples_per_prompt * args.rollout_batch_size:
            rewards = rewards.reshape(-1, args.n_samples_per_prompt)
        else:
            rewards = rewards.view(-1, rewards.shape[-1])
        rewards = rewards - rewards.mean(dim=-1, keepdim=True)
        if args.advantage_estimator in ["grpo", "gspo"] and args.grpo_std_normalization:
            rewards = rewards / (rewards.std(dim=-1, keepdim=True) + 1e-6)
        return raw_rewards, rewards.flatten().tolist()

    return raw_rewards, raw_rewards


def _compute_step_token_advantages(args, samples) -> list[list[float]]:
    import torch

    gamma = float(os.environ.get("SPECTRO_STEP_GAMMA", args.gamma))
    group_size = args.n_samples_per_prompt
    all_token_advantages = [[0.0] * sample.response_length for sample in samples]

    for group_start in range(0, len(samples), group_size):
        group_indices = list(range(group_start, min(group_start + group_size, len(samples))))
        group_returns = []

        for sample_idx in group_indices:
            metadata = samples[sample_idx].train_metadata or {}
            step_rewards = [float(x) for x in metadata.get(_SPECTRO_STEP_REWARDS_KEY, [])]
            group_returns.append(_reward_to_go(step_rewards, gamma))

        max_steps = max((len(returns) for returns in group_returns), default=0)
        group_step_advantages = [[0.0] * len(returns) for returns in group_returns]

        for step_idx in range(max_steps):
            present = [i for i, returns in enumerate(group_returns) if step_idx < len(returns)]
            if not present:
                continue

            values = torch.tensor([group_returns[i][step_idx] for i in present], dtype=torch.float32)
            if args.rewards_normalization:
                values = values - values.mean()
                if args.grpo_std_normalization and values.numel() > 1:
                    std = values.std()
                    if torch.isfinite(std) and std > 1e-6:
                        values = values / (std + 1e-6)
                    else:
                        values = torch.zeros_like(values)

            for local_i, value in zip(present, values.tolist(), strict=False):
                group_step_advantages[local_i][step_idx] = float(value)

        for local_i, sample_idx in enumerate(group_indices):
            sample = samples[sample_idx]
            metadata = sample.train_metadata or {}
            spans = metadata.get(_SPECTRO_STEP_SPANS_KEY, [])
            token_advantages = all_token_advantages[sample_idx]
            for span, advantage in zip(spans, group_step_advantages[local_i], strict=False):
                start, end = int(span[0]), int(span[1])
                start = max(0, min(start, sample.response_length))
                end = max(start, min(end, sample.response_length))
                for token_idx in range(start, end):
                    token_advantages[token_idx] = advantage

    return all_token_advantages


def convert_samples_to_train_data(args, samples):
    raw_rewards, rewards = _post_process_scalar_rewards(args, samples)
    token_advantages = _compute_step_token_advantages(args, samples)

    train_data = {
        "tokens": [sample.tokens for sample in samples],
        "response_lengths": [sample.response_length for sample in samples],
        "rewards": rewards,
        "raw_reward": raw_rewards,
        "truncated": [1 if getattr(sample.status, "value", sample.status) == "truncated" else 0 for sample in samples],
        "sample_indices": [sample.index for sample in samples],
        _PRECOMPUTED_ADVANTAGE_KEY: token_advantages,
    }

    loss_masks = []
    for sample in samples:
        if sample.loss_mask is None:
            sample.loss_mask = [1] * sample.response_length
        assert len(sample.loss_mask) == sample.response_length, (
            f"loss mask length {len(sample.loss_mask)} != response length {sample.response_length}"
        )
        if sample.remove_sample:
            sample.loss_mask = [0] * sample.response_length
        loss_masks.append(sample.loss_mask)
    train_data["loss_masks"] = loss_masks

    if samples and samples[0].rollout_log_probs is not None:
        train_data["rollout_log_probs"] = [sample.rollout_log_probs for sample in samples]

    if samples and samples[0].rollout_routed_experts is not None:
        train_data["rollout_routed_experts"] = [sample.rollout_routed_experts for sample in samples]

    if any(sample.multimodal_train_inputs is not None for sample in samples):
        train_data["multimodal_train_inputs"] = [sample.multimodal_train_inputs for sample in samples]

    if samples and samples[0].teacher_log_probs is not None:
        train_data["teacher_log_probs"] = [sample.teacher_log_probs for sample in samples]

    return train_data


def apply_precomputed_step_advantages(args, rollout_data):
    import torch
    from slime.backends.megatron_utils.cp_utils import slice_log_prob_with_cp

    kl = rollout_data["kl"]
    full_advantages = rollout_data[_PRECOMPUTED_ADVANTAGE_KEY]
    response_lengths = rollout_data["response_lengths"]
    total_lengths = rollout_data["total_lengths"]
    max_seq_lens = rollout_data.get("max_seq_lens", None)

    advantages = []
    for i, (advantage, response_length, total_length) in enumerate(
        zip(full_advantages, response_lengths, total_lengths, strict=True)
    ):
        if len(advantage) < response_length:
            advantage = list(advantage) + [0.0] * (response_length - len(advantage))
        elif len(advantage) > response_length:
            advantage = list(advantage[:response_length])

        tensor = torch.tensor(advantage, dtype=torch.float32, device=kl[i].device)
        tensor = slice_log_prob_with_cp(
            tensor,
            total_length,
            response_length,
            args.qkv_format,
            max_seq_lens[i] if max_seq_lens is not None else None,
        )
        assert tensor.shape == kl[i].shape, f"advantage shape {tensor.shape} != kl shape {kl[i].shape}"
        advantages.append(tensor)

    rollout_data["advantages"] = advantages
    rollout_data["returns"] = [adv.clone() for adv in advantages]


def _get_expected_turns(prompt: str) -> int:
    """joint_nmr (multi-modal NMR with 13C + 1H + HSQC) expects 4 turns; others expect 2."""
    if "multi-modal NMR" in prompt and "HSQC" in prompt:
        return 4
    return 2


async def reward_func(args, sample, **kwargs):
    from slime.utils.types import Sample

    if not isinstance(sample, Sample):
        raise TypeError("Sample must be an instance of Sample class.")

    response = sample.response

    # Dump rollout sample for inspection
    with open("/tmp/rollout_samples.jsonl", "a") as f:
        import json as _json
        _json.dump({"prompt": sample.prompt, "response": response, "label": sample.label}, f, ensure_ascii=False)
        f.write("\n")

    num_turns = getattr(sample, "tool_call_count", 0)

    # Penalize failed tool calls.
    if has_tool_error(response):
        label = sample.label
        if isinstance(label, dict):
            gt = label["ground_truth"][0]
        elif isinstance(label, str):
            gt = label
        else:
            gt = str(label)
        smiles_match = re.search(r"<SMILES>(.*?)</SMILES>", response, re.DOTALL)
        _attach_step_rewards(sample, -1.0)
        return {"score": -1.0, "pred": (smiles_match.group(1).strip() if smiles_match else ""), "gt": gt}

    # Extract ground truth
    label = sample.label
    if isinstance(label, dict):
        ground_truth_smiles = label["ground_truth"][0]
    elif isinstance(label, str):
        ground_truth_smiles = label
    else:
        ground_truth_smiles = str(label)

    # Extract predicted SMILES
    smiles_match = re.search(r"<SMILES>(.*?)</SMILES>", response, re.DOTALL)
    predicted_smiles = smiles_match.group(1).strip() if smiles_match else None

    result = {"score": 0.0, "pred": predicted_smiles or "", "gt": ground_truth_smiles}

    if predicted_smiles:
        try:
            from rdkit import Chem
            from rdkit.Chem import AllChem
            from rdkit.DataStructs import TanimotoSimilarity

            pred_mol = Chem.MolFromSmiles(predicted_smiles)
            gt_mol = Chem.MolFromSmiles(ground_truth_smiles)

            if pred_mol is not None and gt_mol is not None:
                pred_canonical = Chem.MolToSmiles(pred_mol)
                gt_canonical = Chem.MolToSmiles(gt_mol)

                if pred_canonical == gt_canonical:
                    result["score"] = 1.0
                else:
                    pred_fp = AllChem.GetMorganFingerprintAsBitVect(pred_mol, 2, nBits=2048)
                    gt_fp = AllChem.GetMorganFingerprintAsBitVect(gt_mol, 2, nBits=2048)
                    tanimoto = TanimotoSimilarity(pred_fp, gt_fp)
                    result["tanimoto"] = tanimoto
                    result["score"] = tanimoto
        except Exception:
            result["score"] = -1.0

    # Reward shaping: encourage tool usage
    if result["score"] < 0:
        tool_call_reward = (num_turns - 1) / 2 * 0.1
        result["score"] = min(-0.6, result["score"] + tool_call_reward)

    _attach_step_rewards(sample, float(result["score"]))

    # Log for debugging
    with open("/tmp/spectro_reward_debug.log", "a") as f:
        f.write(f"score={result['score']:.4f} pred={result.get('pred', '')[:60]:60s} gt={result['gt'][:60]:60s} turns={num_turns}\n")

    return result
