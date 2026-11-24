# Connection demo

This separate entrypoint tests local development, GitHub publishing, and Streamlit Community Cloud hosting. The existing Mahjong prototype in `app.py` is preserved.

## Local launch

Run from this repository folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run connection_demo.py
```

Open http://localhost:8501 and confirm `connection-demo-v2` appears. Click **Test the connection** twice; the count should become 2.

## Streamlit Community Cloud

Sign in at https://share.streamlit.io with the GitHub account authorized for this repository. Create an app with:

- Repository: `DramondHuangZJ/Streamlit_Demo`
- Branch: `main`
- Main file path: `connection_demo.py`
- Python: `3.12`
- Secrets: none required for this connection demo.

Deploy and check the same version and button behavior on the hosted page. Do not use `app.py` for this connection test.

## Future updates

For each completed code update: save locally, verify the change, commit the intended code files, and push to GitHub. Streamlit Community Cloud follows the deployed branch automatically.

The initial `connection-demo-v1` was observed live in Chrome and its button was tested successfully. The next update changes `DEMO_VERSION` to `connection-demo-v2` to verify automatic deployment after a local commit and GitHub push.

Hosted demo: https://appdemo-nipezfhpiwbuzdrhap6ulk.streamlit.app/

The local folder is a standalone Git checkout of the demo repository. Dissertation files outside this directory are not part of the repository. Never commit credentials, `.venv`, or participant data.
