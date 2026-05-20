# SimNMR (Simulated NMR) Skill

## What it is
SimNMR data contains computationally predicted 1H and 13C NMR chemical shifts for molecules from PubChem. Unlike experimental NMR, SimNMR provides only chemical shift values — no multiplicity, no J-coupling, no integration (nH).

## Key differences from experimental NMR

| Feature | Experimental NMR | SimNMR |
|---------|-----------------|--------|
| Chemical shifts | Yes | Yes |
| Multiplicity (s/d/t/q) | Yes | **No** |
| J-coupling values | Yes | **No** |
| Integration (nH) | Yes | **No** |
| Peak count | Unique environments | **All individual H/C atoms** (may have duplicates at similar shifts) |

## Interpretation strategy for 1H SimNMR

Since we only have shift values (no nH or multiplicity), we reason by:

1. **Shift distribution**: Count peaks in each chemical shift region (same overlapping ranges as 1H NMR skill)
   - Many peaks in 6.0-8.5 ppm → aromatic-rich molecule
   - Many peaks in 0.5-2.2 ppm → aliphatic-rich
   - Peaks in 2.8-4.7 ppm → heteroatom-attached CH

2. **Total peak count**: Approximates total H count
   - SimNMR lists each individual H, so count ≈ total H in molecule
   - Clustered shifts (e.g., three shifts at ~1.9 ppm) → likely equivalent CH3

3. **Shift range**: Max - min shift indicates molecular diversity
   - Narrow range (e.g., 1-3 ppm only) → simple aliphatic
   - Wide range (e.g., 1-9 ppm) → complex molecule with multiple functional groups

## Interpretation strategy for 13C SimNMR

1. **Peak count** = number of unique carbon environments
   - Useful for estimating molecular formula (C count)
   - Fewer peaks than expected → molecular symmetry

2. **Region distribution**:
   - Peaks in 100-160 ppm → sp2 carbons (aromatic/vinyl)
   - Peaks in 160-220 ppm → carbonyl carbons
   - Peaks in 0-90 ppm → sp3 carbons
   - Ratio of sp2/sp3 → degree of unsaturation

3. **Specific markers**:
   - Peak near 170 ppm → ester/amide/acid carbonyl
   - Peak near 55 ppm → OCH3 or NCH
   - Peaks in 110-150 ppm → aromatic ring (6 peaks ≈ monosubstituted benzene)

## Limitations
- No multiplicity → cannot determine coupling partners
- No integration → cannot count equivalent H
- Simulated → may differ from experimental by 1-3 ppm
- Clustered shifts may merge in real experiment
