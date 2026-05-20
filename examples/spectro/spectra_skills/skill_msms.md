# MS/MS (Tandem Mass Spectrometry) Skill

## What it measures
MS/MS measures molecular fragmentation. A precursor ion is selected and fragmented by collision, producing fragment ions. The pattern of fragments reveals the molecular structure.

## Key observables
- **Precursor m/z**: Molecular ion mass (gives molecular weight)
- **Adduct type**: [M+H]+ (positive, M = precursor - 1.0073), [M+Na]+ (M = precursor - 22.9892), [M-H]- (negative, M = precursor + 1.0073)
- **Fragment m/z values**: Masses of breakdown products
- **Fragment intensity**: Relative abundance (higher = more favorable fragmentation)
- **Fragment annotations** (if available): Molecular formula or SMILES of each fragment

## Step 1: Molecular formula from precursor mass

Given the neutral mass M, enumerate possible molecular formulas CxHyNnOoSs... within mass tolerance (typically 5 ppm for high-resolution MS):
- **Small molecules (<250 Da)**: Few candidates, usually unique at 5 ppm
- **Medium molecules (250-500 Da)**: ~10 candidates, need element constraints
- **Large molecules (>500 Da)**: Many candidates, use 10 ppm, fragment annotations help constrain elements

### Element constraints from fragments
If fragment annotations are molecular formulas (e.g., C4O3H4), the union of elements across all fragments tells you which elements exist in the molecule. This dramatically reduces the search space.

### RDBE (Ring and Double Bond Equivalence)
RDBE = 1 + C - H/2 + N/2 (for CHNO molecules)
- RDBE < 0 → chemically impossible
- RDBE = 4 → one benzene ring or equivalent
- RDBE ≥ 4 with aromatic fragments → aromatic compound

### Chemical plausibility scoring for formula ranking
When multiple formula candidates have similar ppm errors, rank by plausibility:
- **N/C ratio > 0.4** → penalty (most organics have N/C < 0.4)
- **O/C ratio > 1.0** → penalty (most organics have O/C < 1.0)
- **RDBE/C ratio > 0.65** → penalty (overly unsaturated; benzene = 0.67 is the practical limit for typical organics)
- **RDBE > mass/20** → penalty (too many degrees of unsaturation for the molecular size)
- **C < mass/20** → penalty (too few carbons for the molecular weight)
- Formulas with no carbon but containing N/O → strongly penalized

## Step 2: Neutral loss analysis

Neutral loss = precursor m/z - fragment m/z. Each loss corresponds to a specific structural moiety:

| Loss (Da) | Formula | Functional group |
|-----------|---------|-----------------|
| 15.024 | CH3 | Methyl group |
| 17.003 | OH | Hydroxyl radical |
| 18.011 | H2O | Alcohol, carboxylic acid (dehydration) |
| 27.995 | CO | Carbonyl group (ketone, quinone) |
| 28.031 | C2H4 | Ethyl group (ethyl ester/ether retro-cleavage) |
| 31.018 | OCH3 | Methoxy group |
| 32.026 | CH3OH | Methanol (methyl ester) |
| 42.011 | CH2CO | Ketene (acetyl group) |
| 43.990 | CO2 | Carboxyl group (-COOH) |
| 46.005 | CH2O2 | Formic acid (formate ester) |
| 60.021 | C2H4O2 | Acetic acid (acetate ester) |
| 63.962 | SO2 | Sulfone, sulfonate |
| 79.957 | SO3 | Sulfate ester |
| 79.966 | HPO3 | Phosphate |
| 162.053 | C6H10O5 | Hexose sugar (glycosides) |
| 176.032 | C6H8O6 | Glucuronic acid |

### Reasoning with neutral losses
- Loss of 18 (H2O) → molecule has OH group (alcohol, carboxylic acid, or hemiacetal)
- Loss of 28 (CO) → carbonyl present, often from ketones/quinones after ring opening
- Loss of 44 (CO2) → carboxylic acid or carbonate
- Loss of 31 (OCH3) → methoxy group present
- Sequential losses: H2O + CO = loss of 46 → phenolic acid fragmentation

## Step 3: Diagnostic fragment ions

Certain fragment m/z values are structural fingerprints. **Caution**: matching by m/z alone can cause false positives — a peak near m/z 91 does not guarantee tropylium. Always cross-check with neutral losses and molecular formula.

| m/z | Ion | Structural meaning | False positive risk |
|-----|-----|-------------------|-------------------|
| 77.04 | C6H5+ | Phenyl cation → benzene ring | Low — very specific |
| 91.05 | C7H7+ | Tropylium/benzyl → toluene/benzyl moiety | **Medium** — other C7H7 isomers exist |
| 105.03 | C7H5O+ | Benzoyl → benzoic acid derivative | Low |
| 120.08 | C8H10N+ | Phenylalanine immonium → contains Phe | **High** if not a peptide |
| 130.07 | C9H8N+ | Tryptophan immonium → contains Trp | **High** if not a peptide |
| 136.06 | C5H6N5+ | Adenine+H → nucleoside/nucleotide | **High** if not nucleotide |
| 147.04 | C9H7O2+ | Coumarin fragment → coumarin scaffold | Medium |
| 152.06 | C5H6N5O+ | Guanine+H → guanine nucleoside | **High** if not nucleotide |

**Matching tolerance**: Use ±0.003 Da (3 mDa) for high-resolution data. Wider tolerances cause frequent false positives — e.g., a non-peptide fragment at m/z 130.065 can be misidentified as tryptophan immonium (130.066). When in doubt, cross-validate with neutral losses.

## Data source differences

| Source | Fragment annotation | Precursor type | Notes |
|--------|-------------------|---------------|-------|
| ICEBERG | Molecular formula (C4O3H4) | [M+H]+ (ion m/z) | ~300 fragments per spectrum |
| SCARF | Molecular formula | Neutral mass M | ~300 fragments |
| CFM-ID (pos) | SMILES fragment | [M+H]+ (ion m/z) | ~10-40 fragments |
| CFM-ID (neg) | SMILES fragment | [M-H]- (ion m/z) | ~3-25 fragments |
| MassSpecGym | None (m/z + intensity only) | [M+H]+ or [M+Na]+ (explicit in metadata) | Real experimental data |

## MassSpecGym limitations
MassSpecGym has **no fragment annotations**, so:
- Element detection relies on default assumption (C,H,N,O,S) — may miss halogens (F,Cl,Br)
- Formula candidates are less constrained → top-1 accuracy is lower for medium/large molecules
- Formula ranking should be treated as a candidate list, not a definitive answer
- Neutral loss and diagnostic fragment analysis remain valid regardless
