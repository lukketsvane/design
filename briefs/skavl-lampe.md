# Designbrief: Skavl-lampe, form av krefter, ikkje vilje (v1.1, 2026-07-06)

Salone-prototype-kandidat #2 av 3. Full brief på Verkstad-sida i Notion
(page_id 3951c681-5f78-8150-b20f-d1aa75cce756); dette er spegelen.

## Konsept

Skjerm/diffusor der geometrien er generert, ikkje teikna: vekstalgoritme
(differential growth / kraftlinje-following) under harde constraint.
Kvar algoritme-iterasjon er eit «snøfall»; ferdig form er fonna, arkiv
av lag. Le-sida glatt og lystett, lo-sida open og porøs. Programmet sitt
tydelegaste manifest-objekt.

## Aksane

| Akse | Krav | Retning |
|---|---|---|
| Lysspreiing | Blendfri 2700 K ~800 lm | Tettare mot augehøgd |
| Termikk | LED ≤10 W; PLA ~60 °C → 40 mm klaring + konveksjon | Open nær kjelda |
| Materialminimum | <150 g; vegg 0,8-1,2 mm | Porøsitet der mogleg |
| Printfysikk | Utan support; overheng <50°; bru <8 mm | Vinkelbudsjett i algoritmen |
| Skuggeteikning | Skuggen skal teikne lagstrukturen | Ordna anisotropi |
| Montering | E27/GU10; verktøyfri demontering | Toleranse i rota |

## Traktat-kopling

3.4/3.41 (uavhengig konvergens mot naturlege attraktorar: termitthaug,
trabekel), 5.31 (grammatikk = moglegheitsrom, landskap = trajektorie →
familie av søsken med ulik trykkvekting), 1.321 (beste projeksjon gjer
flest trykk synlege), 2.142/3.3 (ser familien ut som ein stil? →
stilarten som sverm demonstrert).

## Prosess

Veke 1: script (vinkelbudsjett 50°, termikk-soner, okklusjonsmål), tre
vektingar. Veke 2-3: print + mål blending/temp/skugge. Veke 4-5: iterer
+ finale. Dokumentasjon: print-timelapse (lag-for-lag = snøfall).

## Foto (16:9)

Tend i mørkt rom (skuggen som hovudmotiv) · porøsitet mot lys ·
tre-søsken-familien.

## Rulling mot brotmodus-taksonomien og algoritmen (v1.1, it. 20)

- **Termikk > mekanikk:** lampas kritiske «brotmodus» er ikkje mekanisk
  brot, men termisk mjukning/kryp (slektning av modus 8): PLA byrjar
  krype alt kring 60 °C. Vurder PETG som standardmateriale (høgare
  mjukningstemperatur, seigare), masse-asserten i
  `briefs/skavl-algoritme.md` må då rekne med ~1,27 g/cm³ i staden for
  1,24.
- **Verktøyfri demontering** (monteringsaksen) er snap-geometri i rota →
  rotfillet ≥ halve snap-tjukkleiken (modus 1) og printretning på tvers
  av bøyeplanet, jf. taksonomien.
- **Testplanen veke 2-3** (temperaturmåling) avgjer materialvalet: logg
  måla mot r_min-klaringa (40 mm) slik at termikk-klemma i algoritmen kan
  strammast/slakkast på data, ikkje på kjensle.

## Salone-skildring (EN, 272 teikn)

"A lampshade grown, not drawn. A growth algorithm navigates hard
constraints, glare, heat, material minimum, print physics, and the
form falls out of the navigation, like snow settling on the lee side of
a ridge. Three siblings, three pressure weightings, one grammar."
