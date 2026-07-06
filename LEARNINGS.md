# LEARNINGS.md — ratchet

Kvar feil vert til ein regel, éin gong. Nyaste øvst.

- **2026-07-06:** Notion `create-pages` med mange rader i eitt kall kan
  trunkere JSON → maks ~6 rader per kall, del opp.
- **2026-07-06:** `pdftoppm` manglar i containeren ved oppstart →
  `apt-get update && apt-get install -y poppler-utils` før PDF-lesing.
- **2026-07-06:** Notion-MCP-verktøyprefikset kan endre seg mellom økter
  (server-ID i namnet) → bruk ToolSearch på nytt i staden for å anta
  gamle namn.
