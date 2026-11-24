# Game material sources and visual provenance

Sources were accessed 24–25 November 2026. No full copyrighted rulebook or original publisher photograph is included in the public repository. The researcher requested real-product imagery and selected rulebook captures; this release uses labelled AI product renderings, small official diagram captures and supplemental original task schematics.

| Game/material | Primary source | Use |
| --- | --- | --- |
| Dragon Castle product facts and appearance | https://horribleguild.com/us/product/dragon-castle/ | Theme, components, 45-minute playtime; publisher's current 1–4-player listing includes a solo mode. The pilot uses the multiplayer beginner setup (2–4), not its solo opponent. |
| Dragon Castle product reference | https://horribleguild.com/us/wp-content/uploads/2021/07/DC_WEB_Content-1024x562.jpg | Visual reference for generated rendering; not redistributed as a standalone asset. |
| Dragon Castle tabletop reference | https://horribleguild.com/us/wp-content/uploads/2021/07/DC_WEB_Img06.jpg | Visual reference for actual ivory rectangular tiles and symbols. |
| Dragon Castle official English rules | https://www.dropbox.com/scl/fi/obj1v4l91tdpu998cmwky/DC_Rulebook-EN_v02_Web.pdf?rlkey=9mz7tkbxgl9vyx4f9spbgmqnu&dl=0 | 20-page publisher-linked edition; printed/PDF pp.2–3 setup/components, p.5 actions, p.6 placement/consolidation, p.7 shrines, p.9 countdown/final round. Beginner setup without Spirit/Dragon cards is explicitly supported on p.3. |
| Azul original product facts and appearance | https://www.nextmove-games.com/de/azul/azul-game/ | Original Azul, 2–4 players, 30–45 minutes; components. Do not substitute a sequel or expansion. |
| Azul product reference | https://cdn.svc.asmodee.net/production-nextmove/uploads/sites/5/2024/04/Azul_comp_slider1.jpg | Visual reference for generated rendering; not redistributed as a standalone asset. |
| Azul setting | https://www.asmodee.co.uk/collections/azul | Portuguese azulejo/Royal Palace of Évora setting. |
| Azul official English rules | https://cdn.svc.asmodee.net/production-unboxnowcom/uploads/2022/04/en-azul-rules.pdf | Two wide PDF spreads containing several printed pages: printed pp.2–4 on PDF page 1; printed pp.5–6 on PDF page 2. Original colored-wall rules, not gray-wall variant or special boards. |

## Assets used by participants

| Asset | Type and status |
| --- | --- |
| `dragon_castle_product_v1.png` | Built-in ImageGen rendering based on two official photographs. Real-product appearance reference; generated details need researcher review. |
| `azul_product_v1.png` | Built-in ImageGen rendering based on official product photograph. Same neutral surface, 3:2 frame, camera treatment and intended visual salience. Generated markings need review. |
| `dragon_rule_tiles.png` | Selected official rulebook p.6 tile-type figure. |
| `dragon_rule_groups.png` | Selected official rulebook p.6 group-adjacency figure. |
| `azul_rule_board.png` | Selected official rulebook printed p.2 board detail (PDF spread 1). |
| `azul_rule_tiling.png` | Selected official rulebook printed p.4 wall-tiling figure (PDF spread 1). |
| `*_example1.svg`, `*_example2.svg` | Original generic teaching diagrams for exact simplified scenarios, supplemental to real-product imagery. |
| `*_hero.svg` | Earlier abstract assets retained for history; no longer referenced by product pages. |

AI renderings are not evidence of rules, precise component counts or commercial product quality. No publisher endorsement is claimed. Permission/licence status for public participant use of the official figure excerpts remains part of the recruitment review. The user specifically requested these captures; that request does not establish a publisher licence.

The figure extraction script `research/capture_rule_figures.py` renders selected rectangles from locally acquired PDFs and excludes rulebook prose. Inspect every capture after regenerating. `research/build_materials.py` generates configuration and original schematic diagrams. Do not regenerate or change stimuli during active recruitment without a documented version change.

## Matched presentation audit

Each game has six rule sections, two official diagram captures, two worked original examples, two FAQ entries, three trial decisions with three choices each and five comprehension questions with three choices each. English lesson body word counts are 261 (Dragon Castle) and 269 (Azul), excluding headings/examples/FAQ. Both use the same page structure and image dimensions. Reading level, Chinese comprehension and actual learning effort require human pilot evaluation; equal text length does not establish equivalence. Product facts such as real full-game duration are not falsified to make the games appear identical.

The CNY 299 displayed scenario is a matched experimental placeholder, not a verified current price. Source URLs, rule sections and keys are stored in the versioned configuration. All ten quiz items have a single documented answer; responses are retained at item level. The Dragon Castle end-condition key follows the detailed countdown rule rather than the publisher product blurb's abbreviated description.

See `IMAGE_PROMPTS.md` for generation prompts and `RESEARCHER_CHECKLIST.md` for required material reviews.
