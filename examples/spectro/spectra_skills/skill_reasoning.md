# Structure Elucidation Reasoning Skill

This skill covers the reasoning process AFTER extracting functional groups from spectra. It bridges the gap between "what groups are present" and "what is the molecule."

---

## 1. Molecular Formula & Degree of Unsaturation

### RDBE calculation

RDBE (Ring and Double Bond Equivalence) = (2C + 2 + N − H − X) / 2

where C = carbons, H = hydrogens, N = nitrogens, X = halogens (F, Cl, Br, I). Oxygen and sulfur do NOT contribute.

### RDBE interpretation table

| RDBE | Structural meaning | Common examples |
|------|--------------------|-----------------|
| 0 | Fully saturated, no rings | Alkanes, alcohols, ethers, amines |
| 1 | One ring OR one C=C OR one C=O | Cyclopentane, propene, acetone |
| 2 | Two unsaturations in any combination | Cyclohexanone (ring+C=O), 1,3-butadiene |
| 3 | Three unsaturations | Cyclohexenone (ring+C=C+C=O), C≡C+ring |
| 4 | Benzene ring (3 C=C + 1 ring) | Benzene, toluene, phenol |
| 5 | Benzene + one C=O or C=C | Benzaldehyde, acetophenone, styrene |
| 6 | Benzene + two extra unsaturations | Benzoic acid methyl ester, cinnamaldehyde |
| 7 | Naphthalene or benzene+3 | Naphthalene (5 C=C + 2 rings), indole |
| 8 | Two benzene rings | Biphenyl, diphenylmethane |
| ≥10 | Large polycyclic/highly conjugated | Anthracene (10), steroid skeleton (varies) |

### Key RDBE rules
- RDBE < 0 → chemically impossible formula, reject
- RDBE is always an integer for valid formulas with even-electron species
- Half-integer RDBE → radical species (rare in stable molecules)
- Each benzene ring = 4 RDBE; each C=O = 1; each C=C = 1; each C≡C = 2; each C≡N = 2
- RDBE must be fully accounted for: if RDBE = 5 and one benzene is confirmed, exactly 1 additional unsaturation remains

### Heteroatom budget

The molecular formula constrains possible functional groups:

| Atom | Budget rule | Example |
|------|------------|---------|
| O = 1 | One of: -OH, -OR (ether), C=O, epoxide | C6H12O → cyclohexanone OR cyclohexanol OR tetrahydropyran |
| O = 2 | Two of above, OR: ester (-COOR), carboxylic acid (-COOH), anhydride | C3H6O2 → methyl formate, glycolaldehyde |
| O = 3 | Ester + OH, or carbonate, or nitro-related | Often ester + alcohol or multiple ethers |
| N = 1 | Amine (-NHx), amide (-CONH-), nitrile (-C≡N), nitro (-NO2 uses N+2O), imine (=NH) | Check RDBE: nitrile adds 2, amide adds 1 |
| N = 2 | Diamine, azo (-N=N-), hydrazine, two separate N groups | Azo adds 2 RDBE |
| S = 1 | Thiol (-SH), thioether (-S-), sulfoxide (-SO-), sulfone (-SO2-) | S does not change RDBE |

---

## 2. Skeleton Determination

### Decision tree: aromatic vs. aliphatic

