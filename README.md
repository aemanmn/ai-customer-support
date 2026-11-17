# Knowledge base setup

The knowledge base is stored as Markdown sections in `knowledge_base/`. Apply the
Supabase migrations to the linked project, then seed the entries:

```powershell
uv run python scripts/load_database.py
uv run python scripts/seed_knowledge_base.py
```

The migration command requires the Supabase CLI and a linked project. The seed
script requires `DATABASE_URL` in the environment or project `.env` file. It
updates matching `(section, title)` rows, so rerunning it replaces database edits
for entries that still exist in the Markdown files.

## Pipeline playground

Use [playground/pipeline_playground.py](playground/pipeline_playground.py) to run
a customer question through the classifier, knowledge-base agent, and Python
decision rules without sending an email or connecting to Gmail or the database.
The playground reads the local Markdown files in `knowledge_base/`.

1. Select the project's `.venv` Python interpreter in VS Code.
2. Edit `QUESTION` in the playground file, or run it with
   `uv run python playground/pipeline_playground.py`.
3. In a Jupyter Interactive Window, run the file's cells, then execute:

   ```python
   trace = run_pipeline(QUESTION)
   print_trace(trace)
   ```

The output includes the structured `Classification`, `AgentReply` (when drafting
is reached), and final `Decision` models. The selected model provider's API key
must be configured in `.env` (the current model defaults use `GROQ_API_KEY`).
Google credentials and `DATABASE_URL` are not needed for this playground.