import time
from dataclasses import dataclass

from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

from app.ai.decide import decide
from app.ai.schemas import Decision
from evals.golden_emails import GOLDEN_EMAILS

PAUSE_SECONDS = 8      # wait between cases to stay under the free-tier token limit
RETRY_WAIT_SECONDS = 20
MAX_TRIES = 4


@dataclass
class SectionMatches(Evaluator):
    def evaluate(self, ctx: EvaluatorContext) -> bool:
        return ctx.output.section == ctx.expected_output["section"]


@dataclass
class ActionMatches(Evaluator):
    def evaluate(self, ctx: EvaluatorContext) -> bool:
        return ctx.output.action == ctx.expected_output["action"]


def run_pipeline(email: str) -> Decision:
    time.sleep(PAUSE_SECONDS)
    for attempt in range(1, MAX_TRIES + 1):
        try:
            return decide(email)
        except Exception as error:  # rate limit, connection error, bad output
            if attempt == MAX_TRIES:
                raise
            print(f"Attempt {attempt} failed ({type(error).__name__}). Retrying...")
            time.sleep(RETRY_WAIT_SECONDS)


dataset = Dataset(
    name="golden-emails",
    cases=[
        Case(
            name=case["name"],
            inputs=case["email"],
            expected_output={"section": case["section"], "action": case["action"]},
        )
                # for case in GOLDEN_EMAILS[:6]
                  for case in GOLDEN_EMAILS

    ],
    evaluators=[SectionMatches(), ActionMatches()],
)

if __name__ == "__main__":
    report = dataset.evaluate_sync(run_pipeline, max_concurrency=1)
    report.print(include_input=False, include_output=True, include_durations=False)