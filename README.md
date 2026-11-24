# Board game pilot website

A bilingual English / Simplified Chinese Streamlit website for learning and trying Dragon Castle and Azul. Each participant sees both games in a randomly balanced order. Each game has a product page, a six-section rule lesson, two worked examples, three scenario decisions and five comprehension questions. A 90-second neutral activity separates the games.

**Questionnaires are external**, as requested. The website does not administer rating scales, background surveys, consent forms or eligibility questionnaires. It opens a configured questionnaire after each game and records the participant's return. Eligibility, consent, questionnaire completion and payment must be managed and checked on the external platform. No AI assistance manipulation is included. AI-generated product imagery is stimulus material, not participant assistance.

The default is a functional **research preview**. Every preview record is marked as a test. Recruitment is disabled until the researcher checklist is satisfied.

## Local setup and launch

Use Python 3.11 or 3.12. In a terminal:

```sh
cd '/Users/dramond/.codex/.chatgpt-projects/g-p-6a8abbc6e30c8191aa8cd7203958ed24/pilot_study_streamlit'
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502
```

Open [http://localhost:8502](http://localhost:8502). The terminal must remain running. Choose English or 简体中文 before starting. The chosen language stays fixed for that session. Closing and reopening the same session URL restores the assigned order and saved step. Treat session URLs as private: the random `resume` value is a bearer capability.

On the current machine the prepared `.venv` uses the existing Python 3.11 environment. It can also be launched without activation:

```sh
.venv/bin/python -m streamlit run app.py --server.port 8502
```

## External questionnaires

Set `PILOT_SURVEY_URL_1` and `PILOT_SURVEY_URL_2` to HTTPS survey links for first- and second-game evaluations. These are presentation positions, not fixed game identities. Set `PILOT_PUBLIC_URL` to the deployed website's base URL. Use environment variables or `.streamlit/secrets.toml`; examples contain no real credentials. `.env.example` is documentation and is not loaded automatically.

Read [the handoff guide](docs/EXTERNAL_QUESTIONNAIRE.md) before integrating a survey. Missing links have an explicitly labelled preview bypass. Real sessions cannot use that bypass. The existing generic handoff records **participant-reported return**, not verified survey submission. No end-to-end connection to a real questionnaire provider is claimed before its links and return behavior are configured and tested.

## Researcher tools

Set a strong `PILOT_ADMIN_PASSWORD` in your shell or Streamlit secrets, then open `http://localhost:8502/?researcher=1`. The dashboard requires that password. It reports started/completed sessions, assigned orders, elapsed completion time, missing task records, quiz accuracy by game/item and descriptive paired accuracy differences with 95% t intervals. It exports normalized CSVs in a ZIP. Test records and unfinished records are excluded from analysis exports by default. Withdrawn sessions contribute only an anonymous administrative count.

Local commands use the operating-system account's file permissions:

```sh
.venv/bin/python admin.py summary
.venv/bin/python admin.py --include-tests summary
.venv/bin/python admin.py export --output exports/pilot.zip
.venv/bin/python admin.py --include-tests export --output exports/qa.zip --include-incomplete
.venv/bin/python admin.py merge-external external_game_evaluations.csv --output exports/joined.csv
.venv/bin/python admin.py analyze-external external_game_evaluations.csv --output exports/external_diagnostics.json
```

The optional merge consumes a de-identified external game-level CSV. It does not create a questionnaire on the site. Raw item values are retained; complete scale scores are calculated separately, with documented reverse coding. See [the data dictionary](docs/DATA_DICTIONARY.md). Scores are missing when any scale item is missing; no imputation or automatic item deletion occurs.

## Architecture

- `app.py`: bilingual participant flow and password-protected researcher view.
- `config/games.json`: descriptions, official rule references, lessons, examples, trial/quiz keys and versions.
- `config/study.json`: researcher details, approval gates, fixed 90-second break and protocol settings.
- `pilot/storage.py`: SQLite transactions, balanced random assignment, capability-based resume, incremental saving, withdrawal and duplicate prevention.
- `pilot/content.py`: material loading, scoring, page sequence and questionnaire URL construction.
- `pilot/analysis.py`: diagnostics, normalized CSV export and optional external-data joining.
- `assets/`: product renderings, selected official rulebook diagram captures and archived original schematics (not displayed).
- `research/`: reproducible material builders and source notes; downloaded reference PDFs/photos are excluded from Git.
- `tests/`: storage, scoring, privacy, validation, handoff and full Streamlit-flow tests.

SQLite is the primary local store. Every successful page submission saves responses, timing and the next step in a single transaction. Quiz answers and correctness are saved at item level. Answers are revealed only after both game activities and the final website submission. No response is emailed. Database files, exports and secrets are excluded from Git.

## GitHub and Streamlit

Repository: https://github.com/DramondHuangZJ/Streamlit_Demo/tree/pilot-study

The pilot uses branch **`pilot-study`**, entrypoint **`app.py`**. The existing demo stays on `main`. After each completed code update: verify, commit and push the pilot branch. Streamlit follows the branch selected for that deployment.

For a separate Cloud preview: create an app with repository `DramondHuangZJ/Streamlit_Demo`, branch `pilot-study`, main file `app.py`, Python 3.12 and `PILOT_MODE="preview"`. Do not replace the existing demo unless desired.

**Real data collection:** Streamlit Community Cloud does not guarantee local-file persistence. Its local SQLite file is suitable for expendable preview data, not durable participant records. Use approved persistent hosting with a private SQLite volume and tested backups, or implement an approved external database before online recruitment. Do not put the database in GitHub. Collection requires `PILOT_MODE=collection`, both approval environment flags, complete researcher fields and approved materials/translation/prices/external screening. Those switches are administrative attestations, not proof of ethics approval or eligibility.

## Validation and remaining review

```sh
.venv/bin/python -m pytest -q
```

See [verification evidence](docs/VERIFICATION.md), [material provenance](docs/MATERIALS.md) and [the recruitment checklist](docs/RESEARCHER_CHECKLIST.md). This pilot provides stimulus-validation and usability evidence; it does not test the final dissertation hypotheses or establish equivalence from a non-significant difference.
