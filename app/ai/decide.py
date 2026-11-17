from collections.abc import Callable

from app.ai.agent import write_reply
from app.ai.classifier import classify
from app.ai.rules import CUSTOMER_STEPS, resolve_issue
from app.ai.schemas import AgentReply, Classification, Decision, PipelineTrace


def decide_with_trace(
    thread: str,
    has_attachments: bool = False,
    *,
    classifier: Callable[[str], Classification] = classify,
    reply_writer: Callable[[str, str], AgentReply] = write_reply,
) -> PipelineTrace:
    """Run the AI steps and return their structured outputs plus Python's decision."""
    classification = classifier(thread)
    answer: AgentReply | None = None

    def escalate(reason: str, proposed_action: str | None = None) -> Decision:
        return Decision(
            action="escalate",
            section=classification.section,
            reply=classification.acknowledgement,
            reason=reason,
            proposed_action=proposed_action,
        )

    if has_attachments:
        decision = escalate("The email has attachments")
    elif classification.needs_human:
        decision = escalate(classification.reason)
    else:
        answer = reply_writer(thread, classification.section)
        if answer.action == "escalate":
            decision = escalate(answer.reasoning)
        elif not answer.enough_information:
            decision = escalate("The knowledge base does not answer this")
        elif answer.issue and (step := resolve_issue(answer.issue)) not in CUSTOMER_STEPS:
            decision = escalate(f"Next step: {step}", proposed_action=step)
        elif answer.promises_an_action:
            decision = escalate("The reply promises an action")
        else:
            decision = Decision(
                action="reply",
                section=classification.section,
                reply=answer.reply,
                reason=answer.reasoning,
            )

    return PipelineTrace(
        classification=classification,
        agent_reply=answer,
        decision=decision,
    )


def decide(thread: str, has_attachments: bool = False) -> Decision:
    """Run the AI steps for one email thread. The models propose, this function decides."""
    return decide_with_trace(thread, has_attachments).decision