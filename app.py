import random
from collections import Counter
from datetime import datetime

import pandas as pd
import streamlit as st


TILE_SETS = {
    "Dots": ["1筒", "2筒", "3筒", "4筒", "5筒", "6筒", "7筒", "8筒", "9筒"],
    "Bamboo": ["1条", "2条", "3条", "4条", "5条", "6条", "7条", "8条", "9条"],
    "Characters": ["一万", "二万", "三万", "四万", "五万", "六万", "七万", "八万", "九万"],
    "Honors": ["东", "南", "西", "北", "中", "发", "白"],
}

TILE_SYMBOLS = {
    "1筒": "🀙", "2筒": "🀚", "3筒": "🀛", "4筒": "🀜", "5筒": "🀝", "6筒": "🀞", "7筒": "🀟", "8筒": "🀠", "9筒": "🀡",
    "1条": "🀐", "2条": "🀑", "3条": "🀒", "4条": "🀓", "5条": "🀔", "6条": "🀕", "7条": "🀖", "8条": "🀗", "9条": "🀘",
    "一万": "🀇", "二万": "🀈", "三万": "🀉", "四万": "🀊", "五万": "🀋", "六万": "🀌", "七万": "🀍", "八万": "🀎", "九万": "🀏",
    "东": "🀀", "南": "🀁", "西": "🀂", "北": "🀃", "中": "🀄", "发": "🀅", "白": "🀆",
}

RATING_ITEMS = {
    "cognitive_fluency": [
        "The information about this game was easy to understand.",
        "I found it easy to understand the rules and gameplay.",
        "I quickly understood what players are supposed to do.",
    ],
    "perceived_novelty": [
        "This game feels novel to me.",
        "The cultural setting of this game makes it feel distinctive.",
        "This game offers a fresh gaming experience.",
    ],
    "purchase_intention": [
        "I would consider buying this game.",
        "If I had the opportunity, I would be willing to purchase this game.",
        "I would recommend this game to friends who enjoy board games.",
    ],
}


def build_wall():
    wall = []
    for tiles in TILE_SETS.values():
        for tile in tiles:
            wall.extend([tile] * 4)
    random.shuffle(wall)
    return wall


def init_state():
    if "wall" not in st.session_state:
        random.seed()
        wall = build_wall()
        hand = sorted([wall.pop() for _ in range(13)], key=tile_sort_key)
        st.session_state.wall = wall
        st.session_state.hand = hand
        st.session_state.discards = []
        st.session_state.turns = 0
        st.session_state.drawn = None
        st.session_state.quiz_submitted = False
        st.session_state.quiz_score = None
        st.session_state.condition = random.choice(["AI support", "Static rule guide"])


def tile_sort_key(tile):
    for suit_index, tiles in enumerate(TILE_SETS.values()):
        if tile in tiles:
            return suit_index, tiles.index(tile)
    return 99, tile


def tile_badge(tile, selected=False):
    selected_class = " selected" if selected else ""
    return f"<span class='tile{selected_class}'><span>{TILE_SYMBOLS[tile]}</span><small>{tile}</small></span>"


def score_hand(hand):
    counts = Counter(hand)
    pairs = sum(1 for count in counts.values() if count >= 2)
    triples = sum(1 for count in counts.values() if count >= 3)
    sequences = 0
    for tiles in list(TILE_SETS.values())[:3]:
        for i in range(7):
            sequences += min(counts[tiles[i]], counts[tiles[i + 1]], counts[tiles[i + 2]])
    set_like = triples + sequences
    return pairs, set_like


def hand_feedback(hand):
    pairs, set_like = score_hand(hand)
    if pairs >= 1 and set_like >= 4:
        return "Excellent. Your hand already resembles a winning Mahjong structure: four groups and one pair."
    if pairs >= 1 and set_like >= 2:
        return "Promising. You have a pair and some group structure. Try discarding isolated tiles."
    if pairs >= 1:
        return "You have a pair. Now look for runs, such as 3-4-5 in the same suit, or three identical tiles."
    return "Look for a pair first. A pair is two identical tiles and is usually needed in a complete hand."


def draw_tile():
    if st.session_state.drawn is None and st.session_state.wall:
        st.session_state.drawn = st.session_state.wall.pop()
        st.session_state.hand.append(st.session_state.drawn)
        st.session_state.hand = sorted(st.session_state.hand, key=tile_sort_key)


def discard_tile(tile):
    if tile in st.session_state.hand:
        st.session_state.hand.remove(tile)
        st.session_state.discards.append(tile)
        st.session_state.turns += 1
        st.session_state.drawn = None


