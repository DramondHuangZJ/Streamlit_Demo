# Development workflow

- This repository is the user's local Streamlit demo checkout.
- After every completed code update, verify it, commit the intended changes, and push to `origin` on the deployed branch. Report any authentication or push failure clearly.
- The connection test entrypoint is `connection_demo.py`. Preserve the separate existing prototype in `app.py` unless the user requests changes to it.
- Keep secrets, local environments, and participant data out of Git.
- Do not begin implementing the PhD board-game pilot without the user's instruction.
