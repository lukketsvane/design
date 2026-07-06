# Brotmodus-taksonomi v0.1, datagrunnlag for reparasjonssettet

> Research-notat, loop-iterasjon 13 (2026-07-06). Følgjer
> `briefs/reparasjonssett.md` (veke 1: taksonomi). Spørsmål: kva veit
> verda faktisk om korleis hushaldsplast brotnar, og kva tyder det for
> dei ~10 delfamiliane i settet?

## Kva datakjeldene faktisk seier

**1 · Open Repair Alliance (ORA).** Største opne datasettet om
reparasjonsforsøk: 103 000+ registrerte forsøk frå 650 reparasjonsgrupper
i 27 land, standardisert i [Open Repair Data Standard](https://standard.openrepair.org/standard.html),
publisert halvårleg ([openrepair.org/open-data](https://openrepair.org/open-data/)).
Vanlegaste feil på Restart-partya: **leidningsbrot, utslitne tannhjul,
øydelagde brytarar/knappar, redusert batterikapasitet**
([milepælsmeldinga](https://openrepair.org/news/open-repair-reaches-a-major-milestone-over-100000-records-of-repair/)).
Viktigast for settet: når ting *ikkje* vert fiksa, er hovudbarrieren
**mangel på reservedelar** (pris eller tilgjenge), dernest at produktet
ikkje lèt seg opne. Settet svarar direkte på barriere #1, det er
reservedelen som ikkje finst i sal.
*Atterhald:* ORA dekkjer elektriske/elektroniske produkt; reine
plastbrot (klips, hengsler, skaft) er underrepresenterte i data, men
overrepresenterte i røynda, difor treng veke 1 eiga feltregistrering.

**2 · Snap-fit-ingeniørlitteraturen.** Konsistent på tvers av kjelder
([Xometry](https://xometry.pro/en/articles/snap-fit-joints-for-plastics/),
[RapidDirect](https://www.rapiddirect.com/blog/snap-fit-design/)):
den vanlegaste enkeltfeilen i plastprodukt er **rotbrot i
cantilever-snap**, skarpt hjørne konsentrerer spenning; regel: rotfillet
≥ halve snap-tjukkleiken. Deretter: **kryp** (permanent deformasjon under
langvarig last), **utmatting** (gjentekne syklar) og **laus passform**
(toleranseslitasje). Materialnotat: PP toler flexing (living hinges); ABS
er stivare og sprekker lettare ved dårleg design, relevant for kva
printmateriale protesedelane bør ha (PETG/PP-liknande seigleik, ikkje PLA
rett av spolen for fleksleddet).

## Taksonomien v0.1: ti brotmodusar → fire delfamiliar

| # | Brotmodus | Typisk objekt | Mekanisme | Delfamilie |
|---|---|---|---|---|
| 1 | Knekt snap-klips (cantilever-rot) | Batterideksel, panel, deksel | Spenningskonsentrasjon i skarp rot | **Klips-protese** (ny familie?) |
| 2 | Oversprengt/utsliten skruegjenge i boss | Alt med sjølvskruande skruar | Gjenge i plast toler få syklar | **Gjenge-lapp** |
| 3 | Broten hengsel / living hinge | Lok, boksar, brilleetui | Utmatting i tynnseksjon | **Hengsel-protese** |
| 4 | Skaft-/halsbrot i bøyemoment | Kosteskaft, verktøyhandtak, stenger | Bøyespenning > styrke ved tverrsnittshopp | **Skøytehylse** |
| 5 | Skalsprekk etter fall/støyt | Kabinett, kanner, leiker | Sprøbrot, gjerne frå hjørne/hol | **Spennband** + lapp |
| 6 | Avriven tapp/aksel/tannhjul | Knottar, sveiver, girmekanismar | Torsjon/slitasje (jf. ORA «worn gears») | Skøytehylse (aksel-variant) |
| 7 | Broten krok/øyre/oppheng | Kroker, stroppfeste, oppheng | Strekk over lite tverrsnitt | Klips-/krok-protese |
| 8 | Kryp-deformasjon | Hylleknektar, klemmer under last | Langtidslast + varme | (førebyggjande skinne?) |
| 9 | Laus passform / toleranseslitasje | Ting som «ikkje klikkar lenger» | Slitasje av kontaktflater | Klips-protese med strammemonn |
| 10 | Delaminering/limfuge-svikt | Samansette produkt, tidlegare limte | Feil lim på feil plast (PP/PE limer dårleg) | Spennband (mekanisk, ikkje kjemisk) |

**Observasjon som styrkjer konseptet:** modus 10 er grunnen til at
«berre lim det» ofte sviktar, polyolefinar (PP/PE, størstedelen av
hushaldsplast) er nesten ulimbare utan primer. Mekanisk skøyting
(hylse, band, protese) er difor ikkje eit estetisk val, men det
teknisk rette svaret for dei vanlegaste materiala. Kintsugi-logikken
og ingeniørlogikken konvergerer, uavhengig konvergens (3.4) i miniatyr.

## Konsekvensar for delfamiliane

1. **Klips-protesen bør rykke opp** som eiga familie (modus 1, 7, 9, 
   truleg den vanlegaste gruppa i felt): parametrisk cantilever med
   generøs rotfillet, printretning på tvers av bøyeplanet.
2. **Skøytehylsa** må finnast i to variantar: bøyemoment (skaft, modus 4)
   og torsjon (aksel, modus 6), ulik geometri, ulikt krav.
3. **≥50 N-kravet** frå briefen gjeld ulikt: strekk (krok), bøying
   (skaft), skjer (klips), testplanen i veke 4 må måle per modus, ikkje
   éin generisk verdi.
4. **Materialtilråding for protesar:** PETG som standard (seigleik +
   printbarheit); PLA berre for stive, ikkje-fleksande delar (lappar,
   band-lås).

## Veke 1-feltregistrering: kortmal

For kvar av dei 20 objekta: *objekt · funksjon tapt (ja/nei) · materiale
(gjetting: PP/PE/ABS/PS/anna) · brotmodus (1-10 + «anna») · lastretning
ved brot (strekk/bøy/torsjon/støyt) · kvifor ikkje reparert før (barriere)*.
Siste feltet gjev norsk mikrodata å halde mot ORA-barrierane, og éi
setning til Salone-teksten om kvifor delane ikkje finst i sal.

## Kjelder

- [Open Repair Alliance: Open data](https://openrepair.org/open-data/) og [ORDS-standarden](https://standard.openrepair.org/standard.html)
- [ORA: 100 000-milepælen](https://openrepair.org/news/open-repair-reaches-a-major-milestone-over-100000-records-of-repair/), vanlegaste feil + reservedelsbarrieren
- [The Restart Project: Repair data & insights](https://therestartproject.org/data-and-insights/)
- [Xometry: Snap-fit joints for plastics](https://xometry.pro/en/articles/snap-fit-joints-for-plastics/), rotbrot, kryp, utmatting, toleranse
- [RapidDirect: Snap fit design](https://www.rapiddirect.com/blog/snap-fit-design/), rotfillet-regelen, materialval PP/ABS

## Traktat-kopling

- **5.6/5.601:** taksonomien *er* omhugsfordelinga for settet, ti aksar
  der kvar delfamilie må velje kor nær terskelen han går (universalitet ↔
  presisjon per modus, ikkje generelt).
- **7.x (sviktsignatur):** kvar brotmodus er ein sviktsignatur i
  originalobjektet, settet gjer signaturen leseleg i staden for å viske
  han ut; taksonomikorta til Salone er bokstavleg tala sviktsignatur-atlas.
- **Etterordet (obsolesens):** reservedelsbarrieren frå ORA er systemets
  tid mot materialets, delen finst ikkje i sal fordi systemet har
  avskrive objektet før materialet har.
