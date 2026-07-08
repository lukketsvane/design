# LEARNINGS.md, ratchet

Kvar feil vert til ein regel, éin gong. Nyaste øvst.

- **2026-07-08:** Vil ein ha «merge and smoothen» (mjuke, smelta overgangar
  som i keramikk), er implisitt felt + smin/smax + marching cubes rett
  verktøy; boolske kutt gjev harde kantar same kor mykje ein glattar
  etterpå. Lykt-settet (boolsk) mot Krone-settet (felt) er beviset.
- **2026-07-08:** Same geometri i to språk (krone.py og studio/worker.js)
  MÅ paritetstestast med tilfeldige punkt før ein stolar på biletet; ein
  halv-segment-forskyving i vinkelinnpakkinga gav «umoglege» artefaktar
  som såg ut som mesher-feil. Testen fann rota på minutt (maks avvik
  0,04 mm etter fiks).
- **2026-07-08:** Marching cubes kan la to flater tangere gjennom same kant
  (valens 4/6, ikkje-manifold). Rett reparasjon er vifte-splitting per
  HJØRNE (union-find over flate-vifta gjennom manifolde kantar), ikkje
  omdøyping av hjørne i enkeltflater; det siste riv opp nabokantane.
- **2026-07-08:** Geometri-detaljar under voxel-pitchen (nålehol r < pitch)
  gjev berre skimmer-støy i marching cubes/SurfaceNets; klem radien opp
  til pitchen i grove pass og bruk eksakte verdiar berre i eksportpasset.
- **2026-07-08:** Chromium i containeren kjem ikkje ut gjennom agentproxyen
  (ERR_CONNECTION_RESET); hent eksterne assets med curl (som går gjennom
  proxyen) og test nettsider lokalt på localhost, som er unnateke.

- **2026-07-06:** Ved matching mot eit referansebilete: identifiser den
  underliggjande STRUKTUREN før du modellerer, ikkje overflate-inntrykket.
  Ribbe-referansen såg ut som «skjel/tekstur» men VAR eit gitter av runda
  rør med hol. Eg brende to rundar på skjel-på-kule før det. Spør: er dette
  ei overflate, eit gitter av element, eller eit felt av hol? Bygg deretter.
- **2026-07-06:** For å matche eit fotografert objekt tel RENDER-oppsettet
  like mykje som geometrien: hard 2-lys-på-kvit såg CG ut; mjuk trelys-rig
  (`porcelain_lights`) + grå gradient-botn + glans gjorde same geometri til
  «porselen». Sjekk lyssetjing/bakgrunn før du konkluderer at forma er feil.
- **2026-07-06:** Skavl-porøsiteten er ikkje avgrensa av print (bru-budsjett)
  men av OPTIKK: blendbandet (inga opning med siktline til LED i elevasjon
  −5° til 60°) fjernar heile øvre halvdel av lo-sida, så sjølv v0.3-slissar
  med minimale web når berre ~18 %, ikkje 30 %. Lærdom for generativ form:
  identifiser kva skranke som faktisk bind FØR du optimaliserer, elles
  tuner du feil parameter (som eg gjorde med web/terskel før eg såg det).
- **2026-07-06:** Ved container-omstart forsvinn pip-installerte pakkar
  (numpy/trimesh/pillow/scipy osv.); git-state overlever. Reinstaller frå
  `verkstad/requirements.txt` fyrst i ei ny økt før du køyrer generatorane
  eller render.py.
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

- **2026-07-06:** To loop-økter bygde kvar sin generator B frå Ivers
  referansebilete (it. 28 vase / it. 30 lampe) og skreiv til same
  fil-namn `print/skavl-b-open.3mf` → den eine committen klabba den andre
  si fil. Regel: kvar generator MÅ namespace outputane sine (`skavl-lamell-*`
  vs `vase-*` vs `skavl-a/b/c`); sjekk `git show --stat` for uventa
  binærdiff på filer du ikkje meinte å endre FØR push. Og: ved gjenteken
  rebase-race, renummerer eiga iterasjon til max(remote)+1 og PUSH med ein
  gong; kodefiler kolliderer sjeldan (ulike namn), berre STATE/BACKLOG gjer.
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
