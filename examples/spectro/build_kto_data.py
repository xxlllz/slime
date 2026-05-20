import asyncio
import json
import re
from typing import Any

from generate_with_spectro import (
    format_conversation_with_tools,
    postprocess_predictions,
    postprocess_responses,
    format_tool_observation,
    execute_predictions,
    TOOL_TEMPLATE,
)
from spectro_tool_sandbox import TOOL_CONFIGS, tool_registry
from slime.utils.http_utils import post


async def generate_trajectory(args, sample, sampling_params):
    """Generate a multi-turn trajectory with tool calls."""
    url = f"http://{args.sglang_router_ip}:{args.sglang_router_port}/generate"

    tool_specs = tool_registry.get_tool_specs()
    prompt = format_conversation_with_tools(prompt=sample.prompt, tools=tool_specs)

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.hf_checkpoint, trust_remote_code=True)
    prompt_tokens_ids = tokenizer(prompt, add_special_tokens=False)["input_ids"]

    response = ""
    response_token_ids = []
    messages = []
    tool_call_count = 0

    for turn in range(TOOL_CONFIGS["max_turns"]):
        total_length = len(prompt_tokens_ids) + len(response_token_ids)
        if total_length >= args.rollout_max_context_len:
            break

        current_token_ids = prompt_tokens_ids + response_token_ids
        payload = {
            "input_ids": current_token_ids,
            "sampling_params": sampling_params,
            "return_logprob": False,
        }

        output = await post(url, payload)
        cur_response = output["text"]
        cur_response = postprocess_responses(cur_response)
        response += cur_response
        response_token_ids += tokenizer(cur_response, add_special_tokens=False)["input_ids"]

        if output["meta_info"]["finish_reason"]["type"] == "length":
            break

        next_obs, done = await execute_predictions(cur_response)
        if done:
            break

        if "<tool_response>" in next_obs:
            tool_call_count += 1

        response += next_obs
        response_token_ids += tokenizer(next_obs, add_special_tokens=False)["input_ids"]

        if tool_call_count >= TOOL_CONFIGS["max_tool_calls"]:
            break

    return response, tool_call_count


async def build_kto_sample(args, sample_data, tokenizer):
    """Build a single KTO sample."""
    from slime.utils.types import Sample

    sample = Sample()
    sample.prompt = sample_data["prompt"]
    sample.label = sample_data["label"]

    sampling_params = {
        "temperature": args.temperature,
        "max_new_tokens": args.max_new_tokens,
    }

    response, tool_call_count = await generate_trajectory(args, sample, sampling_params)

    # Build messages for KTO
    tool_specs = tool_registry.get_tool_specs()
    prompt_text = format_conversation_with_tools(prompt=sample.prompt, tools=tool_specs)

    # Parse the full response into messages
    messages = []

    # Extract tool calls and responses from the generated text
    # The response format is: assistant_text + <|im_end|>\n<|im_start|>user\n<tool_response>... + <|im_end|>\n<|im_start|>assistant\n + next_turn
    parts = re.split(r'(<\|im_end\|>\n<\|im_start\|>user\n<tool_response>.*?</tool_response><\|im_end\|>\n<\|im_start\|>assistant\n)', response, flags=re.DOTALL)

    # For simplicity, store the full response as assistant content
    # In practice you may want to parse into separate turns
    messages = [
        {"role": "user", "content": sample.prompt},
    ]

    # Extract assistant turns and tool responses
    turn_pattern = r'<\|im_start\|>assistant\n(.*?)<\|im_end\|>'
    assistant_turns = re.findall(turn_pattern, response, re.DOTALL)

    # Build proper messages sequence
    messages = []
    # system is optional
    # user prompt
    messages.append({"role": "user", "content": sample.prompt})

    # Parse the response into assistant/tool turns
    # The response contains: assistant_text + observation + assistant_text + observation + ...
    remaining = response
    while remaining:
        # Find next tool_response
        tool_resp_match = re.search(r'<tool_response>\n(.*?)</tool_response>', remaining, re.DOTALL)
        if tool_resp_match:
            # Everything before tool_response is assistant content
            before = remaining[:tool_resp_match.start()]
            # The tool response content
            tool_content = tool_resp_match.group(1)
            # Everything after
            remaining = remaining[tool_resp_match.end():]

            # Clean up before text
            before = before.strip()
            if before:
                messages.append({"role": "assistant", "content": before})
            messages.append({"role": "tool_response", "content": tool_content})
        else:
            # No more tool responses, rest is final assistant answer
            remaining = remaining.strip()
            if remaining:
                messages.append({"role": "assistant", "content": remaining})
            break

    # Compute label using RDKit
    from rdkit import Chem
    label = sample_data["label"]
    if isinstance(label, dict):
        gt_smiles = label["ground_truth"][0]
    else:
        gt_smiles = label

    smiles_match = re.search(r"<SMILES>(.*?)</SMILES>", response, re.DOTALL)
    predicted_smiles = smiles_match.group(1).strip() if smiles_match else None

    is_correct = False
    if predicted_smiles:
        try:
            pred_mol = Chem.MolFromSmiles(predicted_smiles)
            gt_mol = Chem.MolFromSmiles(gt_smiles)
            if pred_mol is not None and gt_mol is not None:
                pred_canonical = Chem.MolToSmiles(pred_mol)
                gt_canonical = Chem.MolToSmiles(gt_mol)
                is_correct = pred_canonical == gt_canonical
        except Exception:
            pass

    kto_sample = {
        "tools": json.dumps(tool_specs),
        "messages": messages,
        "label": is_correct,
    }

    return kto_sample, response, predicted_smiles, gt_smiles, is_correct


class Args:
    sglang_router_ip = "127.0.0.1"
    sglang_router_port = 15000
    rollout_max_context_len = 16384
    hf_checkpoint = "/workspace/output/qwen3-4b-think-toolcall-0423/v0-20260505-111806/checkpoint-10000"
    temperature = 1.0
    max_new_tokens = 2048


async def main():
    args = Args()

    # Read input data
    input_path = "/workspace/slime/examples/spectro/0423_rl.jsonl"
    output_path = "/workspace/slime/examples/spectro/kto_agent_data.jsonl"

    with open(input_path) as f:
        lines = [json.loads(line) for line in f]

    # Take a small batch for testing
    test_lines = lines[:50]

    kto_samples = []
    stats = {"correct": 0, "incorrect": 0, "no_smiles": 0}

    for i, data in enumerate(test_lines):
        print(f"Processing {i+1}/{len(test_lines)}...")
        try:
            kto_sample, response, pred, gt, is_correct = await build_kto_sample(args, data, None)
            kto_samples.append(kto_sample)

            if is_correct:
                stats["correct"] += 1
            elif pred:
                stats["incorrect"] += 1
            else:
                stats["no_smiles"] += 1

            print(f"  pred={pred[:40] if pred else 'None':40s} gt={gt[:40]:40s} correct={is_correct}")
        except Exception as e:
            print(f"  ERROR: {e}")

    # Save KTO data
    with open(output_path, "w") as f:
        for sample in kto_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")

    print(f"\nDone! Saved {len(kto_samples)} samples to {output_path}")
    print(f"Stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
