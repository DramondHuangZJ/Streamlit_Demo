# Verification of the pilot website

Verified 24–25 November 2026. This report evaluates website function and stimulus-material preparation, not the dissertation hypotheses or actual stimulus equivalence.

## Automated checks

Command: `.venv/bin/python -m pytest -q --junitxml=docs/test-results.xml`.

The suite contains 19 passing cases. The final isolated environment uses Python 3.11.5, Streamlit 1.55.0, pandas 2.3.3, SciPy 1.17.1 and pytest 8.4.2; the complete run passed in 2.98 seconds. Exact runtime metadata is in `test-environment.json`, with machine-readable results in `test-results.xml`. It covers concurrent balanced assignment, stable assignment/resume after reruns, both complete game orders (English and Simplified Chinese), missing required answers, correct and incorrect scoring, transactional saves, stale/double submissions, finalization, real server-side 90-second enforcement, withdrawal, excluded test records, empty/full CSV export, anonymous export fields, password-protected administration, HTTPS handoff fields, missing-image fallback, material-version mismatch protection, external questionnaire versioning, external CSV join/reverse coding, external descriptive diagnostics and live configuration refresh.

Both full Streamlit AppTest sessions submitted every trial and quiz item through the participant UI. They reached the debrief page in the two assigned orders. For automated speed only, the test fixture moves the filler entry timestamp back by 91 seconds. A separate test proves early continuation is rejected. Browser verification additionally exercised the actual elapsed-time gate.

## Browser and storage checks

- Launched the application on `http://localhost:8502` and inspected the participant pages in native Chrome.
- Completed a full manual Chinese session, Dragon Castle then Azul, including all six trial decisions, all ten comprehension questions, both preview questionnaire handoffs, the neutral break, final submission and debrief.
- Reconciled that manual session against SQLite: completed status, six trial rows and ten quiz rows, with all ten entered quiz answers scored correctly. This walkthrough was on stimulus version 2; the final version 3 replaces the remaining task schematics with the reviewed AI component images. Both final-version orders were then covered by the automated full-flow cases, and the final images were inspected in Chrome and on the hosted deployment.
- Exported the completed manual record into a nine-entry ZIP (eight normalized CSV tables plus manifest). Verified it contained the matching participant row and no resume credential hash. The private QA export is kept in ignored `exports/`, outside Git.
- Checked the participant interface at a desktop width and a responsive 400-pixel viewport. The final build was checked again at 400 pixels after the image and header changes; mobile text, controls and product imagery fit the viewport. Screenshots in the visual summary show the inspected views.
- Browser inspection found retained scroll position between stages and a header overlap. Stage transitions now reset to the heading, and content padding clears the Streamlit header.
- Configuration files are refreshed on reruns without replacing shared material references. A session stops if its assigned material version differs from the configured version, preventing silent mixing of revised stimuli.

## Hosted preview

Published a separate app at https://phd-board-game-pilot.streamlit.app using repository `DramondHuangZJ/Streamlit_Demo`, branch `pilot-study`, file `app.py`, Python 3.12, and explicit preview-mode configuration. The original demo deployments on `main` remain separate.

Observed the hosted bilingual welcome, Dragon Castle product page, AI component lesson and trial. Submitted trial responses and observed advancement into the quiz. This verifies deployed execution and incremental task saving. It does not claim a completed real questionnaire or durable Cloud data storage.

## Material checks

- Located and inspected primary publisher game pages and the official English rules.
- Checked the Dragon Castle consolidation illustration and numerical scoring, beginner setup, permitted picks, placement restrictions and countdown end condition.
- Checked Azul's original colored-wall rules, display drafting, line restrictions, isolated-tile scoring and round-end trigger.
- Each game has six rule sections, two worked examples, three trial decisions and five quiz items. English lesson bodies contain 261 and 269 words respectively.
- Inspected six AI images, each 1536×1024 pixels, against the publisher references and intended scenarios. Checked two-vs-three coin identity, four connected Merchant tiles, exactly two blue/one red/one yellow Azul tiles and one isolated raised wall tile. Files and hashes are listed in `asset-manifest.json`.
- Official rulebook figure captures are available separately as source references. Full source PDFs and original reference photographs are excluded from Git.

## Limits and delegated checks

The website contains no consent, eligibility, demographic or rating questionnaire. The user explicitly moved those to an external platform. Consequently, consent-decline/under-18 termination and all questionnaire validation must be tested on that platform. No website test is presented as proof of those external branches.

The two real questionnaire links, provider export and redirect flow have not been supplied. URL construction, matching keys and return mechanics are tested, but a real-provider end-to-end handoff remains a recruitment requirement. The current continuation is participant-reported, not a signed provider confirmation. Missing links can be bypassed only in preview/test sessions.

The site is not recruitment-ready: researcher/ethics details, translation review, material fidelity/usage review, price treatment, practical equivalence bounds and durable storage remain as listed in `RESEARCHER_CHECKLIST.md`. All preview records are test data and are excluded from analysis exports by default. No real participant data, payment identifiers, password or database file is published to GitHub.

## Deliverable audit

| Requested deliverable | Evidence |
| --- | --- |
| Working Streamlit application | `app.py`, `pilot/`, current local launch and public Cloud preview |
| Exact launch instructions | README.md with the current-machine interpreter, environment setup and command |
| Architecture | README.md plus DATA_DICTIONARY.md |
| Test results | Nineteen passing tests, both complete game orders, test-results.xml and test-environment.json |
| Screenshots or visual summary | VISUAL_SUMMARY.md with selected final screenshots and generated component images |
| Temporary placeholders | RESEARCHER_CHECKLIST.md: external links/version, researcher/ethics fields, price and material/translation approval |
| Research decisions before recruitment | RESEARCHER_CHECKLIST.md: screening/consent on the external platform, fieldwork approvals, scale/content fit, equivalence bounds, prior exposure/exclusion rules, survey-return reconciliation and persistent hosting |
| Real-game material discovery | MATERIALS.md, primary-source rule references in config/games.json, six AI component/product renderings and selected official figure captures |
| Local code and GitHub updates | Standalone local folder, tracked pilot-study branch, completed code updates pushed to origin |

The remaining pre-recruitment decisions are intentionally exposed rather than described as approved. They do not prevent using the preview, testing its tasks or configuring the future external questionnaire links.

## Color contrast

Configured text/background pairs were calculated using WCAG relative luminance. This verifies the specified palette rather than claiming a full accessibility audit.

- Body text: 14.41:1.
- Caption text: 6.13:1.
- Primary button: 6.98:1.
