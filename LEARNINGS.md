# LEARNINGS.md, ratchet

Kvar feil vert til ein regel, éin gong. Nyaste øvst.

- **2026-07-06:** Headless GL (OSMesa + pyrender) i containeren renderar
  berre spekulær refleksjon, ikkje diffus: alle matte flater vart svarte
  same kva lyssetjing. Ikkje bruk tid på å tune pyrender-intensitetar mot
  dette; `verkstad/render.py` er ein liten eigen NumPy z-buffer-rasteriser
  (Lambert + crease-medvitne normalar + mjuk kontaktskugge) utan
  GL-avhengnad. To retningslys, ingen ambient (Ivers val).
- **2026-07-06:** Notion `create-attachment` tek ikkje lokale filer, berre
  `content` (tekst) eller `source_url` (offentleg HTTPS utan redirect).
  For lokale PNG-ar: push til det offentlege repoet fyrst og bruk
  `raw.githubusercontent.com/<owner>/<repo>/<branch>/<sti>` som source_url.
- **2026-07-06:** Konvensjonssveip med regex over md-filer kollapsa
  innrykk i kodeblokker og listeframhald (`re.sub('  +', ' ')`) →
  tekstsveip skal alltid vere fence-medvite (linje for linje, hopp over
  kodeblokker) og aldri røre leiande mellomrom.
- **2026-07-06:** Skrivekonvensjonen «ingen tankestrekar» gjeld
  teiknsetjing, IKKJE bokstavane æøå. Aldri translitterer til aa/oe/ae
  i innhald. (Skjedde to gonger i it. 25; retta manuelt.)
- **2026-07-06:** Notion replace_content kan flytte eksisterande blokker
  til uventa posisjonar → verifiser alltid med fetch etterpå, og rett
  rekkjefølgja med målretta update_content-byte.

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
