# FEEDWISE Camera + Protein Prototype

## Run in VS Code (Windows)
1. Install Python 3.10+.
2. Open this folder in VS Code and choose Terminal → New Terminal.
3. Run:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   streamlit run app.py
   ```
   If activation is blocked, use Command Prompt and `.venv\Scripts\activate.bat`.
4. Open the local URL printed in the terminal, usually http://localhost:8501.

## Deploy
Upload `app.py`, `requirements.txt`, and `README.md` to GitHub. On https://share.streamlit.io/ create an app using your repository, branch `main`, and main file path `app.py`.

## Limitations
The camera score is a non-diagnostic colour/texture heuristic, not a trained fungal classifier. It cannot identify species or mycotoxins. Protein must be entered from a suitable analysis; the target must come from an applicable feeding standard or qualified nutritionist. Do not use this prototype alone to decide feed safety.
