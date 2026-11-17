# %%
import sys
from pathlib import Path


def _find_project_root() -> Path:
    script_path = globals().get("__file__")
    start_paths = [Path(script_path).resolve().parent] if script_path else []
    start_paths.append(Path.cwd().resolve())
    for start_path in start_paths:
        for candidate in (start_path, *start_path.parents):
            if (candidate / "app" / "__init__.py").is_file():
                return candidate
    raise RuntimeError("Could not find the project root containing app/__init__.py.")


PROJECT_ROOT = _find_project_root()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ai.agent import create_support_agent, write_reply
from app.ai.decide import decide_with_trace
from app.ai.schemas import PipelineTrace
from scripts.seed_knowledge_base import parse

KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
QUESTION = "my board loses air overnight."


def _list_local_sections() -> list[str]:
    return sorted(path.stem for path in KNOWLEDGE_BASE_DIR.glob("*.md"))


def _get_local_section(section: str) -> list[dict[str, str]]:
    for path in KNOWLEDGE_BASE_DIR.glob("*.md"):
        if path.stem == section:
            return [
                {"title": title, "content": content}
                for _, title, content in parse(path)
            ]
    return []


def run_pipeline(question: str = QUESTION) -> PipelineTrace:
    """Run classification, knowledge-base drafting, and Python decision rules without email."""
    if not question.strip():
        raise ValueError("Enter a customer question before running the pipeline.")

    thread = f"Subject: Customer question\n\nCustomer:\n{question.strip()}"
    local_agent = create_support_agent(_list_local_sections, _get_local_section)
    return decide_with_trace(
        thread,
        reply_writer=lambda message, section: write_reply(
            message, section, agent=local_agent
        ),
    )


def print_trace(trace: PipelineTrace) -> None:
    print("CLASSIFICATION")
    print(trace.classification.model_dump_json(indent=2))
    print("\nAGENT REPLY")
    if trace.agent_reply is None:
        print("Skipped because Python escalated before drafting a reply.")
    else:
        print(trace.agent_reply.model_dump_json(indent=2))
    print("\nFINAL PYTHON DECISION")
    print(trace.decision.model_dump_json(indent=2))


script_path = globals().get("__file__")
if (
    __name__ == "__main__"
    and script_path
    and Path(sys.argv[0]).resolve() == Path(script_path).resolve()
):
    print_trace(run_pipeline())
