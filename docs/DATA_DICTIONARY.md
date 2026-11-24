# Data dictionary

All timestamps are UTC ISO 8601 strings (`...Z`). Times are elapsed wall-clock seconds, including inactive tabs. All IDs are generated random codes. No name, email, Prolific ID, IP address, user agent, questionnaire rating or demographic answer is stored by this website. No email is sent.

| Table | Fields and interpretation |
| --- | --- |
| `participants` | `participant_id`: `P-` plus 16 random hex characters, primary key; `resume_hash`: SHA-256 of a 256-bit random bearer capability, never exported; `started_at`, `completed_at`: website start/finalization; `status`: `in_progress`, `completed` or `withdrawn`; `is_test`: 1 for preview, 0 for collection; `language`: `en`/`zh`, cleared on withdrawal; `page_index`: current zero-based stage; `page_entered_at`: current stage entry time; `app_version`, `protocol_version`: version identifiers. |
| `assignments` | `participant_id`; `order_code`: `dragon_castle>azul` or `azul>dragon_castle`; `first_game`, `second_game`; `assigned_at`; `algorithm`: `balanced-random-tie-v1`, or `test-forced` only for explicit test records. The least-used order is selected; equal counts are broken randomly. Assignment is transactional and separate for preview/collection populations. |
| `page_timings` | `participant_id`, `page_id`: unique per saved stage; `entered_at`, `exited_at`, `duration_seconds`. A page submit saves timing and next stage together. Refresh does not restart timing. |
| `trial_responses` | `participant_id`, `game_id`, `item_code`: unique key; `response`: option ID string `0`, `1` or `2`; `correct`: 0/1; `rule_ref`: official rule section/printed page; `recorded_at`. Three items per game (`D_T1`–`D_T3` / `A_T1`–`A_T3`). |
| `comprehension_responses` | Same response fields; five items per game (`D_Q1`–`D_Q5` / `A_Q1`–`A_Q5`). Exact prompts, labelled options and answer key are in `config/games.json`. |
| `game_sessions` | `participant_id`, `game_id`: unique key; `game_position`: 1/2; `stimulus_version`, `rules_version`: versions at session creation; `quiz_accuracy`: correct/5; `trial_accuracy`: correct/3. Scores stay missing until the relevant task is saved. |
| `survey_handoffs` | `participant_id`, `game_id`: unique key; `generated_at`: handoff prepared, not an observed click; `returned_at`: continuation button time; `confirmation_method`: `participant_reported` or `preview_no_survey`; `configured`: whether a link was configured; `questionnaire_version`: researcher-supplied external version, default `external-unconfigured`. No survey response or provider submission proof is received. |
| `events` | `event_id`: sequence key; `participant_id`; `event_type`: `start` or `filler`; `recorded_at`; `details`: JSON recording external screening boundary/test flag or the three neutral shape counts. |

`page_id` order: product, learn, trial, quiz and handoff for the first assigned game; filler; the same five stages for the second game; finish; complete. The final complete page is an acknowledgement and has no next-submit timing record. There are twelve saved transitions in a completed website session.

On withdrawal, task responses, timings, game sessions, handoffs, assignment and events are deleted. The anonymous participants row remains only to count withdrawals; the resume capability is invalidated. Exports omit resume hashes and default to completed non-test sessions. Dashboard counts may include in-progress/withdrawn administrative rows; these are not valid questionnaire completions.

## Versions

- App: `pilot-1.1.0`.
- Protocol: `external-survey-per-game-1`.
- Stimulus: `stimuli-3-ai-components-draft`.
- Rules: `rules-1-source-checked`.
- External questionnaire: not configured. Set `PILOT_QUESTIONNAIRE_VERSION` when the actual instrument is published.

If the configured stimulus/rule version differs from a session's assigned version, the app stops that session rather than silently mixing material versions. Do not publish material changes during live recruitment without a documented protocol/version decision.

## CSV bundle

The ZIP includes one CSV for each table and `manifest.json`, even for empty tables (headers retained). CSVs are UTF-8 with BOM and have no artificial spreadsheet index. Join website task tables by `participant_id`; join game-level external evaluations using **both** `participant_id` and `game_id`. Use `game_position`/`order_code` as design factors. Never treat the two game rows as independent participants.

## External scale scoring

The site serves none of these items. The optional local merge supports the 7 November revised item codes in an external export:

| Score | Required raw fields | Direction |
| --- | --- | --- |
| `CF_score` | CF1–CF6 | Reverse CF3–CF6 as 8−raw; higher = greater fluency |
| `PN_score` | PN1–PN3 | Higher = greater novelty |
| `PI_score` | PI1–PI5 | Higher = greater purchase intention; Spears–Singh endpoints |
| `PCD_score` | PCD1–PCD5 | Higher = greater perceived cultural distance |
| `PQ_score` | PQ1–PQ5 | Higher = greater perceived quality |
| `GC_score` | GC1–GC4 | Higher = greater complexity |
| `VIS_score` | VIS1 | Higher = greater visual attractiveness |
| `THEME_score` | THEME1 | Higher = greater theme liking |
| `PRICE_score` | PRICE1 | Reverse as 8−raw; higher = greater price acceptability |

Scale means require every item; incomplete scales remain missing. Raw values are preserved. Optional `culture_recognition` and `prior_exposure` remain explicit external fields, not inferred website responses. Baseline familiarity, frequency/knowledge, demographics and usability should be analyzed from the external platform's own properly coded export.

## Interpretation

Task diagnostics are stimulus-validation and website-usability evidence. Dashboard paired differences are Azul minus Dragon Castle with 95% Student-t confidence intervals when at least two complete pairs exist. Accuracy is bounded 0–1; small samples need cautious interpretation. The proposed practical accuracy bound is ±0.10, not a validated/preregistered equivalence criterion. Proposed bounds for seven-point ancillary ratings are ±0.5 scale points, requiring substantive researcher approval before recruitment. No p-value, automatic exclusion, deletion or declaration of equivalence is implemented. Cultural distance, fluency, novelty and intention are absent until external data are joined.