```
Start with RDBE and aromatic evidence (1H 6-9 ppm, 13C 110-160 ppm, UV >240 nm)

RDBE ≥ 4 AND aromatic signals present?
├── YES → Aromatic skeleton
│   ├── Count aromatic H (from 1H NMR):
│   │   ├── 5 ArH → monosubstituted benzene → subtract C6H5 from formula
│   │   ├── 4 ArH → disubstituted benzene
│   │   │   ├── Check J-coupling pattern for ortho/meta/para
│   │   │   └── Subtract C6H4 from formula
│   │   ├── 3 ArH → trisubstituted benzene → subtract C6H3
│   │   ├── 2 ArH → tetrasubstituted benzene OR five-membered heteroaromatic
│   │   │   ├── If N in formula → pyrrole, imidazole, pyrazole, thiazole
│   │   │   ├── If O in formula → furan
│   │   │   └── If S in formula → thiophene
│   │   ├── 1 ArH → pentasubstituted benzene OR highly substituted heteroaromatic
│   │   └── 0 ArH + aromatic 13C → fully substituted aromatic ring
│   ├── Remaining RDBE after aromatic = total RDBE − 4 (per benzene ring)
│   └── Remaining atoms = formula − aromatic fragment → analyze as substituent
│
├── RDBE ≥ 1 AND no aromatic signals?
│   ├── RDBE = 1 → one ring OR one C=C OR one C=O
│   │   ├── C=O signal (13C >160 ppm, IR 1650-1800 cm⁻¹) → carbonyl
│   │   ├── Vinyl signal (1H 4.5-6.5 ppm, 13C 100-140 ppm) → alkene
│   │   └── Neither → saturated ring (cyclopentane, cyclohexane, etc.)
│   ├── RDBE = 2 → two of above in any combination
│   └── RDBE ≥ 3 (no aromatic) → multiple rings/double bonds, or C≡C/C≡N
│
└── RDBE = 0 → fully saturated acyclic
    └── Only sp3 carbons, possible heteroatom functional groups (OH, OR, NH2, SH)
```

### Aromatic substitution pattern from 1H coupling

| ArH count | J-coupling pattern | Substitution |
|-----------|-------------------|-------------|
| 5H | Complex multiplet (monosubst.) | C6H5-R |
| 4H (ortho) | Two pairs of doublets, J = 7-8 Hz | 1,2-disubstituted |
| 4H (meta) | t + d + s + d pattern | 1,3-disubstituted |
| 4H (para) | Two 2H doublets, J = 8-9 Hz (AA'BB') | 1,4-disubstituted |
| 3H (1,2,4-tri) | dd + d + d | 1,2,4-trisubstituted |
| 3H (1,3,5-tri) | Three singlets (equivalent: one singlet) | 1,3,5-trisubstituted |
| 2H (1,2,3,5-tetra) | Two singlets or two doublets | Tetrasubstituted |

### Aromatic substitution from 13C peak count

| Unique aromatic 13C peaks | Substitution pattern |
|---------------------------|---------------------|
| 1 peak | Fully symmetric: benzene, or para-disubstituted (identical groups) |
| 3 peaks | Para-disubstituted (different groups): C1, C2/C6, C3/C5, C4 reduces to 3 if the groups differ |
| 4 peaks | Monosubstituted benzene (C1, C2/C6, C3/C5, C4) |
| 6 peaks | No symmetry: ortho/meta-disubstituted with different groups |

### Chain length estimation

- Count of CH2 groups (from HSQC or 13C in 22-50 ppm) estimates chain length
- n CH2 in a row → (CH2)n chain
- Total aliphatic H count / 2 ≈ number of CH2 equivalents (rough estimate)
- If total H is large (>20) and mostly in 0.5-2.0 ppm → long aliphatic chain (fatty acid, lipid)

---

## 3. Substructure Recognition & Assembly

### Common fragment signatures (multi-spectral)

#### Alkyl fragments

| Fragment | 1H NMR | 13C NMR | Other evidence |
|----------|--------|---------|----------------|
| -CH3 (terminal methyl) | 0.8-1.0 ppm, t (3H) | 10-22 ppm | — |
| -CH2- (methylene) | 1.2-1.4 ppm, m (2H) | 22-35 ppm | — |
| -CH(CH3)2 (isopropyl) | 0.8-1.0 ppm, d (6H) + 1.5-2.0 ppm, sept (1H) | ~20 + ~28 ppm | Characteristic 6H doublet |
| -C(CH3)3 (tert-butyl) | 1.0-1.5 ppm, s (9H) | ~27 + ~35 ppm (quat) | 9H singlet is diagnostic |
| -CH2CH3 (ethyl) | 1.0-1.3 ppm, t (3H) + 2.0-4.5 ppm, q (2H) | ~14 + variable | Triplet-quartet pattern |

#### Oxygen-containing fragments

