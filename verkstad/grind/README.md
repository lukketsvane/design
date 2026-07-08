# Grind, grafbyggjaren for skjelett-strukturar

> Ivers styring 2026-07-08: «now lets make a builder for creating all
> these generative parametrical structures», sju referansebilete av
> keramiske lysestakar og korger bygde av roer og kuler, smelta saman
> som metaballs.

## Grammatikken

Same konstruksjonsprinsipp som `../krone/`: eitt signert felt der alle
element er mjuke unionar (smin) med kontrollert smelteradius, og heile
strukturen er n-periodisk kring aksen. Elementmenyen:

| element | parametrar | kva |
|---|---|---|
| nivaa | L, H, R, f_bot, f_top, buk, twist | nodekransar i hoegda |
| stag | bow, tube, diag | kapsel-bogar mellom nivaa, X-diagonalar |
| ringar | rings (0, endar, alle) | torusar paa nivaa |
| eiker | spokes | stag fraa oevste krans inn til koppen |
| kopp | cup, cup_zf | sentral lysestake-kopp med boring |
| kuler | ball, nub | ledd-kuler paa nodane, knoppar utover |
| munningar | mlen, tilt | opne roerender som foeter (boring subtrahert) |
| loop | loop, loop_out, loop_zf, loop_tilt, loop_lean, loop_ell | lukka blad/drope-ring i tilta radialplan |
| smelt | k | kor mykje alt flyt saman |

Sju verdisett, same kode, mot dei sju referansane:

| sysken | les |
|---|---|
| tromme | laag tromlekorg med ovale hol, eiker, kopp og knoppar |
| stjerne | flat stjernefot med kraftige ledd-kuler |
| totem | hoeg open struktur med boga stag og roermunningar |
| korg | korgvase i tre nivaa med X-fletting og knoppar |
| krabbe | laag fot med kopp og skraastilte roerfoeter |
| kloever | tilta blad-loops kring koppen |
| drope | hoege drope-loops som lener inn mot midtring med kopp |

## Filene

| fil | kva |
|---|---|
| `grind.py` | feltet + marching cubes + reparasjon: vasstette 3MF |
| `print/grind-*.3mf` | dei sju syskena |
| `validering-v01.md` | maaltal, generert av scriptet |

Byggjaren er interaktiv i **Krone Studio** (`../krone/studio/`), som no
er fleirfamilie: familieveljar (Krone, Grind) oevst, preset-chips per
familie, alle parametrane som slidere, shuffle, lampelys, STL-eksport
og delbar URL. JS-feltet er paritetstesta mot dette python-feltet
(maks avvik under 0,001 mm; elementa er identisk geometri).

## Traktat-kopling

- **5.31:** sju trajektoriar gjennom same grammatikk, verdisett i
  `VARIANTS`.
- **2.1:** budsjetta (roertjukn for print, smelteradius, boringar) er
  konstruksjonsvilkaar i feltet, ikkje etterkontroll.
- **1.321:** valideringsrapporten + paritetstesten er projeksjonane.
