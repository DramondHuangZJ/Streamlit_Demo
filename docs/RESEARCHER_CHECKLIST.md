# Researcher checklist before recruitment

The website is a working preview. The items below are explicit recruitment decisions or missing external configuration, not hidden completed functionality.

## Temporary content and configuration

- [ ] Provide the first- and second-position external questionnaire URLs (`PILOT_SURVEY_URL_1`, `_2`). They can use one branching instrument if the provider supports the supplied embedded fields. Configure and test the return link for each assigned game order.
- [ ] Publish an actual questionnaire version and set `PILOT_QUESTIONNAIRE_VERSION`. `external-unconfigured` is not a deployed questionnaire version.
- [ ] Insert institutional study information, researcher contact, ethics reference and retention/withdrawal wording in `config/study.json`. A completed ethics application is not evidence of granted approval.
- [ ] Review the Simplified Chinese website translation and the external questionnaire translation. English source wording remains the measurement authority; no new approved scale translation is claimed here.
- [ ] Approve or replace the two AI-generated product renderings after checking their appearance against the physical products/publisher references. They are labelled illustrations, not exact photos. Generated board markings and tile counts must not be used as rule evidence.
- [ ] Approve usage of the selected official rulebook diagram captures. Their source/printed page is documented; online availability is not itself a reuse licence. They were captured at the user's request. Full PDFs are not redistributed.
- [ ] Approve the matched CNY 299 experimental price scenario or replace it with an approved retail-price treatment. It is a placeholder, not a statement of current retail price. Keep currency, framing and salience comparable.
- [ ] Review the AI-rendered scenario images for tile identity, exact color counts, blocked long sides and the absence of unintended placed pieces. All primary component illustrations are AI renderings; official rulebook captures remain in a separate reference section.

## Research design decisions

- [ ] Confirm the focal cultural population and external eligibility rules, including language proficiency and childhood-residence handling. Do not screen solely from nationality or IP location.
- [ ] Implement consent decline and under-18 termination on the external platform before exposing participants to this website. Test these branches there. The website does not collect or verify consent/age.
- [ ] Keep cultural familiarity and board-game/AI experience before exposure as specified in the revised questionnaire. All opinion, background, culture-recognition and usability items are external.
- [ ] Verify per-game ratings occur immediately after that game's activity; prevent the survey from revealing the next game's content early.
- [ ] Decide how to reconcile participant-reported survey returns with the provider's true submission records. A callback integration would be a separate provider-specific implementation; the current generic return is not proof of questionnaire completion.
- [ ] Review all ten comprehension items, six trial decisions and bilingual distractors against the cited official rules. Do not reveal keys before the entire pilot is complete.
- [ ] Confirm that short scenario decisions provide sufficient experience for items referring to “playing” the game. This website does not implement either complete commercial game.
- [ ] Confirm recognition coding: China/East Asia for Dragon Castle, Portugal/Europe for Azul, with partial/ambiguous responses handled in a predefined way on the external platform. Explicit cultural-setting text and pre-exposure familiarity can prime recognition.
- [ ] Consider whether ethnicity, nationality, language, customs and religion are all meaningfully communicated by these stimuli. Do not invent cultural claims to force the five-item distance scale to fit.
- [ ] A two-game pilot cannot separate cultural setting from all product/mechanism differences. Validate the pair; do not claim a causal culture effect or generalize to all Asian/European games.
- [ ] Approve practical equivalence bounds and a sample-size/precision rationale. ±0.10 accuracy and ±0.5 on ancillary seven-point ratings are proposals only. Do not declare equivalence from a non-significant difference.
- [ ] Prespecify prior-exposure handling, attention-check policy, incomplete/duplicate rules and which records are test data. The site does not identify repeated people who use different browsers or new links.
- [ ] Measure observed completion times and external survey burden; replace the provisional 15–20-minute website estimate if needed.

## Hosting and operations

- [ ] Choose approved durable hosting/storage. Community Cloud local SQLite is expendable preview storage; do not recruit using it as the only record store.
- [ ] Set a strong `PILOT_ADMIN_PASSWORD` outside Git. Protect the host's database file and backups with appropriate permissions. Do not store API keys, survey credentials, response exports or participant session links in the repository.
- [ ] Set the actual HTTPS `PILOT_PUBLIC_URL`; verify the provider saves the matching fields and returns the original opaque resume URL.
- [ ] Test restore from backup and verify row counts/export joins with a complete dummy external submission in both game orders.
- [ ] Set the study approval booleans only after completing the reviews. Then set `PILOT_MODE=collection`, `PILOT_APPROVALS_CONFIRMED=true` and `PILOT_STORAGE_APPROVED=true` on the approved persistent deployment.
- [ ] Keep the public Streamlit preview in `preview` mode. Existing demo deployment on `main` is separate from this pilot on branch `pilot-study`.