| Fragment | 1H NMR | 13C NMR | IR | Key diagnostic |
|----------|--------|---------|-----|---------------|
| -OCH3 (methoxy) | 3.3-3.9 ppm, s (3H) | 52-58 ppm | 1000-1100 cm⁻¹ (C-O) | 3H singlet in O-CH region |
| -OCH2CH3 (ethoxy) | 3.4-4.2 ppm, q (2H) + 1.1-1.3 ppm, t (3H) | ~15 + ~60-65 ppm | 1000-1100 cm⁻¹ | Quartet + triplet across two regions |
| -COCH3 (acetyl) | 2.0-2.2 ppm, s (3H) | ~20-30 + ~170-210 ppm | 1700-1750 cm⁻¹ (C=O) | 3H singlet at ~2.1 + carbonyl |
| -CHO (aldehyde) | 9.4-10.0 ppm, s (1H) | 190-205 ppm | 2700+2850+1720 cm⁻¹ | Highly deshielded 1H singlet |
| -COOH (carboxylic acid) | >10 ppm, broad (1H) | 170-180 ppm | Broad 2500-3300+1700-1720 cm⁻¹ | Very broad OH + acid C=O |
| -COOR (ester) | — (no unique 1H for C=O) | 170-175 ppm (C=O) | 1720-1750+1150-1300 cm⁻¹ | IR ester doublet + 13C ~170 |
| -OH (alcohol) | 1-5 ppm, broad (1H) | — | Broad 3200-3600 cm⁻¹ | Broad OH in IR, variable 1H |
| -COOCH3 (methyl ester) | 3.6-3.8 ppm, s (3H) | ~52 + ~170-175 ppm | 1735+1200 cm⁻¹ | OCH3 singlet + ester 13C/IR |
| -COOCH2CH3 (ethyl ester) | 4.1-4.2 ppm, q (2H) + 1.2-1.3 ppm, t (3H) | ~14 + ~60 + ~170 ppm | 1735+1200 cm⁻¹ | Ethyl pattern + ester C=O |

#### Nitrogen-containing fragments

| Fragment | 1H NMR | 13C NMR | IR | Key diagnostic |
|----------|--------|---------|-----|---------------|
| -NH2 (primary amine) | 1-3 ppm, broad (2H) | C-N: 40-55 ppm | 3300-3500 cm⁻¹ (two peaks) | Two NH stretches in IR |
| -NHR (secondary amine) | 1-3 ppm, broad (1H) | C-N: 40-55 ppm | 3300-3500 cm⁻¹ (one peak) | Single NH stretch |
| -NCH3 (N-methyl) | 2.2-2.8 ppm, s (3H) | 30-42 ppm | — | Singlet in N-CH region |
| -CONH2 (primary amide) | 6-8 ppm, broad (2H) | ~170 ppm | 1630-1680+1510-1570 cm⁻¹ | Amide I + amide II bands |
| -CONHR (secondary amide) | 6-8 ppm, broad (1H) | ~170 ppm | 1630-1680+1510-1570 cm⁻¹ | Single NH + amide bands |
| -C≡N (nitrile) | — (no H) | 115-120 ppm | 2200-2260 cm⁻¹ (sharp) | Sharp IR absorption |
| -NO2 (nitro) | — (no H) | — | 1350-1380+1510-1560 cm⁻¹ | Two strong IR bands |

#### Sulfur-containing fragments

| Fragment | 1H NMR | 13C NMR | Other evidence |
|----------|--------|---------|----------------|
| -SCH3 (thiomethyl) | 2.0-2.5 ppm, s (3H) | 15-20 ppm | Raman: strong C-S ~700 cm⁻¹ |
| -SO2- (sulfone) | Deshields adjacent CH by ~0.5 ppm | — | IR: 1120-1160+1290-1350 cm⁻¹ |
| -SH (thiol) | 1-2 ppm, s (1H, variable) | — | Raman: strong S-H ~2570 cm⁻¹ |
| -S-S- (disulfide) | — | — | Raman: very strong ~500 cm⁻¹ |

### Fragment assembly rules

After identifying individual fragments, assemble them into a molecular structure by:

1. **Start with the largest rigid fragment** (aromatic ring or longest chain)
2. **Attach heteroatom-bearing groups** to account for O, N, S atoms
3. **Fill remaining carbons and hydrogens** with alkyl chains
4. **Check atom count**: sum of all fragment atoms must equal molecular formula
5. **Check RDBE**: assembled structure's RDBE must match calculated RDBE

### Assembly heuristics

