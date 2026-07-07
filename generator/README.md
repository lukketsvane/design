# generator/ — FORMLÆRE generativ motor

Frå genom til produksjonsmodell. Motoren realiserer formspråket
(`strategy/07-formsprak.md`) som faktisk, printbar geometri.

## Køyr

```
pip install numpy scikit-image trimesh matplotlib   # éin gong
python3 generator/grow.py --n 6 --seed 42 --out generator/out
```

Ut:
- `out/sibling_NN.stl` — vasstette produksjonsmodellar (slice/print/støyp)
- `out/contact_sheet.png` — sverm av søsken (rask visuell utval)
- `out/genomes.json` — genom + volum/mål/vasstett-status per søsken

## Modellen (kopla til traktaten)

| Kode | Traktat |
|---|---|
| `Genom` (parametervektor) | Posisjon i formrommet (1.3) |
| kvart genom-felt | eit seleksjonstrykk (2.1) |
| `grow_spheres` (aggregasjon) | formgjevaren som navigerer (5.11–5.13) |
| smooth-union → marching cubes | forma fell ut av navigasjonen |
| sverm av søsken | stilarten som sverm kring attraktor (3.3) |

## v1 dekkjer

Bulbøs sfære-aggregasjon (blomkål/molekyl/totem — ref IMG_7404/7405).

## Backlog for motoren

- Ribbe/differential-growth-modus (kråkebolle/lamell/gjelle)
- Radial hòl-topologi (vase, skjerm, krukke)
- Veggtjukn-offset + overheng/krymp-sjekk for keramikk-print
- Omhugs-score for automatisk utval av beste søsken
- OBJ + fargekart for celadon-dal-lesing
