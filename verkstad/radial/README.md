# Ribbe, radiale finnar (arbeidsnamn)

> Ny retning, starta etter Ivers referansebilete (celadon-porselen,
> vertebra/gjelle-struktur, 2026-07-06). Radiale finnar som byggjer ein
> porøs kule, med djupe glipor som teiknar skuggen. Svaret på Skavl-funnet
> at blendbandet kapslar porøsiteten: her ER glipene mellom finnane
> opningane, og dei kan vere så store me vil.

## Kva ligg her

| Fil | Kva |
|---|---|
| `radial.py` | Generatoren: finnesilhuett, ekstrudering, radial array, vri |
| `print/ribbe-blad.3mf` | Søsken «blad»: reine vertikale ribber, roleg |
| `print/ribbe-virvel.3mf` | Søsken «virvel»: vertebra-skjel stabla på ribbene |
| `print/ribbe-spiral.3mf` | Søsken «spiral»: skjela vridd rundt aksen (hero) |
| `_iter.py` | Rask iterasjonshjelpar (byggjer + renderar lite) |

Køyr: `python3 radial.py` (skriv `print/ribbe-*.3mf`). Render:
`python3 ../render.py --radial` (celadon, glans, familiestripe).

## Grammatikken

Kvar finne er ein 2D-silhuett i (radius, høgd)-planet, ekstrudert til ein
tynn vegg (tjukkleik `t` i tangentretninga) og arrayd `n_fin` gonger rundt
aksen. Konvolutten `R(z)` set kula (0 ved polane, `r_max` ved ekvator,
`power` < 1 gjev rundare kule). Ei undulasjon legg vertebra-skjela på
ytterkanten: kvar skjel er ein glatt node med ein djup hals under, og
`hook` skeivar noden oppover så tuppane nebbar ut-og-opp som skjel. `twist`
vrir finnene rundt aksen med høgda (spiral-søskenet).

Same tre-søsken-logikk som Skavl (traktat 5.31): éin grammatikk, tre
vektingar. «blad» = undulasjon av, «virvel» = skjel utan vri, «spiral» =
skjel med vri.

## Status og neste steg

- **Form:** låst mot referansen, tre søsken renderer i celadon.
- **Ikkje vasstett enno:** finnene er konkatenerte (ikkje boolsk union),
  godt nok for render men ikkje for print. Neste: boolsk union av finnar +
  nav til éin vasstett solid, eller gje kvar finne ein delt rot som møter
  navet reint, så validering (veggtjukkleik, overheng, E27-krage, masse).
- **Blend/termikk:** som lampe må navet husa E27 og glipene sleppe
  konveksjon; blendbandet frå Skavl gjeld framleis for direkte innsyn til
  kjelda, men her kan finnene skjerma sikta utan å tette opningane.
- **Namn:** arbeidsnamn «Ribbe»; kandidatar Virvel/Finne/Skjel/Kam står
  til Iver (jf. namnevalet i STATE-blokkeringane).

## Traktat-kopling

- **3.4/3.41:** forma konvergerer mot ein biologisk attraktor (vertebra,
  kråkebolle, gjelle) utan at me teikna arten; loggfør likskapen.
- **5.31:** grammatikk + tre trajektoriar = søskenfamilie.
- **2.1:** konvolutt og skjel-undulasjon er projeksjonar; glipa er ikkje
  eit tillegg men fråværet av materiale, forma er det som står att.
