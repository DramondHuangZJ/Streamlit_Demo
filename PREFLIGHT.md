# Pilot preflight

Reviewed 24 November 2026. No application code has been written at this stage.

## Scope

Build a Streamlit stimulus-validation pilot for Dragon Castle and Azul. Adults primarily socialized in Chinese culture evaluate both games in a randomized, counterbalanced order. No AI manipulation is included. The pilot evaluates stimulus distance, culture recognition, comprehension, nuisance differences, questionnaire usability, procedure and website operation. It does not test the dissertation's final causal hypotheses.

## Document authority

Read-only project references inspected:

- `deliverables/Expanded_PhD_Literature_Review_Model_Methodology_and_Questionnaire.docx` (21 November file timestamp).
- `deliverables/Board_Game_Participant_Questionnaire_Revised_Ana_Maria.docx` (7 November).
- `deliverables/Board_Game_Item_Source_Register_Revised_Ana_Maria.docx` (7 November).
- `deliverables/Response_to_Professor_Ana_Maria_Questionnaire_Comments.docx`.
- `output/questionnaire/QUESTIONNAIRE_UPDATE_NOTES.md` (older material).

The expanded methodology contains a stale appendix and measurement paragraph: Dodds willingness-to-buy, a single perceived-distance item, shortened experience measures and a single learning-effort check. These conflict with the dedicated supervisor-revised files. Per the user's explicit precedence instruction, the supervisor-revised questionnaire and source register govern item wording and scale composition. The current chat governs the two named-game pilot, rather than the later multi-stimulus AI main experiment. No source document is modified.

## Questionnaire requirements found

Before exposure: consent and adult eligibility; childhood residence ages 6–18 including tied places; two familiarity/knowledge endpoints for each named culture; board-game frequency; all five subjective board-game knowledge items; two AI-use frequency items; all five subjective AI-knowledge items. Preserve pre-exposure timing despite the initial website outline placing some background measures at the end.

After each game: six CF pairs, three PN items, five Spears–Singh PI pairs, five Sharma–Wu–Su PCD items, five PQ pairs, four Guo–Ren–Ma GC items, and one item each for visual attractiveness, theme appeal and price acceptability. Administer the explicit attention check once after game two.

Reverse directions must be documented: CF3–CF6, BGK2/BGK4/BGK5, AIK2/AIK4/AIK5 and PRICE1. Retain raw response values and calculate separately labelled recoded scores. Seven response positions must retain the revised endpoints. Behavioural frequency must not be averaged with subjective knowledge.

Culture recognition, recognition confidence, language ability, current residence, prior exposure, product-page professionalism, usability feedback, demographics and objective game quizzes require pilot-specific additions. They must be labelled as study-specific items, never presented as approved published scales. The revised register explicitly replaced the former single learning-effort measure with the full four-item complexity scale; any separate learning-effort diagnostic must remain a proposed pilot-specific item.

## Materials located online

- Dragon Castle official publisher page: https://horribleguild.com/us/product/dragon-castle/
- English rulebook linked by that publisher: https://www.dropbox.com/scl/fi/obj1v4l91tdpu998cmwky/DC_Rulebook-EN_v02_Web.pdf?rlkey=9mz7tkbxgl9vyx4f9spbgmqnu&dl=0
- Alternative publisher/distributor rulebook: https://cmon-files.s3.amazonaws.com/pdf/assets_item/resource/112/DRC001_Rulebook_website.pdf
- Original Azul official English rules: https://cdn.svc.asmodee.net/production-unboxnowcom/uploads/2022/04/en-azul-rules.pdf
- Azul publisher/distributor setting description: https://www.asmodee.co.uk/collections/azul

Accessed 24 November 2026. Rule details, answer keys and page references still require item-level checking before implementation. Do not use Azul expansions or alternate scoring boards as the base game. Official product pictures are discoverable, but public availability is not evidence of reuse permission. Use original schematic examples or clearly identified research placeholders where rights are unconfirmed.

## Pending language decision

The inspected participant questionnaire is English. No approved Chinese version was identified in the priority files. Ask whether to build English, Simplified Chinese (translation pending review), or bilingual, and whether a newer approved version exists. Do not silently call a generated translation approved.

## Hosting and recruitment

Use persistent local SQLite as requested. Streamlit Community Cloud does not guarantee persistence of local files: https://docs.streamlit.io/develop/concepts/connections/connecting-to-data . Therefore, a public Community Cloud preview cannot be described as reliable real-participant storage using only its local SQLite file. Before recruitment, choose persistent approved hosting or a durable external store. Never commit participant records to GitHub.

Institutional participant-information wording, ethics approval status/reference, researcher contacts, retention/withdrawal policy, translation review, approved prices and practical equivalence bounds require confirmation before recruitment. These do not require the user to provide game rulebooks or commercial pictures now.

## Final verification target

The application deliverable remains outstanding. Completion requires the entire 13-stage participant journey; incremental versioned SQLite tables; protected researcher analysis and exports; a data dictionary; placeholder/recruitment checklist; critical-logic tests; full test completions in both orders; desktop and narrow-width visual inspection; record/export reconciliation; exact launch instructions; screenshots or a visual summary; and GitHub publication of completed code updates. Passing a demo test does not satisfy these pilot requirements.
