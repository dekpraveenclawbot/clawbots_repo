# Daily arXiv → NotebookLM Audio Pipeline

This pipeline is for Praveen's daily robotics digest:
- Pull recent arXiv robotics papers
- Filter by topics:
  - humanoid
  - video models / VLA / world models
  - simulation / sim2real
  - robotic arms / manipulation
  - autonomous driving
- Create (or update) a NotebookLM notebook
- Add selected papers as sources
- Trigger an Audio Overview (podcast-style)
- Output a compact report JSON + markdown

## Current status

- ✅ arXiv fetch + filtering
- ✅ ranking + report generation
- ✅ NotebookLM API client scaffold (REST)
- ⏳ Wire and validate NotebookLM Enterprise endpoints in your project
- ⏳ Optional Telegram delivery automation

## Files

- `pipeline.py` — main runner
- `notebooklm_client.py` — API client wrapper
- `.env.example` — required env vars
- `requirements.txt`

## Setup

```bash
cd /home/praveen/.openclaw/workspace/notebooklm_pipeline
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

## Run (dry-run first)

```bash
. .venv/bin/activate
python pipeline.py --dry-run
```

## Run (real NotebookLM calls)

```bash
. .venv/bin/activate
python pipeline.py --max-papers 5
```

## Notes

NotebookLM Enterprise API needs:
- Google Cloud project + NotebookLM Enterprise enabled
- `gcloud auth application-default login` OR service account setup
- Project number + location configured in `.env`