| If you see... | Likely combination | Resulting substructure |
|--------------|-------------------|----------------------|
| OCH3 singlet + Ar-H | Methoxy on aromatic ring | Ar-OCH3 (anisole-type) |
| Ethyl pattern (q+t) + C=O at ~170 ppm | Ethyl ester | R-COOCH2CH3 |
| 9H singlet + C=O + NH | Boc protecting group | (CH3)3C-OC(=O)-NHR |
| 3H singlet ~2.1 ppm + ArH | Methyl ketone on ring | Ar-COCH3 (acetophenone-type) |
| 3H singlet ~3.8 ppm + 13C ~55 ppm + ArH | Methoxy on aromatic | Ar-OCH3 |
| Two 2H doublets (para pattern) + OCH3 + C=O | Para-substituted ring with MeO and carbonyl | 4-MeO-C6H4-COR |
| Triplet-quartet + OH (broad, IR 3300) | Ethanol fragment | R-CH(OH)-CH2CH3 or similar |
| Aldehyde 1H (9.7 ppm) + ArH | Aromatic aldehyde | Ar-CHO (benzaldehyde-type) |
| NH broad + C=O ~170 ppm + no OH | Amide | R-CONHR' |
| Two 13C at ~170 ppm | Two carbonyl groups | Diester, diacid, keto-acid, anhydride |
| ArH + 13C >140 ppm (substituted) + no N/O | Alkyl substituent on ring | Ar-R (toluene/xylene-type) |

---

## 4. Exclusion Rules

Absence of a signal is often more informative than its presence. If a spectral feature is expected but NOT observed, the corresponding structural element can be confidently excluded.

### From 1H NMR

| Absent feature | Exclude |
|---------------|---------|
| No peaks in 6.0-9.0 ppm | No aromatic ring, no vinyl (unless fully substituted — rare for MW < 300) |
| No peaks in 9.0-10.5 ppm | No aldehyde (-CHO) |
| No peaks above 10 ppm | No carboxylic acid (-COOH), no strongly chelated enol-OH |
| No peaks in 3.0-5.0 ppm | No C-O bonds (no alcohol, ether, ester O-side), no C-N (amine) |
| No peaks in 0-2.5 ppm | No simple alkyl groups (no CH3, CH2 chains) |
| All peaks are singlets | No H-H vicinal coupling → no adjacent CH-CH fragments, or high symmetry |
| No exchangeable H (D2O shake) | No OH, NH, SH |
| Total integrated H << expected from formula | Some H are exchangeable (OH, NH) or molecule is partially deuterated |

### From 13C NMR

| Absent feature | Exclude |
|---------------|---------|
| No peaks in 110-160 ppm | No aromatic C, no vinyl C |
| No peaks in 160-220 ppm | No carbonyl (no ketone, aldehyde, ester, acid, amide) |
| No peaks in 50-90 ppm | No C-O sp3 (no alcohol, ether, ester O-alkyl side) |
| No peaks in 0-50 ppm | No saturated aliphatic C (implies fully unsaturated/aromatic — uncommon) |
| Fewer 13C peaks than formula suggests | Molecular symmetry exists → structure has mirror plane, rotation axis, or equivalent groups |

### From IR spectroscopy

| Absent feature | Exclude |
|---------------|---------|
| No broad band 3200-3600 cm⁻¹ | No free OH, no NH |
| No broad band 2500-3300 cm⁻¹ | No carboxylic acid (-COOH) |
| No band 1650-1800 cm⁻¹ | No C=O (no ketone, aldehyde, ester, acid, amide) |
| No band 2100-2300 cm⁻¹ | No C≡C, no C≡N, no isocyanate, no azide |
| No band >3000 cm⁻¹ (experimental) | No sp2 C-H, no aromatic C-H, no vinyl C-H |
| No band 1500-1600 cm⁻¹ | Possibly no aromatic ring (but not definitive alone) |
| No band 1350+1550 cm⁻¹ pair | No nitro group (-NO2) |

### From Raman spectroscopy

| Absent feature | Exclude |
|---------------|---------|
| No strong band ~1000 cm⁻¹ | No monosubstituted benzene ring breathing |
| No strong band 1580-1620 cm⁻¹ | No aromatic ring, no C=C |
| No strong band ~2100 cm⁻¹ | No C≡C (Raman is more sensitive than IR for symmetric alkynes) |
| No strong band ~500 cm⁻¹ | No S-S disulfide bond |
| No bands ~700 cm⁻¹ | No C-S bond |

