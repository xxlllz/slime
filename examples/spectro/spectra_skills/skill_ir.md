# Infrared (IR) Spectroscopy Skill

## What it measures
IR spectroscopy measures molecular vibrations (stretching, bending). Each functional group absorbs at characteristic frequencies (wavenumber, cm⁻¹). Peak intensity reflects the change in dipole moment during vibration.

## Key observables
- **Position (cm⁻¹)**: Type of bond/functional group
- **Intensity**: Strong vs weak absorption (dipole moment change)
- **Shape**: Broad (H-bonded OH) vs sharp (free OH, C=O)

## Spectral regions

### Diagnostic region (4000-1500 cm⁻¹)
Specific functional group stretches — most useful for identification.

| Range (cm⁻¹) | Group | Notes |
|--------------|-------|-------|
| 3700-4000 | #C-H/free OH | Alkyne C-H stretch or free OH overtone |
| 3500-3750 | free O-H/N-H | Sharp peak, non-hydrogen-bonded OH or NH |
| 3000-3300 | sp2 C-H/Ar-H | Aromatic/vinyl C-H stretch |
| 3100-3600 | O-H/N-H | Broad for OH, sharper for NH; NH2 shows 2 peaks |
| 2800-3100 | sp3 C-H | Alkyl C-H stretch |
| 2650-2900 | CHO(C-H)/overtone | Aldehyde C-H (Fermi resonance), overtones |
| 2400-2700 | O-H(acid)/overtone | Very broad, carboxylic acid O-H |
| 2100-2500 | C#N/C#C/CO2/isocyanate | Nitrile, alkyne, CO2, azide, isocyanate |
| 1650-1780 | C=O | Ester ~1735, acid ~1710, amide ~1660 |
| 1550-1700 | C=O(conj)/C=C/Ar | Conjugated C=O, alkene C=C, aromatic ring stretch |
| 1450-1600 | Ar C=C/NO2(asym) | Aromatic ring C=C, NO2 asymmetric stretch |

### Fingerprint region (1500-400 cm⁻¹)

| Range (cm⁻¹) | Group | Notes |
|--------------|-------|-------|
| 1350-1500 | C-H bend/NO2/Ar | CH2/CH3 deformation, aromatic |
| 1200-1400 | C-O/NO2(sym)/C-N | Ester C-O, NO2 symmetric, amine |
| 1000-1250 | C-O/C-N/C-C | Alcohols, amines, ethers |
| 800-1050 | =C-H oop/Ar C-H oop | Out-of-plane bending |
| 600-850 | C-Cl/C-Br/C-S | Halogen and sulfur stretch |
| 400-650 | C-I/ring def | Iodide stretch or ring deformation |

> Note: Ranges deliberately overlap. A peak in an overlap zone matches multiple groups — all possibilities are reported.

## Multi-peak combination rules

Single peaks are ambiguous. Combinations are diagnostic:

| Combination | Conclusion |
|-------------|-----------|
| Broad 3200-3500 + 1710 + 1200 | **Carboxylic acid** (-COOH) |
| 1735 + 1200 (no broad OH) | **Ester** (-COOR) |
| Broad 3300 + 1050 (no C=O) | **Alcohol** (-OH) |
| 3350 + 1660 + 1550 | **Amide** (-CONH-) — amide I + amide II |
| 2220 (sharp) | **Nitrile** (-C≡N) |
| 2700+2850 (two weak) + 1720 | **Aldehyde** (-CHO) |
| >3000 + 1600 + 800-900 | **Aromatic ring** present |
| No peaks >3000 | Likely **no aromatic, no vinyl, no OH/NH** |

## Intensity interpretation
- **Strong C=O** (~1720): almost always visible if carbonyl present
- **Weak/absent C≡C**: symmetric alkynes may not show IR absorption
- **Broad OH vs sharp NH**: breadth indicates hydrogen bonding

## QM9sp computational data caveat
The QM9sp dataset uses DFT-computed IR spectra. Key differences from experimental:
- **Frequencies are systematically higher** by ~50-150 cm⁻¹ (no anharmonic correction)
- **sp2/sp3 C-H cannot be distinguished**: computed sp3 C-H overlaps with sp2 range. Treat 2850-3200 cm⁻¹ as generic "C-H stretch" without sp2/sp3 assignment
- Multi-peak combination rules that depend on sp2 C-H detection (e.g., "sp2 C-H → aromatic") are unreliable for QM9sp
- Use aromatic ring C=C stretch (~1550-1600) instead to detect aromaticity
