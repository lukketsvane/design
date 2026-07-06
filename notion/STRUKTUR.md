# Notion-strukturen (kanonisk skildring)

Sist rulla: iterasjon 26, 2026-07-06. ID-ar i `manifest.json`.

## Hovudsida FORMLÆRE (dashbord)

Rekkjefølgje på sida, med føremål:

1. **No: det viktigaste fyrst.** Raud callout med dei tre avgjerande
   punkta (print knaggane, namneval, dobbeltfristen 15. sep).
   Oppdaterast når prioriteringane flyttar seg.
2. **Oppgåver-databasen, inline.** Den kanoniske handlingskøa.
   Views: Kanban etter status, Kalender med fristar, Treng Iver etter
   frist (filtrert tabell). Speglar BACKLOG.md i git.
3. **Verkstad.** Objekta med fase-kanban. Printfiler i git under
   `verkstad/`.
4. **Skriving og vegkart.** Skriveprosjekt (fase-kanban), Vegkart
   (horisont-kanban og tidsline), Søknadspakke-sida.
5. **Grunnlag og strategi.** Tesen, Snøhetta-analogien, sidene 01-05.
6. **Referansar og logg.** Bibliotek, Prinsipp, Logg, 06 Agent-loop.
7. **Slik heng systemet saman.** Tabell som forklarar kvar database
   pluss arbeidsdelinga menneske/agent.

## Databasane

| Database | Rolle | Master |
|---|---|---|
| Oppgåver | Handlingskøa med status, prioritet, frist, eigar | Notion (BACKLOG.md er agent-spegelen) |
| Verkstad | Produkt/eksperiment, aksar og traktat-kopling per objekt | Notion |
| Skriveprosjekt | Casar og manifest med fase | Notion |
| Vegkart | Horisontane H0-H3 | Notion |
| Bibliotek | Kjelder | Notion |
| Prinsipp | Operasjonelle reglar frå traktaten | Notion |
| Logg | Ei rad per iterasjon/hending | Notion |

Git speglar ikkje databaseradene; større funn vert destillerte inn i
`strategy/` og `research/`.

## Synk-reglar for Oppgåver

- Ny `[TRENG IVER]`-oppgåve i BACKLOG.md skal få ei rad i Oppgåver
  med Status = Treng Iver, og omvendt.
- Når Iver flyttar noko til Gjort i kanbanen, kryssar neste
  loop-iterasjon av i BACKLOG.md (og omvendt).
- Fristar skal alltid ha dato i Frist-feltet slik at kalenderen er
  komplett.

## Skrivekonvensjonar (Ivers instruks 2026-07-06)

Ingen tankestrekar, ingen ikon, ingen emojiar, i git og Notion.
Nynorsk i alt innhald. Sjå CLAUDE.md.