### From UV-Vis

| Absent feature | Exclude |
|---------------|---------|
| No absorption >200 nm | No aromatic, no conjugation, no chromophore |
| No absorption >250 nm | No benzene ring, no extended conjugation |
| No absorption >300 nm | No naphthalene, no azo, no extended polyene, no n→π* C=O |
| Only weak absorption 250-300 nm | Possibly isolated C=O (n→π*) or benzene — not extended conjugation |

### From MS/MS

| Absent feature | Exclude |
|---------------|---------|
| No N in molecular formula | All nitrogen-containing structures (amine, amide, nitrile, nitro, N-heterocycles) |
| No S in molecular formula | All sulfur-containing structures (thiol, thioether, sulfone, thiophene) |
| No halogen isotope pattern | No Cl, Br (F and I have no isotope pattern) |
| Even molecular weight + no N | Confirms no odd-number-of-N species |
| Odd molecular weight | Must contain odd number of nitrogen atoms (nitrogen rule) |
| No loss of 18 (H2O) | No easily dehydratable -OH (though not all OH gives loss of 18) |
| No loss of 28 (CO) | No ketone/quinone prone to CO loss |
| No loss of 44 (CO2) | No free carboxylic acid |

### Exclusion confidence levels

Not all exclusions are equally reliable:

| Confidence | Exclusion type | Example |
|-----------|---------------|---------|
| **High** | Formula-based | No N in formula → no N-containing groups |
| **High** | Strong diagnostic absence | No IR 1650-1800 → no C=O |
| **Medium** | Region-based NMR | No 1H at 6-9 ppm → probably no aromatic (could be fully substituted) |
| **Medium** | Multi-signal absence | No ArH + no aromatic 13C + no UV >250 → very likely no aromatic |
| **Low** | Single weak signal | No Raman at 1600 → might still have aromatic (weak signal, poor S/N) |

**Rule of thumb**: Exclusion from TWO independent spectra (e.g., no ArH in 1H NMR AND no aromatic 13C in 13C NMR) is much more reliable than from one.

---

## 5. Constraint Propagation

Constraint propagation is the systematic process of narrowing candidate structures by combining evidence from all available sources. Work from the MOST constrained (fewest possibilities) to LEAST constrained.

### Priority order of constraints

1. **Molecular formula** (from MS) — most powerful single constraint
2. **RDBE** — immediately limits ring/double bond count
3. **Exclusion rules** — eliminate entire classes of structures
4. **Identified functional groups** — must appear in final structure
5. **Atom accounting** — remaining atoms after subtracting identified groups
6. **Connectivity** — how fragments connect (from coupling, HSQC, neutral losses)

### Step-by-step constraint propagation template

```
Step 1: MOLECULAR FORMULA
  Input: precursor m/z → neutral mass → molecular formula CxHyNnOoSs
  Constraint: fixes total atom count

Step 2: RDBE CALCULATION
  RDBE = (2C + 2 + N − H − X) / 2
  Constraint: total unsaturation budget

Step 3: AROMATIC SYSTEM IDENTIFICATION
  Evidence: 1H (6-9 ppm), 13C (110-160 ppm), UV (>250 nm), Raman (~1000, 1600 cm⁻¹)
  If aromatic:
    Count ArH → substitution pattern
    Subtract aromatic atoms from formula: remaining = CxHyNnOo − C6H(5−n)
    Subtract aromatic RDBE: remaining RDBE = total RDBE − 4
  If not aromatic:
    Full RDBE available for rings/double bonds/triple bonds

Step 4: HETEROATOM ACCOUNTING
  For each O: assign to one of {OH, OR, C=O, epoxide, ...}
  For each N: assign to one of {NH2, NHR, NR2, C=N, C≡N, NO2, ...}
  For each S: assign to one of {SH, SR, SO, SO2, ...}
  Constraint: total O, N, S must be accounted for

Step 5: FUNCTIONAL GROUP MATCHING
  Check detected groups (from tool output) against heteroatom budget:
    - If O=2 and detected ester → uses both O → no remaining O for other groups
    - If O=2 and detected OH → one O used → one O remains for C=O or ether
  Constraint: detected groups must be compatible with atom budget

Step 6: CARBON/HYDROGEN ACCOUNTING
  Remaining C after aromatic + functional groups → alkyl chain length
  Remaining H must match the alkyl chain structure
  Example: 3 remaining C + 7 remaining H → propyl group (-CH2CH2CH3)
  Constraint: sum of all fragment atoms = molecular formula

Step 7: CONNECTIVITY DETERMINATION
  From J-coupling: which H are neighbors
  From HSQC: which H is on which C
  From HMBC (if available): long-range C-H correlations
  From neutral losses: which fragments are connected
  Constraint: topology of connections
```

