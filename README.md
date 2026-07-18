# Mahjong Streamlit Demo

This is a prototype participant-facing website for an academic experiment about cultural distance, cognitive fluency, perceived novelty, and purchase intention in board games.

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit, usually:

```text
http://localhost:8501
```

## Prototype Flow

1. Product page for Chinese Mahjong.
2. Learning stage with optional AI-style support.
3. Simplified trial play task.
4. Objective comprehension quiz.
5. Short 7-point rating questionnaire.

The game logic is simplified for research demonstration. It is not a complete implementation of competitive Mahjong.
