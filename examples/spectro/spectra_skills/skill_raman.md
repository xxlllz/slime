# Raman Spectroscopy Skill

## What it measures
Raman spectroscopy measures inelastic scattering of light by molecular vibrations. It is complementary to IR: vibrations that are IR-inactive (no dipole change) are often Raman-active (polarizability change), and vice versa.

## Key differences from IR
- **Symmetric stretches** are strong in Raman (weak in IR): C=C, C-C, S-S, aromatic breathing
- **Polar groups** are weak in Raman (strong in IR): O-H, C=O, N-H
- **No water interference**: Raman works in aqueous solution
- **Same wavenumber axis** (cm⁻¹) as IR

## Key observables
- **Position (cm⁻¹)**: Vibrational frequency
- **Intensity**: Related to polarizability change (not dipole)

## Characteristic Raman bands (overlapping ranges)

| Range (cm⁻¹) | Group | Raman behavior |
|--------------|-------|---------------|
| 3300-3800 | sp C-H/free OH | Alkyne C-H or free OH, medium |
| 3500-4000 | free O-H/N-H | Weak in Raman |
| 3100-3500 | O-H/N-H | Weak (use IR instead) |
| 2950-3250 | sp2 C-H/Ar-H | Medium |
| 2750-3050 | sp3 C-H | Medium-strong |
| 2300-2800 | silent region | Very few Raman bands in this region |
| 2100-2350 | C#N/C#C | Medium (symmetric: strong Raman) |
| 1900-2200 | C#C/C=C=C | Alkyne **very strong**, cumulated diene weak-medium |
| 1580-1820 | C=C/C=O | C=C **strong**; C=O weak in Raman |
| 1520-1620 | Ar ring | **Strong** — ring quadrant stretch |
| 1380-1550 | C-H bend/Ar | Medium, C-H deformation |
| 1230-1420 | C-H wag | CH2/CH3 wagging modes |
| 980-1280 | C-O/C-C/ring | Ring breathing modes are strong |
| 780-1030 | Ar breath/=CH | **Very strong** at ~1000 cm⁻¹ for monosubstituted benzene |
| 580-820 | C-S/C-Cl | C-S is **strong** in Raman |
| 380-630 | S-S/ring def | S-S is **very strong** (~500 cm⁻¹), diagnostic for disulfides |
| 180-420 | lattice/skeletal | Low-frequency framework vibrations |

> Note: Ranges deliberately overlap. A peak in an overlap zone matches multiple groups — all possibilities are reported.

## Raman-specific diagnostics

| Feature | Meaning |
|---------|---------|
| Strong band ~1000 cm⁻¹ | Monosubstituted benzene ring breathing |
| Strong band ~1600 cm⁻¹ | C=C or aromatic ring present |
| Strong band ~2100 cm⁻¹ | C≡C triple bond (may be invisible in IR!) |
| Strong band ~500 cm⁻¹ | S-S disulfide bond |
| Strong bands 2800-3000 with nothing above 3000 | Saturated aliphatic, no aromatic/vinyl |

## Complementary use with IR
- If IR shows strong 1720 cm⁻¹ (C=O) but Raman is weak there → confirms carbonyl
- If Raman shows strong 2100 cm⁻¹ but IR is silent → symmetric alkyne (R-C≡C-R)
- Both show 1600 cm⁻¹ → aromatic ring (active in both)

## QM9sp computational data caveat
Same as IR: DFT-computed Raman frequencies are systematically higher (~50-150 cm⁻¹).
- **sp2/sp3 C-H merged**: treat 2800-3200 cm⁻¹ as generic "C-H stretch"
- The "nothing above 3000 → saturated aliphatic" rule does NOT apply to QM9sp
