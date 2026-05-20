# UV-Vis Spectroscopy Skill

## What it measures
UV-Vis spectroscopy measures electronic transitions — electrons jumping between molecular orbitals when absorbing ultraviolet or visible light. It identifies chromophores (light-absorbing groups) and the extent of conjugation.

## Key observables
- **Absorption energy (eV)** or wavelength (nm): Type of electronic transition. Conversion: λ(nm) = 1240 / E(eV)
- **Intensity**: Related to the probability of the transition (extinction coefficient)

## Electronic transitions (high to low energy)

| Energy (eV) | λ (nm) | Transition | What it means |
|-------------|--------|-----------|--------------|
| 14.5-25 | <85 | core electron | Core electron transitions |
| 10.5-15.0 | 80-118 | sigma->sigma* | Saturated C-C, C-H bonds. All organics absorb here. |
| 7.8-11.0 | 113-159 | n->sigma*/weak pi | Heteroatom lone pairs (O, N, S), weak pi |
| 6.3-8.2 | 151-197 | isolated C=C/C=O/lone pair | Isolated C=C or C=O pi→pi* |
| 5.3-6.7 | 185-234 | conj diene/heteroAr | Conjugated diene, heteroaromatic |
| 4.3-5.7 | 218-288 | Ar pi->pi* | Benzene ring (~254 nm), naphthalene |
| 3.3-4.7 | 264-376 | C=O n->pi*/extended Ar | C=O lone pair transition, extended aromatic |
| 2.3-3.7 | 335-539 | polyene/azo/large Ar | Polyenes, azo compounds, large aromatics |
| 1.5-2.7 | 459-827 | extended conj/visible | Highly conjugated systems, dyes |

> Note: Ranges deliberately overlap. A peak in an overlap zone matches multiple transitions — all possibilities are reported.

## Chromophore identification

| Chromophore | Typical λmax | Typical E(eV) |
|------------|-------------|---------------|
| Isolated C=C | ~170 nm | ~7.3 eV |
| Conjugated diene | ~217 nm | ~5.7 eV |
| Benzene | ~254 nm | ~4.9 eV |
| Naphthalene | ~275, 310 nm | ~4.5, 4.0 eV |
| C=O (ketone, n→π*) | ~280 nm | ~4.4 eV |
| C=O (aldehyde, n→π*) | ~290 nm | ~4.3 eV |
| Nitro (-NO2) | ~270 nm | ~4.6 eV |
| Azo (-N=N-) | ~350 nm | ~3.5 eV |
| Extended polyene | 300-500 nm | 2.5-4.1 eV |

## Structural reasoning

### Conjugation length
- More conjugation → lower energy (red shift)
- Each additional conjugated C=C shifts λmax by ~30 nm
- Benzene (254 nm) → naphthalene (310 nm) → anthracene (375 nm)

### Substituent effects
- Electron-donating groups (-OH, -NH2, -OCH3) → red shift (lower energy)
- Electron-withdrawing groups (-NO2, -CN, -COOH) → red shift when conjugated with donor

### Absence of absorption
- No absorption above 200 nm → no aromatic ring, no conjugation, no heteroatom lone pairs
- Only σ→σ* → saturated hydrocarbon

## QM9sp data notes
- QM9sp uses computed (DFT) transitions, energy in eV
- Small molecules (≤9 heavy atoms): mostly σ→σ* and σ→π*
- Transitions are vertical (Franck-Condon), may differ from solution-phase experiment
