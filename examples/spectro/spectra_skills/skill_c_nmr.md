# 13C NMR Spectroscopy Skill

## What it measures
13C NMR measures the magnetic environments of carbon atoms. Each chemically distinct carbon produces one signal. Unlike 1H NMR, peak count directly gives the number of unique carbon environments (molecular symmetry reduces peak count).

## Key observables
- **Chemical shift (delta, ppm)**: Carbon electronic environment (0-220 ppm range)
- **Peak count**: Number of chemically distinct carbons
- **Integral/intensity**: Roughly proportional to number of equivalent carbons (less reliable than 1H)

## Chemical shift → carbon type (overlapping ranges)

| Range (ppm) | Carbon type | Typical structures |
|-------------|------------|-------------------|
| -15 to -5 | Shielded C | Organometallic, strained rings, some cyclopropanes |
| -5 to 5 | TMS/Si-C | Reference, organosilicon |
| 5-28 | CH3(alkyl) | Terminal methyls, C-CH3 |
| 22-50 | CH2/CH(alkyl) | Aliphatic chains, cycloalkanes |
| 48-65 | C-N/C-O | Amines (N-CH), methoxy (O-CH3) |
| 58-92 | C-O(alc/eth) | Alcohols, ethers, sugars, ester O-side |
| 88-105 | O-C-O(acetal) | Acetals, ketals, anomeric carbons |
| 95-125 | =CH/Ar-C(e-rich) | Alkene carbons, heteroaromatic, electron-rich aromatic |
| 115-145 | Ar-C/=C | Unsubstituted aromatic C-H, vinyl |
| 138-165 | Ar-C(subst) | Substituted aromatic (C-N, C-O, C-C) |
| 155-178 | C=O/Ar-C=N | Ester, amide, acid carbonyl, aromatic C=N (pyridine) |
| 172-198 | C=O(acid/anhy) | Carboxylic acid, anhydride |
| 192-220 | C=O(ald/ket) | Aldehyde -CHO, ketone R-CO-R |

> Note: Ranges deliberately overlap. A peak in an overlap zone matches multiple carbon types — all possibilities are reported.

## Structural reasoning from 13C

### Peak counting
- Benzene: 1 peak (all 6 C equivalent) → high symmetry
- Monosubstituted benzene: 4 peaks (C1, C2/C6, C3/C5, C4) → mirror symmetry
- 1,4-disubstituted benzene: 3 peaks
- n unique peaks ≤ total carbons (equality means no symmetry)

### Carbon skeleton inference
- Peaks only in 0-50 ppm → pure aliphatic (alkane)
- Peaks in 120-140 ppm → aromatic carbons present
- Count of aromatic peaks: 6 unique → monosubstituted benzene or asymmetric ring
- Peak at 170 ppm + peak at 60 ppm → ester (C=O + O-CH2)
- Peak at 200 ppm → ketone or aldehyde

### Distinguishing similar structures
- Ester vs acid: both show ~170 ppm, but acid has broad OH in 1H
- Ketone vs aldehyde: ketone ~200-210, aldehyde ~190-205 + 1H signal at 9-10 ppm
- Aromatic C-OH (phenol) ~155 ppm vs aromatic C-H ~128 ppm
