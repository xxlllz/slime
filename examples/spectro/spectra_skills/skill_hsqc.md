# HSQC (Heteronuclear Single Quantum Coherence) NMR Skill

## What it measures
HSQC is a 2D NMR experiment that correlates each 1H signal with the directly bonded 13C. Each cross-peak represents a C-H bond. Quaternary carbons (no H) are invisible.

## Key observables
- **1H chemical shift (ppm)**: Hydrogen environment
- **13C chemical shift (ppm)**: Carbon environment
- **nH**: Number of H on that carbon (1=CH, 2=CH2, 3=CH3)

## Combined (1H, 13C) → precise assignment

The power of HSQC is that combining both dimensions resolves ambiguities:

| 1H (ppm) | 13C (ppm) | nH | Assignment |
|-----------|-----------|-----|-----------|
| 0.0-1.0 | -5-25 | 3 | R-CH3/cyPr (alkyl CH3 or cyclopropyl) |
| 1.0-2.0 | 0-25 | 3 | R-CH3 (methyl) |
| 1.0-2.0 | 25-50 | 2 | R-CH2-R (alkyl CH2) |
| 0.5-1.8 | 25-50 | 2 | R-CH2-R (alkyl CH2) |
| 1.8-3.0 | 0-25 | 3 | =C-CH3/S-CH3 (allyl or thioether methyl) |
| 2.0-3.0 | 20-50 | 2-3 | C=O-CH/allyl (alpha to carbonyl) |
| 2.0-3.5 | 25-65 | 2-3 | N-CH/S-CH (bonded to N or S) |
| 3.0-4.5 | 20-50 | 2 | N-CH2/N-CH (nitrogen methylene) |
| 3.0-4.5 | 50-90 | 3 | O-CH(sp3) (methoxy, alcohol, ether) |
| 4.0-5.0 | 55-80 | 2 | O-CH2(ester) |
| 4.5-5.5 | 30-60 | 1 | N-CH/act-CH (activated CH) |
| 4.5-6.0 | 85-110 | 1 | O-CH-O (anomeric, acetal) |
| 5.0-6.5 | 60-85 | 1 | O-CH(allyl) |
| 5.0-7.0 | 95-140 | 1 | =CH(vinyl) (olefinic) |
| 6.0-7.0 | 80-120 | 1 | Ar-H/HetAr (aromatic/heteroaromatic) |
| 6.5-8.0 | 100-145 | 1 | Ar-H (aromatic) |
| 7.5-9.0 | 100-140 | 1 | Ar-H(EWG) (electron-withdrawing group adjacent) |
| 7.0-9.0 | 140-165 | 1 | Ar-H(subst) (deshielded, C-N/C-O adjacent) |
| 8.0-9.5 | 115-165 | 1 | Ar-H/HetAr(ds) (highly deshielded) |
| 9.0-10.5 | 175-220 | 1 | CHO (aldehyde) |
| 8.0-8.5 | 160-175 | 1 | HCO(formate) (formate/formamide) |
| 2.0-3.5 | 60-90 | 1 | C#C-CH/epoxy (propargylic or epoxide) |
| 3.0-3.5 | 0-25 | 3 | cyPr/N-CH3 (cyclopropyl or N-methyl) |
| 4.5-5.0 | 75-90 | 1 | O-CH(sugar) (sugar-type) |
| 5.0-6.0 | 40-60 | 1 | =CH(strained) (strained olefinic) |
| 6.0-7.5 | 55-100 | 1 | HetAr/=CH(ds) (heteroaromatic, deshielded vinyl) |
| 7.0-8.0 | 90-100 | 1 | HetAr(5-ring) (five-membered heteroaromatic) |

> Note: Ranges deliberately overlap. A correlation in an overlap zone matches multiple groups — all possibilities are reported.

## CH multiplicity from nH

| nH | Carbon type | What it tells you |
|----|------------|-------------------|
| 3 | CH3 | Methyl group. If at ~3.8/55 ppm → OCH3. If at ~0.9/14 ppm → terminal CH3. |
| 2 | CH2 | Methylene. Count these to estimate chain length. |
| 1 | CH | Methine or aromatic. If in aromatic region → aromatic H count. |
| 0 | Quaternary C | Not visible in HSQC (no cross-peak). |

## Structural reasoning

### Aromatic ring detection
- Cross-peaks at (6.5-8.5, 110-145) with nH=1 → aromatic CH
- Count of aromatic CH correlations → substitution pattern
  - 5 aromatic CH → monosubstituted benzene
  - 4 aromatic CH → disubstituted benzene
  - 2-3 aromatic CH → tri/tetrasubstituted

### Functional group counting
- Total H from HSQC = sum(nH for all cross-peaks)
- Missing H vs molecular formula → NH, OH (exchangeable, not in HSQC)
- No cross-peak at certain 13C → quaternary carbon (C=O, C-quaternary)

### OCH3 fingerprint
- (3.8-4.0, 53-58, nH=3) is almost always OCH3 (methoxy)
- Very diagnostic: if you see this, molecule has -OCH3