### Worked example

```
Given: 1H NMR with 5 ArH (7.2-7.4 ppm), 3H singlet at 3.8 ppm, molecular formula C8H10O (from MS)

Step 1: Formula C8H10O
Step 2: RDBE = (2×8 + 2 − 10) / 2 = 4
Step 3: 5 ArH → monosubstituted benzene (C6H5-)
         Remaining: C8H10O − C6H5 = C2H5O
         Remaining RDBE: 4 − 4 = 0 → no more unsaturation
Step 4: O = 1 → one of {OH, OR, C=O, epoxide}
         RDBE remaining = 0 → cannot be C=O (needs RDBE=1)
         → must be OH or ether (-O-)
Step 5: 3H singlet at 3.8 ppm → OCH3 (methoxy, uses C1H3O1)
         Remaining after OCH3: C2H5O − CH3O = CH2
         Wait — that leaves CH2 which needs connection.
         Reconsider: C6H5- + OCH3 = C7H8O → remaining from C8H10O = CH2
         Actually: C6H5-O-CH3 = C7H8O (anisole), remaining = CH2 → need one more CH2
         → This doesn't balance. Reassess:
         C6H5-CH2-OCH3? → C6H5CH2OCH3 = C8H10O ✓ (benzyl methyl ether)
         OR: C6H5-OCH2CH3? → C6H5OC2H5 = C8H10O ✓ (phenetole/ethoxybenzene)
Step 6: Both candidates satisfy C8H10O with RDBE=4
Step 7: Distinguish by multiplicity:
         If 3.8 ppm is singlet (3H) → not ethoxy (would be quartet+triplet)
         If 3H singlet → more consistent with benzyl methyl ether (PhCH2OCH3)
           Then expect 2H singlet for PhCH2 at ~4.4 ppm
         Check: is there a 2H singlet at ~4.4 ppm? If yes → PhCH2OCH3
```

---

## 6. Self-consistency Checks

Before reporting a final SMILES, verify these constraints:

### Mandatory checks

| Check | Method | Pass criterion |
|-------|--------|---------------|
| Atom count | Count atoms in proposed SMILES | Matches molecular formula exactly |
| RDBE match | Calculate RDBE from SMILES | Equals RDBE from molecular formula |
| H accounting | Sum of all 1H NMR integrals | Equals H count in proposed structure (± exchangeable H) |
| C accounting | Count of 13C peaks ≤ C in formula | Symmetry can reduce peak count but never increase it |
| Functional group presence | Each detected group appears in SMILES | All reported groups must map to a part of the structure |
| Functional group absence | Each excluded group is absent in SMILES | Structure must not contain excluded groups |
| Heteroatom accounting | O, N, S count in SMILES | Matches molecular formula |

### Cross-spectrum consistency

| If spectrum A says... | Then spectrum B should show... | If not → problem |
|----------------------|-------------------------------|------------------|
| 1H: ArH at 7 ppm | 13C: peaks in 110-145 ppm | Missing aromatic 13C → wrong ArH assignment |
| 1H: singlet 3H at 3.8 ppm | HSQC: cross-peak at (3.8, 55) ppm | Missing HSQC → maybe not OCH3 |
| IR: C=O at 1720 cm⁻¹ | 13C: peak in 160-220 ppm | Missing carbonyl 13C → false positive in IR |
| MS: loss of 18 (H2O) | 1H or IR: OH evidence | No OH evidence → might be artifact or different dehydration |
| UV: absorption at 254 nm | 1H: ArH in 6-9 ppm | No ArH → fully substituted aromatic (rare) or wrong UV assignment |
| 13C: peak at 55 ppm | 1H: singlet ~3.8 ppm (OCH3) | No 1H signal → quaternary C-O (not OCH3) |

