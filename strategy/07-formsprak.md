# 07 · Formspråk: den generative keramikken

Den visuelle kjernen. Referanseobjekt i `assets/formsprak/`. Notion:
page_id 3951c681-5f78-8141-afd0-dbe350b0c6e6.

## Påstanden

*Form follows fitness* har hatt eit språkproblem — lettare å seie enn å
vise. Desse 3D-printa keramikkobjekta løyser det: radiell symmetri,
segmentering og ribbing (krek, kråkebolle, virvel, gjelle, korall) er
minimalt materiale som spenner over maksimal flate. Dei ser grodde ut,
ikkje teikna. Celadon-glasuren er den same Song-keramikken traktatens
diktet XIV byggjer på.

## Kvifor desse formene ber tesen

Traktaten hyllar former *designa utan designar* — korall, termitthaug,
trabekel, elvedelta (XLIII), spindelvev Pareto-optimal (LIV). Alle:
minimalt materiale, maksimal funksjon, via eit vekstprinsipp under
constraint. Keramikken er same løysing i artefakt → den synlege
signaturen av rammeverket, ikkje ein vald stil.

## Formgrammatikken (5 reglar)

1. Radiell/aksial grunntopologi — men broten (sverm kring attraktor, 3.3).
2. Segmentet er vekst-eininga (lag på lag, diktet XII).
3. Materialminimum som ærlegheit (ribba ER strukturen, XLV/LVI).
4. Celadon som materialidentitet (glasur les geometrien, diktet XIV).
5. Det skal sjå grodd ut (sluttprøve: «Spor, ikkje påstand»).

## Referanseobjekt

| Fil | Morfologi | Traktat |
|---|---|---|
| 01-radial-skive | Torus m/ ~50 piggar, kråkebolle | XXIII, XXV |
| 02-kuppel-ribbe | Ribbekuppel, radiolar | XLV, XLIII |
| 03-virvel-segment | Segmentert band, virvel | XII, 5.123 |
| 04-skjel-blad | Bladribber, ammonitt | LV |
| 05-lamell-vase | Lamell over rå betong | XII (stratigrafi) |

## Teknisk veg

Grasshopper + Anemone/Kangaroo2/Weaverbird (differential mesh growth,
sjå briefs/skavl-algoritme.md) → keramisk paste-print (LDM) eller
PLA-positiv → støypeform → porselen → celadon-glasur.
