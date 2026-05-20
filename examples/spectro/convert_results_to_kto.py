import json
import re
import sys
from rdkit import Chem


def extract_smiles(text):
    """Extract SMILES from text."""
    match = re.search(r'<SMILES>(.*?)</SMILES>', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def canonical_smiles(smiles_str):
    """Get canonical SMILES using RDKit."""
    try:
        mol = Chem.MolFromSmiles(smiles_str)
        if mol is not None:
            return Chem.MolToSmiles(mol)
    except Exception:
        pass
    return None


def process_result(result):
    """Convert a single result to KTO format."""
    messages = result['messages']

    # Add loss=false to all assistant messages except the last one
    assistant_indices = [i for i, m in enumerate(messages) if m['role'] == 'assistant']
    for idx in assistant_indices[:-1]:
        messages[idx]['loss'] = False

    # Extract ground truth and predicted SMILES
    gt_smiles = extract_smiles(result['label'])
    last_assistant = messages[assistant_indices[-1]] if assistant_indices else None
    pred_smiles = extract_smiles(last_assistant['content']) if last_assistant else None

    # Compare canonical SMILES
    is_correct = False
    if gt_smiles and pred_smiles:
        gt_canonical = canonical_smiles(gt_smiles)
        pred_canonical = canonical_smiles(pred_smiles)
        if gt_canonical and pred_canonical:
            is_correct = gt_canonical == pred_canonical

    kto_sample = {
        "messages": messages,
        "label": is_correct,
    }

    return kto_sample, is_correct, gt_smiles, pred_smiles


def process_file(input_path, output_path, append=False):
    """Process a result file and write KTO samples."""
    with open(input_path, 'r') as f:
        data = json.load(f)

    results = data['results']
    kto_samples = []
    stats = {"correct": 0, "incorrect": 0, "no_smiles": 0, "total": len(results)}

    for i, result in enumerate(results):
        kto_sample, is_correct, gt, pred = process_result(result)
        kto_samples.append(kto_sample)

        if is_correct:
            stats["correct"] += 1
        elif pred:
            stats["incorrect"] += 1
        else:
            stats["no_smiles"] += 1

        if (i + 1) % 1000 == 0:
            print(f"  Processed {i+1}/{len(results)}...")

    mode = 'a' if append else 'w'
    with open(output_path, mode) as f:
        for sample in kto_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")

    print(f"Done: {input_path}")
    print(f"  Total: {stats['total']}, Correct: {stats['correct']}, Incorrect: {stats['incorrect']}, No SMILES: {stats['no_smiles']}")
    print(f"  Accuracy: {stats['correct']/stats['total']*100:.2f}%")
    return stats


if __name__ == "__main__":
    output_file = "/data/zxl/slime/examples/spectro/kto_14094_last_only.jsonl"

    # Process part02
    print("=== Processing part02 ===")
    stats02 = process_file(
        "/data/zxl/slime/examples/spectro/results_14094/0423_part02_result.json",
        output_file,
        append=True
    )

    # Process part03
    print("\n=== Processing part03 ===")
    stats03 = process_file(
        "/data/zxl/slime/examples/spectro/results_14094/0423_part03_result.json",
        output_file,
        append=True
    )

    # Final stats
    print("\n=== Final Summary ===")
    total = stats02["total"] + stats03["total"]
    correct = stats02["correct"] + stats03["correct"]
    incorrect = stats02["incorrect"] + stats03["incorrect"]
    no_smiles = stats02["no_smiles"] + stats03["no_smiles"]
    print(f"Total new samples: {total}")
    print(f"Correct: {correct}, Incorrect: {incorrect}, No SMILES: {no_smiles}")
    print(f"Accuracy: {correct/total*100:.2f}%")

    # Count total lines in output file
    with open(output_file, 'r') as f:
        total_lines = sum(1 for _ in f)
    print(f"Total lines in {output_file}: {total_lines}")
