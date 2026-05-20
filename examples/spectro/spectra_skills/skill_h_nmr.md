# 1H NMR Spectroscopy Skill

## What it measures
1H NMR measures the magnetic environments of hydrogen atoms in a molecule. Each chemically distinct hydrogen produces a signal at a characteristic chemical shift (ppm), with multiplicity (splitting pattern) from neighboring hydrogens and integration proportional to the number of equivalent H atoms.

## Key observables
- **Chemical shift (delta, ppm)**: Electronic environment of the H atom
- **Multiplicity (category)**: Number of neighboring H atoms (n+1 rule)
  - s (singlet): 0 neighbors
  - d (doublet): 1 neighbor
  - t (triplet): 2 neighbors
  - q (quartet): 3 neighbors
  - m (multiplet): complex coupling
  - dd, dt, td, etc.: multiple distinct couplings
- **Integration (nH)**: Relative number of equivalent H atoms
- **J-coupling (Hz)**: Bond distance and geometry between coupled H atoms

## Chemical shift → structural environment (overlapping ranges)

| Range (ppm) | Environment | Typical structures |
|-------------|-------------|-------------------|
| 0.0-0.5 | TMS/M-H | Cyclopropane rings, TMS reference, metal hydride |
| 0.5-1.2 | R-CH3 | Terminal methyl groups (-CH2-**CH3**) |
| 0.8-1.5 | R-CH2-R | Aliphatic methylene chains |
| 1.3-2.2 | R3CH/=C-CH | CH next to C=C or branching point, allylic |
| 1.8-2.5 | C=O-CH/C#C-H | -CO-**CH**-, C≡C-**H** (alpha to carbonyl, alkynyl) |
| 2.3-3.2 | N-CH/S-CH | Amines, thioethers |
| 2.8-4.0 | O-CH | Alcohols, ethers, esters (oxygen side) |
| 3.8-4.7 | O-CH/N-CH | Deshielded oxygen/nitrogen methylene |
| 4.3-5.2 | =CH2/O-CH-O | Terminal alkene, acetals |
| 4.8-5.5 | =CH- | Internal alkene (vinyl) |
| 5.3-6.8 | =CH-(conj) | Conjugated vinyl, enol, heteroaromatic |
| 6.0-7.5 | Ar-H | Benzene, electron-rich aromatics |
| 7.3-8.5 | Ar-H(EWG) | Aromatic with -NO2, -C=O, -CN adjacent |
| 8.3-9.2 | Ar-H/HetAr | Pyridine, pyrimidine N-adjacent H |
| 8.8-10.0 | CHO | Aldehyde -CH=O |
| 9.5-13.0 | COOH/OH | -COOH, chelated phenol, enol OH |
| 12.5-16.0 | enol-OH | Strongly chelated enol, beta-diketone |

> Note: Ranges deliberately overlap. A peak in an overlap zone matches multiple groups — all possibilities are reported.

## J-coupling interpretation

| J value (Hz) | Relationship | Structural meaning |
|--------------|-------------|-------------------|
| 0.5-3 | Long-range / meta | W-coupling, 4-5 bond |
| 6-8 | Vicinal (3-bond) | Typical alkyl H-C-C-H (delta < 5 ppm) |
| 6-10 | Ortho aromatic | Adjacent aromatic H (delta 6.5-9 ppm) |
| 6-12 | Cis alkene | H-C=C-H (Z) |
| 12-18 | Trans alkene | H-C=C-H (E) |

## Multiplicity reasoning
- Singlet (s) + 3H at 3.5-4.2 ppm → OCH3 or NCH3 (methoxy or N-methyl)
- Triplet (t) + 3H at 0.8-1.5 ppm → CH3 next to CH2 (ethyl group)
- Quartet (q) + 2H at 3.5-4.5 ppm → OCH2 or NCH2 adjacent to CH3
- Singlet (s) + 3H at 1.8-2.3 ppm → COCH3 (acetyl) or SCH3
- Singlet (s) + ≥9H at 1.0-2.0 ppm → tert-butyl C(CH3)3
- Singlet (s) + 1H at 9.5-10.5 ppm → aldehyde CHO or deshielded NH/ArH
- Doublet (d) + large J (15-17 Hz) → trans alkene
- Doublet of doublets (dd) in aromatic region → 1,2,4-substituted benzene

## Degree of unsaturation clues
- Peaks only below 5 ppm → likely saturated (no rings/double bonds unless heteroatoms)
- Peaks in 6.5-8.5 ppm → aromatic ring present (each ring = 4 degrees)
- Peak at 9-10 ppm → aldehyde (1 degree for C=O)
