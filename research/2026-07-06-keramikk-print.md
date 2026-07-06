# Research-notat: keramisk 3D-print for formspråket (iterasjon 9)

Kritisk sti for flaggskip-objekta (Formspråk-sida). Kva utstyr og prosess
skal til for å realisere den generative celadon-keramikken?

## To vegar til objektet

### Veg A — direkte paste-print (LDM)
- **WASP 40100 LDM**: designar-/arkitektstudio-klasse; 50 µm lagoppløysing,
  opptil 150 mm/s; leire/porselen/steingods/terrakotta. Dyse 1,2 og 2 mm.
  Porselen: WASP tilrår 95 % porselen + 5 % vatn. Leverer med Simplify3D.
- **WASP Delta 2040 Clay**: mindre, rimelegare desktop-delta.
- **Eazao Potter**: rimelegaste desktop keramikk-printer (direkte
  ekstrudering, ekte leire) — inngangsnivå, godt for prototyping.
- Kjelder: 3dwasp.com/en/ceramic-3d-printer-wasp-40100-ldm ·
  eazao.com · 3dnatives.com/en/ceramic-3d-printers-130120204

**Konsekvens for formspråket:** dei fine lamellane (05) og tette piggane
(01) er på grensa av kva 1,2 mm-dyse klarer i wet clay uten kollaps.
Ribbe-avstand må ≥ ~3× dysebreidde; overheng-grensa er strengare enn PLA
(wet clay saggar). Differential-growth-algoritmen må difor få eit
*strammare* vinkel- og spennbudsjett enn skavl-lampa i PLA.

### Veg B — PLA-positiv → gipsform → støypt porselen
- Print forma i PLA (billeg, presis), lag gipsform, slå/støyp i
  flytande porselen (slip casting). Gjev tynnare veggar og skarpare
  detalj enn direkte print, men taper «print-lag»-estetikken.
- Best for objekt der lamell-finleiken er poenget (Fonn-vasen).

## Etterarbeid (begge vegar)

Grønt → tørk → sintring (bisque ~900 °C) → celadon-glasur → glasurbrenning
(~1250–1280 °C reduksjon for jern-celadon). Celadon *pyttar seg i
dalane* og les geometrien — difor forsterkar glasuren nett den
lagstrukturen formspråket byggjer på. Fargen kjem av jern(II) i
reduksjonsatmosfære.

## Avgjerdspunkt (`[TRENG IVER]`)

1. **Har AHO paste-ekstruder + reduksjonsomn?** Avgjer veg A vs. B og om
   keramikk rekk Salone (30/8) eller vert H1. Sjekk keramikk-/
   materialverkstaden på AHO.
2. **Prototyp-strategi:** køyr Eazao/desktop for rask formiterasjon;
   finale på WASP 40100 om tilgjengeleg (Fellesverkstaden/eksternt).
3. Om keramikk ikkje rekk 30/8: PLA-trioen dekkjer Salone/Greenhouse;
   keramikken vert diplomspor + H1-flaggskip.

## Konklusjon for vegkartet

Keramikken er flaggskipet, men har lengre syklus (brenning, glasur) enn
PLA. Realistisk: **PLA-objekt til H0-søknadene (aug/sep 2026); generativ
celadon-keramikk som diplom- og H1-spor (2027–28)** der ho får tid til
å bli rett. Skavl-algoritmen er felles motor for begge.
