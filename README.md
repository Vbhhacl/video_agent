# Video Agent

This project is an AI-powered meeting assistant that can:
- download audio/video from YouTube or local files,
- transcribe speech,
- summarize the meeting,
- extract action items and decisions,
- and answer questions over the transcript using RAG.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   ```powershell
   uv pip install -r requirements.txt
   ```
3. Copy the example environment file and fill in your API keys:
   ```powershell
   copy .env.example .env
   ```
4. Run the app:
   ```powershell
   streamlit run app.py
   ```

## Security notes

- The `.env` file is ignored by Git and should never be committed.
- Use `.env.example` as the template for required variables.
