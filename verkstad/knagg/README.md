# Knagg #1 v0.1: tre hypotesar som printbare solidar

Iterasjon 24 (2026-07-06). Implementerer planen i `briefs/knagg-01.md`
(v1.1): dei tre print-hypotesane som parametrisk kode og ferdige
3MF-filer, klare til slicing. Kortaste printsyklusen i trioen, difor
fyrste falsifiseringsinstrument.

## Kva ligg her

| Fil | Kva |
|---|---|
| `knagg.py` | Generatoren: ryggrad, tverrsnitt-loft, plate, boolske kutt, validering |
| `print/knagg-kraftlinje.3mf` | Hypotese 1: moment-følgjande gods, mest ved rota (PETG, 28 g) |
| `print/knagg-kanalisert.3mf` | Hypotese 2: jamn tjukkleik, sverm-standarden som kontroll (PETG, 27 g) |
| `print/knagg-medvite-svak.3mf` | Hypotese 3: designa brotsone ved rota (PLA, 26 g) |
| `validering-v0.1.md` | Måltala mot aksane (generert av scriptet) |
| `profil-v0.1.svg` | Sideprofilane, brotsona markert med raudt |

Køyr på nytt: `python3 knagg.py` (treng numpy, trimesh, manifold3d,
shapely). Deterministisk: same parametrar gjev same geometri.

## Dei tre hypotesane (same grammatikk, tre vektingar)

1. **kraftlinje**: tjukkleiken følgjer bøyemomentet (t proporsjonal med
   kvadratrota av M, konstant-spennings-taper), rotflaring som gjer
   fillet-regelen kontinuerleg. Tesevarianten: forma er kompromisset,
   designa for å lesast (traktat 2.13).
2. **kanalisert**: same ryggrad, jamn tjukkleik. Sverm-standarden
   (traktat 3.2), kontrollen dei andre vert lesne mot.
3. **medvite-svak**: skarpt spor utan fillet ved cantilever-rota
   (brotmodus 1), dimensjonert til å tole dagleg last (5 kg, SF 1,9)
   og svikte lesbart kring 10 kg statisk. Sviktlatens gjort til
   instrument (traktat 7.14). PLA med vilje: sprøtt brot gjev tydeleg
   signatur.

## Printorientering og styrke

Filene er eksporterte liggjande på sida: laga ligg i bøyeplanet, den
sterke retninga, slik brotmodus-taksonomien krev. Heile knaggen er ein
konstant-breidd 2,5D-kropp (arm og plate begge 16 mm), så heile
flatsida ligg på senga. Ingen support: overheng over 45 grader er
0,11 prosent av arealet (små hjørneradiusar nær senga).

## Validering (hovudtal, sjå rapporten)

- Masse 26-28 g (krav under 40), printtid-overslag 39-42 min (krav
  under 120).
- Utstikk 64-67 mm, momentarm 61 mm (krav 60-80).
- Kontaktradius i sadelen 10 mm (krav minst 8): jakka heng på ei
  flate med stor radius. Tuppen er 5 mm og medvite under kravet,
  fordi tuppen ikkje er kontaktsona og kompromisset skal vere synleg.
- Spenningsoverslaga er fyrsteordens (rektangulært tverrsnitt, last i
  sadelpunktet, Kt 2,5 for sporet). Den fysiske testplanen i briefen
  (5/10 kg, fire vekers kryptest med vekesfoto) kalibrerer tala.

## Montering

Ei forsenka M4-skrue øvst i plata, pluss limflate på resten av plata
for ukjend vegg, jf. monteringsaksen i briefen.

## Traktat-kopling

- 2.13/2.131: kraftlinje-varianten er kompromisset gjort leseleg.
- 3.2: kanalisert-varianten måler avstanden til svermen.
- 7.14: medvite-svak-varianten er falsifiseringsinstrumentet, med
  predikert brotlast (10 kg) som testbar påstand.
- 1.321: valideringsrapporten er projeksjonen som gjer trykka synlege.
