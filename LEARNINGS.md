# LEARNINGS.md — ratchet

Kvar feil vert til ein regel, éin gong. Nyaste øvst.

- **2026-07-06:** To loop-økter køyrde parallelt på `main` og laga kvar si
  case-idéliste (it. 15/16) → før persistence: `git fetch origin main` og
  sjekk om remote har flytta seg; har han det, les dei nye committane og
  sjekk for duplikatarbeid FØR du vel neste oppgåve. Ved kollisjon: behald
  begge artefaktar, renummerer, legg konsolidering i backloggen.

- **2026-07-06:** Iterasjon 7 enda i ein *tom* git-commit (arbeidet låg
  berre i Notion) og STATE/BACKLOG vart ikkje oppdaterte → persistence-
  steget skal alltid sjekke `git show --stat HEAD` før push, og STATE.md
  skal oppdaterast i same commit som arbeidet.
- **2026-07-06:** Notion-SQL (`query-data-sources`, sql-modus) kan tidsavbryte
  ved 60 s → bruk view-modus (`mode: "view"` + view-URL) som fallback.
- **2026-07-06:** Notion `create-pages` med mange rader i eitt kall kan
  trunkere JSON → maks ~6 rader per kall, del opp.
- **2026-07-06:** `pdftoppm` manglar i containeren ved oppstart →
  `apt-get update && apt-get install -y poppler-utils` før PDF-lesing.
- **2026-07-06:** Notion-MCP-verktøyprefikset kan endre seg mellom økter
  (server-ID i namnet) → bruk ToolSearch på nytt i staden for å anta
  gamle namn.
