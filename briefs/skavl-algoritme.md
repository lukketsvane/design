# Skavl-lampe: algoritme-skisse v0.1 (pseudokode + parameterliste)

> Loop-iterasjon 11 (2026-07-06). Følgjer brief `briefs/skavl-lampe.md`.
> Nivå: nok til at Iver kan implementere i Grasshopper (Anemone/Kangaroo +
> GhPython) eller rein Rhino-Python. Ingen kode er testa — dette er
> *navigasjonskartet*, ikkje territoriet.

## Grunnval: kurve-stabel, ikkje mesh-vekst

Lampeskjermen er ein stabel av lukka kurver (ringar) frå sokkel til topp;
kvar ring er eitt «snøfall». Differential growth køyrer på kvar ring,
arva frå ringen under. Det gjev tre ting gratis:

1. **Printfysikken vert eksplisitt:** overheng er berre radiell drift
   mellom nabo-ringar — `Δr/Δz ≤ tan(50°)` er ein hard klemme, ikkje ein
   etterkontroll.
2. **Fonn-metaforen er bokstavleg:** forma er eit arkiv av lag; kvar
   iterasjon legg seg oppå den førre, slik snø legg seg på snø.
3. **Skuggeteikninga følgjer med:** ordna anisotropi (lagretning synleg)
   er sjølve datastrukturen.

Loft ringane → solid med veggtjukkleik → boolsk vindauge-kutt på lo-sida
→ STL.

## Felt (definerte på sylinderdomenet θ × z)

| Felt | Definisjon | Rolle |
|---|---|---|
| `vind(θ)` | `cos(θ − θ_le)` glatta; 1 = le-side, −1 = lo-side | Le: glatt/tett. Lo: porøs/open |
| `blend(z)` | 1 i banda som har siktline frå augehøgd til LED-sona, elles 0 | Tettleik og innovervipp der det blendar |
| `term(θ,z)` | avstand til LED-akse/kjelde | < `r_term`: forbode; nær: tving opning (konveksjon) |
| `støy(θ,z,i)` | 2D-simplex/Perlin, frø per søsken | Det «vêret» som gjer kvar køyring unik |

## Pseudokode

```
PARAMETRAR (sjå tabell)

ring[0] = sirkel(r_sokkel)                     # E27-krage + toleranse
for i in 1..N_lag:
    z = i * Δz
    ring[i] = resample(ring[i-1], l_kant)      # jamn nodeavstand

    for kvar node p i ring[i]:
        # 1 · VEKST (differential growth)
        F_vekst  = w_vekst  * støy(θ_p, z, frø) * normal(p)
        F_fråstøyt = w_fråstøyt * sum(unngå naboar nærare enn d_min)
        F_glatt  = w_glatt  * laplace(p)        # kurvatur-glatting
        # 2 · TRYKKVEKTING (aksane frå briefen)
        F_vekst *= lerp(porøs_gain, glatt_gain, (vind(θ_p)+1)/2)
        if blend(z):    F_vekst -= w_blend * normal(p)   # vipp inn/tett
        p += Δt * (F_vekst + F_fråstøyt + F_glatt)

        # 3 · HARDE KLEMMER (projeksjon, aldri "straff")
        p = klemm_overheng(p, ring[i-1], tan(50°) * Δz)  # printfysikk
        p = klemm_term(p, r_term + 40mm)                 # termikk
        p = klemm_boks(p, r_min, r_maks, høgd)           # montering/format

# 4 · VINDAUGE (porøsitet på lo-sida)
overflate = loft(ring[0..N]) + tjukkleik(t_vegg)
for kvar celle c på lo-sida (vind < vind_terskel):
    if støy(c) > p_terskel and blend(z_c) == 0 and term(c) ok:
        kutt ellipse(c, maks_span ≤ 8mm, web ≥ w_min)    # bru-budsjettet

# 5 · SØSKEN: køyr alt tre gonger med ulik vekting
søsken_A = vekt(glare=høg,  porøs=låg,  masse=med)   # «roleg»
søsken_B = vekt(glare=med,  porøs=høg,  masse=låg)   # «open»
søsken_C = vekt(glare=høg,  porøs=med,  masse=min)   # «asketisk»

# 6 · VALIDERING (måltal før print — sjå testplan i briefen)
assert ingen_siktline(augehøgd_band → LED)            # blendfri
assert masse(STL, PLA 1.24 g/cm³) < 150 g
assert maks(overheng) < 50° and maks(bru) ≤ 8 mm
rapport: histogram(overheng), okklusjonsgrad, masse, opningsareal
```