def likert(label, key):
    return st.slider(label, 1, 7, 4, key=key)


def page_style():
    st.markdown(
        """
        <style>
        .stApp { background: #fbfaf7; }
        .hero {
            border-bottom: 1px solid #ddd5c7;
            padding: 1.2rem 0 1.1rem;
            margin-bottom: 1rem;
        }
        .hero h1 { font-size: 2.1rem; margin: 0 0 .35rem; color: #1f1b18; letter-spacing: 0; }
        .hero p { max-width: 850px; font-size: 1.03rem; color: #4e4840; margin: 0; }
        .metric-strip {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: .6rem;
            margin: 1rem 0;
        }
        .metric {
            border: 1px solid #ddd5c7;
            background: #fffdf8;
            border-radius: 8px;
            padding: .7rem .8rem;
        }
        .metric small { display: block; color: #766c60; }
        .metric strong { color: #221f1b; }
        .tile-row { display: flex; gap: .42rem; flex-wrap: wrap; margin: .7rem 0 1rem; }
        .tile {
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 58px;
            height: 76px;
            border: 1px solid #d1c7b8;
            background: linear-gradient(180deg, #fffefb 0%, #f0eadf 100%);
            box-shadow: 0 2px 0 #c5b9a8;
            border-radius: 7px;
            color: #201c18;
            margin-bottom: .18rem;
        }
        .tile span { font-size: 2.2rem; line-height: 1; }
        .tile small { font-size: .72rem; color: #685f55; margin-top: .16rem; }
        .selected { border-color: #b83232; box-shadow: 0 0 0 2px rgba(184,50,50,.18), 0 2px 0 #bda894; }
        .note {
            border-left: 4px solid #b83232;
            background: #fff8ee;
            padding: .75rem .9rem;
            margin: .7rem 0 1rem;
        }
        .rule-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .8rem;
        }
        .rule {
            border: 1px solid #ded7cc;
            background: #fffdf8;
            border-radius: 8px;
            padding: .85rem;
            min-height: 132px;
        }
        @media (max-width: 760px) {
            .metric-strip, .rule-grid { grid-template-columns: 1fr; }
            .tile { width: 47px; height: 66px; }
            .tile span { font-size: 1.85rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_product_page():
    st.markdown(
        """
        <div class="hero">
          <h1>Chinese Mahjong Participant Demo</h1>
          <p>A research prototype where participants learn a culturally rooted board game, complete a short interaction task, and report understanding, novelty, and purchase intention.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="metric-strip">
          <div class="metric"><small>Source culture</small><strong>Chinese</strong></div>
          <div class="metric"><small>Players</small><strong>4</strong></div>
          <div class="metric"><small>Learning time</small><strong>5-8 min demo</strong></div>
          <div class="metric"><small>Research role</small><strong>High/low distance stimulus candidate</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.subheader("Game Background")
    st.write(
        "Mahjong is a tile-based tabletop game associated with Chinese social life, family gatherings, symbolic suits, winds, dragons, and patterned hand-building. "
        "In this demo, participants do not need to master full tournament rules. They only need to learn the basic goal: improve a hand by drawing and discarding tiles while looking for useful groups."
    )
    st.subheader("What Participants Experience")
    st.write(
        "Participants see a standardized product-style page, learn the simplified rules, try a short turn-based task, complete objective comprehension questions, and then answer 7-point scale items."
    )


def render_learning_page():
    st.subheader("Learn the Simplified Rules")
    st.markdown(
        """
        <div class="rule-grid">
          <div class="rule"><strong>Goal</strong><br>Build a hand that resembles four groups plus one pair. A group can be three identical tiles or a sequence in one suit.</div>
          <div class="rule"><strong>Turn</strong><br>Draw one tile, inspect your hand, and discard one tile. Keep tiles that help complete pairs, triples, or sequences.</div>
          <div class="rule"><strong>Culture</strong><br>Winds, dragons, bamboo, dots, and characters are culturally meaningful signs. They make the game distinctive but may also require explanation.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.condition == "AI support":
        st.markdown(
            """
            <div class="note">
            <strong>AI-style support:</strong> Focus on pattern recognition. Keep pairs, three-of-a-kind, and near sequences such as 3-4 or 6-7. If a tile is isolated and does not connect to its neighbors, it is often a good discard.
            </div>
            """,
            unsafe_allow_html=True,
        )
        question = st.text_input("Ask the learning assistant a Mahjong question", placeholder="Example: Why are wind tiles important?")
        if question:
            st.info("Demo assistant: In this simplified task, wind tiles are honor tiles. They cannot form number sequences, so they are most useful as pairs or triples.")
    else:
        st.markdown(
            """
            <div class="note">
            <strong>Static rule guide:</strong> The same basic information is provided as written text. No interactive explanation is available in this condition.
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_game_page():
    st.subheader("Trial Play Task")
    st.write("Draw a tile, then discard one tile. Try to keep pairs and connected number tiles.")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Turns completed", st.session_state.turns)
    col_b.metric("Tiles left in wall", len(st.session_state.wall))
    col_c.metric("Learning condition", st.session_state.condition)

    if st.button("Draw tile", type="primary", disabled=st.session_state.drawn is not None):
        draw_tile()

    if st.session_state.drawn:
        st.success(f"You drew {st.session_state.drawn}. Choose one tile to discard.")

    st.markdown("<div class='tile-row'>" + "".join(tile_badge(tile, tile == st.session_state.drawn) for tile in st.session_state.hand) + "</div>", unsafe_allow_html=True)
    discard = st.selectbox("Choose a tile to discard", [""] + st.session_state.hand)
    if st.button("Discard selected tile", disabled=not discard):
        discard_tile(discard)
        st.rerun()

    st.info(hand_feedback(st.session_state.hand))
    if st.session_state.discards:
        st.caption("Discarded tiles")
        st.markdown("<div class='tile-row'>" + "".join(tile_badge(tile) for tile in st.session_state.discards[-12:]) + "</div>", unsafe_allow_html=True)


def render_quiz_page():
    st.subheader("Comprehension Check")
    with st.form("quiz_form"):
        q1 = st.radio("What is the main goal in the simplified demo?", ["Collect the most wind tiles", "Build groups and one pair", "Discard all tiles first"], index=None)
        q2 = st.radio("Which set is a valid sequence?", ["3筒, 4筒, 5筒", "东, 南, 西", "2条, 2筒, 2万"], index=None)
        q3 = st.radio("What should you usually do with an isolated tile?", ["Always keep it", "Consider discarding it", "Use it as money"], index=None)
        submitted = st.form_submit_button("Submit quiz")
    if submitted:
        score = int(q1 == "Build groups and one pair") + int(q2 == "3筒, 4筒, 5筒") + int(q3 == "Consider discarding it")
        st.session_state.quiz_score = score
        st.session_state.quiz_submitted = True
    if st.session_state.quiz_submitted:
        st.success(f"Quiz score: {st.session_state.quiz_score}/3")


def render_questionnaire():
    st.subheader("Participant Ratings")
    st.write("For each statement, use 1 = strongly disagree and 7 = strongly agree.")
    ratings = {}
    with st.form("ratings_form"):
        for construct, items in RATING_ITEMS.items():
            st.markdown(f"**{construct.replace('_', ' ').title()}**")
            for index, item in enumerate(items, start=1):
                ratings[f"{construct}_{index}"] = likert(item, f"{construct}_{index}")
        submitted = st.form_submit_button("Save response")

    if submitted:
        row = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "stimulus": "Chinese Mahjong demo",
            "condition": st.session_state.condition,
            "turns_completed": st.session_state.turns,
            "quiz_score": st.session_state.quiz_score,
            **ratings,
        }
        st.session_state.response = row
        st.success("Response saved for this demo session.")

    if "response" in st.session_state:
        df = pd.DataFrame([st.session_state.response])
        st.download_button(
            "Download demo response CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="mahjong_demo_response.csv",
            mime="text/csv",
        )


def main():
    st.set_page_config(page_title="Mahjong Research Demo", page_icon="🀄", layout="wide")
    init_state()
    page_style()

    with st.sidebar:
        st.title("Study Demo")
        st.caption("Prototype participant material")
        st.session_state.condition = st.radio("Learning condition", ["AI support", "Static rule guide"], index=0 if st.session_state.condition == "AI support" else 1)
        if st.button("Reset participant session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    tab_intro, tab_learn, tab_play, tab_quiz, tab_survey = st.tabs(
        ["Product Page", "Learn", "Trial Play", "Quiz", "Ratings"]
    )
    with tab_intro:
        render_product_page()
    with tab_learn:
        render_learning_page()
    with tab_play:
        render_game_page()
    with tab_quiz:
        render_quiz_page()
    with tab_survey:
        render_questionnaire()


if __name__ == "__main__":
    main()
