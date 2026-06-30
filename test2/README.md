# Local Math Agent (FastAPI + TypeScript)

This subproject replaces the Tkinter UI with a local web app.

## Run

Backend:

```bash
cd /Users/idanvaysman/NeurosymbolicAI_MathTool
./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir test2/backend
```

Frontend:

```bash
cd /Users/idanvaysman/NeurosymbolicAI_MathTool/test2/frontend
npm install
npm run dev -- --host 127.0.0.1
```

Open:
- Frontend: http://127.0.0.1:5173
- API health: http://127.0.0.1:8000/api/health