## Parameterliste (startverdiar)

| Parameter | Start | Kommentar |
|---|---|---|
| `N_lag` | 120 | algoritme-lag ≠ print-lag; 2 mm per ring, høgd ~240 mm |
| `Δz` | 2 mm | ringavstand før loft |
| `l_kant` | 3 mm | node-avstand etter resampling |
| `d_min` | 2,5 mm | fråstøytingsradius (hindrar sjølvkryss) |
| `Δt` | 0,3 | steglengd; lågare = rolegare vekst |
| `w_vekst / w_fråstøyt / w_glatt` | 1,0 / 1,2 / 0,4 | grunnbalansen; glatt opp på le-sida |
| `porøs_gain / glatt_gain` | 1,6 / 0,5 | lo- vs. le-forsterking av vekst |
| `w_blend` | 0,8 | innovervipp i blendingsband |
| `θ_le` | 0° | kvar le-sida vender; foto-avgjerd |
| `r_sokkel` | 22 mm | E27-krage +0,3 mm toleranse (mål faktisk fatning!) |
| `r_min / r_maks` | 35 / 110 mm | termikk-golv (40 mm klaring) / format |
| `r_term` | LED-radius | mål på faktisk pære |
| `t_vegg` | 1,0 mm | midt i 0,8–1,2-budsjettet |
| `p_terskel` | 0,55 | del av lo-sida som opnar seg (~30 %) |
| `w_min` | 3 mm | minste web mellom vindauge |
| `frø` | 3 ulike | eitt per søsken; loggfør! reproduserbarheit er poenget |

## Implementasjonsnotat

- **Grasshopper-veg:** Anemone (loop) + GhPython for klemme-stega;
  Kangaroo2 kan ta fråstøyt/glatting som «goals», men dei harde klemmene
  skal vere projeksjonar *etter* solver-steget, elles vert 50° mjuk.
- **Rein-Python-veg:** heile kurve-stabelen er ~200 liner numpy;
  eksporter ringane til Rhino for loft, eller loft direkte med
  `rhino3dm`. Enklare å versjonere enn .gh-fil.
- **Slicer-sjekk:** PrusaSlicer med 2 perimeter à 0,5 mm (= t_vegg 1,0 mm,
  jf. briefen) + «detect bridging perimeters»; samanlikn slicerens overheng-varsel med algoritmens
  histogram — avvik = feil i klemma.
- **Timelapse:** print-timelapsen (lag-for-lag = snøfall) er
  dokumentasjonskravet frå briefen; set kamera før fyrste testprint.

## Referansar (metode)

- Anders Hoff: [Differential line growth](https://inconvergent.net/generative/differential-line/) — kanonisk skildring av vekst + fråstøyt + glatting på kurve.
- Nervous System: [Floraform](https://n-e-r-v-o-u-s.com/blog/?p=6721) — differensiell vekst under fysiske constraint; nærast i ånd.
- Long Nguyen: [C#/Grasshopper differential growth-workshop](https://www.youtube.com/watch?v=dSyBhAWc9Y0) — implementasjonsdetaljar (spatial hashing for fråstøyt).
- Daniel Piker: [Kangaroo2](https://www.food4rhino.com/en/app/kangaroo-physics) — solver-alternativet i Grasshopper.

## Traktat-kopling

- **5.31:** grammatikken (pseudokoden) er moglegheitsrommet; kvar
  parametervekting er ein trajektorie gjennom det — søskena er tre
  trajektoriar, éin grammatikk.
- **2.1:** klemme-stega er seleksjonstrykka gjort bokstavlege:
  projeksjonar som avgrensar kvar forma *ikkje* kan vere.
- **3.4/3.41:** om resultatet konvergerer mot termitthaug/trabekel utan
  at me har teikna det, er det uavhengig konvergens demonstrert — loggfør
  likskapen når printane kjem.
- **1.321:** valideringsrapporten (okklusjon, masse, overheng) er
  «projeksjonen som gjer flest trykk synlege» — legg han ved kvar print.
