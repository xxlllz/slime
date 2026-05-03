import json
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
{{- messages[0]['content'] }}
{%- else %}
You are a helpful assistant.
{%- endif %}
{%- if tools %}
# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{%- for tool in tools %}
{{- tool | tojson }}
{%- endfor %}
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
{{- message['content'] }}<|im_end|>
{%- elif message['role'] == 'assistant' %}
<|im_start|>assistant
{{- message['content'] }}<|im_end|>
{%- endif %}
{%- endfor %}
<|im_start|>assistant
"""

SYSTEM_PROMPT = (
    "You are a spectroscopy analysis agent specialized in molecular structure "
    "elucidation from spectral data. Use the read_skill tool to learn analysis "
    "techniques, then use run_code to analyze the spectrum data. Finally, provide "
    "your predicted molecular structure as SMILES wrapped in <SMILES></SMILES> tags."
)


def format_conversation_with_tools(
    prompt: str, tools: list[dict[str, Any]] = None, system_prompt: str = None, messages: list[dict[str, Any]] = None
) -> str:
    template = Template(TOOL_TEMPLATE)
    messages_to_render = []
    messages_to_render.append({"role": "system", "content": system_prompt or SYSTEM_PROMPT})
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


async def execute_predictions(prediction: str) -> tuple[str, bool]:
    action, content = postprocess_predictions(prediction)

    if action == "read_skill":
        result = await tool_registry.execute_tool("read_skill", {"name": content.strip()})
        return f"\n\n<tool_response>\n{result}\n</tool_response>\n\n", False

    elif action == "run_code":
        code = content.strip()
        if code:
            async with SEMAPHORE:
                result = await tool_registry.execute_tool("run_code", {"code": code})
            return f"\n\n<tool_response>\n{result}\n</tool_response>\n\n", False
        else:
            return "\n\n<tool_response>\nError: No code provided\n</tool_response>\n\n", False

    elif action == "answer":
        return "", True

    else:
        return (
            "\nYour previous action was invalid. "
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

    for turn in range(TOOL_CONFIGS["max_turns"]):
        total_length = len(prompt_tokens_ids) + len(response_token_ids)
        if args.rollout_max_context_len is not None:
            max_context_length = args.rollout_max_context_len
        else:
            max_context_length = args.context_parallel_size * args.max_tokens_per_gpu
        if total_length >= max_context_length:
            sample.status = Sample.Status.TRUNCATED
            break

        current_token_ids = prompt_tokens_ids + response_token_ids
        payload = {
            "input_ids": current_token_ids,
            "sampling_params": sampling_params,
            "return_logprob": True,
        }

        output = await post(url, payload)

        if output["meta_info"]["finish_reason"]["type"] == "abort":
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

        response += cur_response
        response_token_ids += cur_response_token_ids
        loss_masks += [1] * len(cur_response_token_ids)

        if output["meta_info"]["finish_reason"]["type"] == "length":
            break

        next_obs, done = await execute_predictions(cur_response)
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
            break

    sample.tokens = prompt_tokens_ids + response_token_ids
    sample.response_length = len(response_token_ids)
    sample.response = response
    sample.loss_mask = loss_masks
    sample.tool_call_count = tool_call_count

    match output["meta_info"]["finish_reason"]["type"]:
        case "length":
            sample.status = Sample.Status.TRUNCATED
        case "abort":
            sample.status = Sample.Status.ABORTED
        case "stop":
            sample.status = Sample.Status.COMPLETED

    return sample


async def reward_func(args, sample, **kwargs):
    from slime.utils.types import Sample

    if not isinstance(sample, Sample):
        raise TypeError("Sample must be an instance of Sample class.")

    response = sample.response
    num_turns = getattr(sample, "tool_call_count", 0)

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

    result = {"score": -1.0, "pred": predicted_smiles or "", "gt": ground_truth_smiles}

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

                    if tanimoto >= 0.85:
                        result["score"] = 0.5
                    elif tanimoto >= 0.6:
                        result["score"] = 0.2
                    else:
                        result["score"] = -0.5
        except Exception:
            result["score"] = -1.0

    # Reward shaping: encourage tool usage
    if result["score"] < 0:
        tool_call_reward = (num_turns - 2) / 2 * 0.1
        result["score"] = min(-0.6, result["score"] + tool_call_reward)

    return result