### Common errors to catch

| Error | How to detect | Fix |
|-------|--------------|-----|
| RDBE mismatch | Calculated ≠ from formula | Recount rings and double bonds |
| Missing hydrogen | ΣnH from NMR < H in formula | Exchangeable H (OH, NH) not integrated, or missed a peak |
| Extra hydrogen | ΣnH from NMR > H in formula | Over-integration, overlapping peaks miscounted |
| Wrong symmetry | More 13C peaks than C in formula | Impurity peak, or formula is wrong |
| Impossible valence | Atom with too many bonds | Carbon must be 4, nitrogen 3 (or 5 in salts), oxygen 2 |

---

## 7. Common Structural Patterns

### Small molecules (≤9 heavy atoms, e.g., QM9sp dataset)

These molecules are constrained by size. Common frameworks:

| Framework | Formula range | Key spectral features |
|-----------|--------------|----------------------|
| Substituted cyclopropane | C3-C6 | 1H: 0.0-1.0 ppm (shielded), strained ring |
| Cyclopentane/cyclohexane derivatives | C5-C9 | 1H: mostly 1-2 ppm, possibly CH-O at 3-4 ppm |
| Furan/pyrrole/thiophene | C4-C8 + heteroatom | 1H: 6-7.5 ppm (2-3H), lower RDBE than benzene |
| Oxetane/oxirane/aziridine | C2-C6 + O/N | Strained ring, unusual chemical shifts |
| Small linear with functional groups | C1-C9 | Variable, depends on functional groups |

### Medium molecules (10-20 heavy atoms)

| Framework | Key spectral features |
|-----------|----------------------|
| Monosubstituted benzene + chain | 5 ArH + aliphatic chain signals |
| Disubstituted benzene + substituents | 4 ArH (pattern depends on ortho/meta/para) |
| Naphthalene derivatives | 6-7 ArH, UV ~275+310 nm, RDBE = 7 |
| Pyridine derivatives | ArH at 7-9 ppm (some shifted downfield vs benzene) |
| Indole derivatives | 4-5 ArH + NH, RDBE = 8, UV ~270+280 nm |
| Amino acid derivatives | NH + alpha-CH + COOH/COOR, side chain varies |
| Fatty acid fragments | Long CH2 chain (1.2-1.4 ppm), COOH/COOR terminus |

### Protecting groups (important in synthetic chemistry)

| Protecting group | Characteristic signals | Formula contribution |
|-----------------|----------------------|---------------------|
| Boc (-OC(=O)C(CH3)3) | 9H singlet ~1.4 ppm | C5H9O2, RDBE = 1 |
| Cbz (-OC(=O)OCH2C6H5) | 5 ArH + 2H singlet ~5.1 ppm | C8H7O2, RDBE = 5 |
| Fmoc | 7-8 ArH (complex), 2H at ~4.2 ppm | C15H11O2, RDBE = 11 |
| Acetyl (-COCH3) | 3H singlet ~2.0 ppm | C2H3O, RDBE = 1 |
| Benzyl (-CH2C6H5) | 5 ArH + 2H singlet ~4.5-5.0 ppm | C7H7, RDBE = 4 |
| TMS (-Si(CH3)3) | 9H singlet ~0.0 ppm | C3H9Si, RDBE = 0 |
| Tosyl (-SO2C6H4CH3) | 4 ArH (para pattern) + 3H singlet ~2.4 ppm | C7H7SO2, RDBE = 4 |
| PMB (-CH2C6H4OCH3) | 4 ArH (para) + 2H singlet ~4.4 ppm + 3H singlet ~3.8 ppm | C8H9O, RDBE = 4 |

### Heterocyclic recognition patterns

