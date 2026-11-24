# External questionnaire handoff

The researcher confirmed: questionnaires are external, after each game; objective comprehension quizzes remain on the website. The site therefore contains no research-scale or demographic questionnaire, no on-site consent form and no on-site eligibility questions.

## Recommended study sequence

1. External platform: study information, voluntary informed consent, age/language/cultural eligibility, prior-game exposure and all approved pre-exposure covariates. Declined consent, under-18 or ineligible participants must end there and must not be sent to the game website.
2. Website: generated anonymous matching code and stable counterbalanced assignment, first game's product/lesson/trial/quiz.
3. External first-game questionnaire: current game's ratings; then return to the website.
4. Website: neutral 90-second activity, second game's product/lesson/trial/quiz.
5. External second-game questionnaire: second-game ratings, final background/usability items and attention check; then return.
6. Website: finalization and debrief. External platform manages payment and Prolific completion codes if used.

The supervisor-revised questionnaire places cultural familiarity and board-game/AI frequency/knowledge before exposure. Preserve that timing in the external survey. Do not move pre-treatment items to the end merely because the website no longer serves them. The two culture-familiarity blocks require explicitly named cultures; this may prime later source-culture recognition. Treat recognition as recall of signalled culture, not an unaided discovery task.

## Links and matching fields

Configure HTTPS `PILOT_SURVEY_URL_1` and `_2`. The site appends URL-encoded:

| Field | Meaning |
| --- | --- |
| `participant_id` | Generated `P-` matching code, not a name/email/Prolific identifier |
| `game_id` | `dragon_castle` or `azul` |
| `game_position` | 1 or 2 |
| `assigned_order` | Comma-separated fixed game IDs |
| `language` | `en` or `zh` |
| `return_url` | Website URL with an opaque session resume capability |
| `stimulus_version` | Actual material version assigned at session creation |
| `rules_version` | Rule-content version |
| `protocol_version` | External-survey protocol version |

Configure the survey to save these as embedded data. Return to the exact `return_url` without replacing its resume parameter. The survey can show this as a final link or use its supported redirect mechanism. The website tab can also remain open while a survey opens in another tab.

Returning lands on the current handoff step. The participant presses **I completed the questionnaire — continue**. The site records `participant_reported`; it does not receive or verify the provider's submission event. Reconcile this against the actual external export. Do not describe a mere visit, link generation or button click as confirmed questionnaire completion. A signed provider callback would need a provider-specific integration that is not configured in this release.

No questionnaire-provider URL has been supplied. Preview bypass is consequently deliberate and restricted to records marked `is_test=1`. The website records link generation, not an observed link click. Its own completion means tasks and reported returns are complete, not that the participant is entitled to payment.

## Participant identity and consent boundary

A survey platform may use its own participant ID or a Prolific ID for recruitment/payment. Keep that mapping on the external platform; do not put names/emails/Prolific IDs into this website's URL. The website ignores unsolicited query parameters other than `resume` and the researcher route. It cannot enforce consent or eligibility on another system; the external platform's branching, direct-link exposure and duplicate-participation rules must be tested before recruitment. The researcher gate `external_screening_approved` attests that this has been done.

Anyone possessing an active resume URL can access that session. Do not publish a real participant's URL, use it in a screenshot, or share it in a recruitment post. Store hashes of resume values in SQLite; hashes are omitted from exports. Set the correct public HTTPS base URL in production.

## Joining external results

Create one de-identified CSV row per `participant_id,game_id`. Optional supported columns: `CF1`–`CF6`, `PN1`–`PN3`, `PI1`–`PI5`, `PCD1`–`PCD5`, `PQ1`–`PQ5`, `GC1`–`GC4`, `VIS1`, `THEME1`, `PRICE1`, `culture_recognition`, `prior_exposure`. Numeric scale responses must be integers 1–7 or missing. Unknown columns and duplicate game rows are rejected to reduce accidental identifier inclusion.

The merge keeps completed website records, excludes test records unless requested, preserves raw values and adds complete-case scale means. Reverse-code CF3–CF6 and PRICE1 as `8 − raw`. If you score the baseline knowledge blocks externally, reverse BGK2/BGK4/BGK5 and AIK2/AIK4/AIK5. Do not combine behavioural frequency and subjective knowledge.

## Sources

- Prolific study hosting: https://researcher-help.prolific.com/en/articles/445178-what-survey-experimental-software-is-compatible-with-prolific
- Prolific data collection, including available collection modes: https://researcher-help.prolific.com/en/articles/445127-data-collection
- Streamlit storage persistence limitation: https://docs.streamlit.io/develop/concepts/connections/connecting-to-data