| Ring system | ArH pattern | 13C pattern | UV λmax |
|------------|-------------|-------------|---------|
| Pyridine | 4H, one shifted to 8.5+ ppm | ~120-150 + 148-155 (C-N) | ~255 nm |
| Pyrimidine | 2-3H at 7-9 ppm | ~120-160 | ~240 nm |
| Furan | 2-3H at 6.0-7.5 ppm | 105-145 | ~200 nm |
| Thiophene | 2-3H at 6.8-7.5 ppm | 120-140 | ~235 nm |
| Pyrrole | 2-3H at 6.0-6.8 ppm + NH | 105-130 | ~210 nm |
| Imidazole | 1-2H at 7.0-8.0 ppm | 115-140 | ~215 nm |
| Indole | 4-5H at 6.5-7.7 ppm + NH | 100-140 | ~270+280 nm |
| Quinoline | 5-6H at 7.0-9.0 ppm | 120-150 | ~270+310 nm |
| Piperidine (saturated) | No ArH, CH2 at 1-3 ppm + NH | 24-47 ppm | No UV >200 |
| Piperazine (saturated) | No ArH, CH2 at 2.4-2.8 ppm | 44-54 ppm | No UV >200 |
| Morpholine (saturated) | No ArH, O-CH2 at 3.6-3.7 + N-CH2 at 2.4-2.7 ppm | 44-67 ppm | No UV >200 |

---

## 8. Multi-spectrum Fusion Strategy

When multiple spectrum types are available for the same molecule, combine them in this priority order:

### Fusion priority

| Priority | Spectrum | What it contributes best |
|----------|---------|------------------------|
| 1 | MS/MS | Molecular formula (strongest single constraint) |
| 2 | IR | Functional group presence/absence (fast binary filter) |
| 3 | 1H NMR | H environments + multiplicities → substructure patterns |
| 4 | 13C NMR | Carbon skeleton (count + types) |
| 5 | HSQC | Precise C-H connectivity (resolves NMR ambiguities) |
| 6 | Raman | Complements IR (symmetric vibrations, C≡C, S-S, C-S) |
| 7 | UV-Vis | Conjugation extent, chromophore identity |

### Fusion rules

1. **All spectra must be self-consistent**: If any spectrum contradicts a proposed structure, the structure is wrong
2. **Start from the most constrained spectrum**: Molecular formula (MS) > functional groups (IR) > detailed structure (NMR)
3. **Use each spectrum for what it does best**: Don't try to determine chain length from IR — use NMR; don't try to determine molecular formula from NMR — use MS
4. **Resolve conflicts by specificity**: If 1H NMR suggests OCH3 but 13C shows no peak at 55 ppm → likely NOT OCH3 (13C is more specific for this assignment)
5. **Accumulate evidence, don't override**: "IR suggests C=O" + "13C shows 170 ppm" + "1H shows no aldehyde H" → ester or acid, not ketone/aldehyde

### Typical fusion workflow

```
1. MS → molecular formula C₁₀H₁₂O₂ → RDBE = 5

2. IR scan → C=O present (1735 cm⁻¹), no OH (no 3200-3600), no NH
   → Ester likely (C=O + no OH + 1735 is ester frequency)
   → Exclude: alcohol, carboxylic acid, amide, amine

3. 1H NMR →
   - 5 ArH (7.2-7.4 ppm, monosubstituted benzene pattern)
   - 2H quartet (4.2 ppm) + 3H triplet (1.3 ppm) → ethyl group on O
   - 2H singlet (3.6 ppm) → CH₂ between ring and C=O
   → Proposed fragments: C₆H₅- + -CH₂- + -COOCH₂CH₃

4. 13C NMR verification →
   - Peaks at 128, 129, 134 ppm → aromatic ✓
   - Peak at 171 ppm → ester C=O ✓
   - Peak at 61 ppm → O-CH₂ ✓
   - Peak at 14 ppm → CH₃ ✓
   - Peak at 41 ppm → benzylic CH₂ ✓

5. Assembly: C₆H₅-CH₂-COOCH₂CH₃ = ethyl phenylacetate
   Check: C₁₀H₁₂O₂ ✓, RDBE = 5 ✓ (benzene 4 + ester C=O 1)
```

---

## 9. Reasoning Checklist

Use this checklist for every structure elucidation:

```
□ Molecular formula determined (or estimated)?
□ RDBE calculated?
□ Aromatic system identified (type, substitution)?
□ Remaining RDBE after aromatic accounted for?
□ All heteroatoms (O, N, S) assigned to functional groups?
□ Exclusion rules applied — what is definitely NOT in the molecule?
□ All detected fragments assembled into one connected structure?
□ Atom count matches molecular formula?
□ RDBE matches?
□ All spectral observations explained by the proposed structure?
□ No spectral contradictions remain?
```
