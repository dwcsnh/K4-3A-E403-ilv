from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agent import Agent, AgentRun
from providers.base import Provider


PROMPTS_DIR = Path(__file__).resolve().parent / "artifacts" / "system_prompts"
ORCHESTRATOR_PROMPT_PATH = PROMPTS_DIR / "orchestrator_agent.md"


def _read_prompt() -> str:
    if ORCHESTRATOR_PROMPT_PATH.exists():
        return ORCHESTRATOR_PROMPT_PATH.read_text(encoding="utf-8")
    return "You are the Orchestrator Agent for an AI multi-agent classroom."


def _parse_json(text: str | None) -> dict[str, Any] | None:
    if not text:
        return None
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(cleaned[start : end + 1])
        except Exception:
            pass
    return None


@dataclass
class AgentTask:
    agent_name: str  # "ta_agent" | "student_agent" | "generator_agent"
    channel: str     # "shared" | "private_ta" | "private_student" | "material"
    instruction: str
    reply_to_id: str | None = None


@dataclass
class OrchestratorPlan:
    guardrail_status: str  # "passed" | "rejected"
    refusal_reason: str | None = None
    reply: str | None = None
    reasoning: str = ""
    agent_tasks: list[AgentTask] = field(default_factory=list)


@dataclass
class ConceptEvaluation:
    approved: bool
    key_concepts: list[str] = field(default_factory=list)
    covered_concept: str | None = None
    feedback: str = ""
    improved_question: str | None = None


class OrchestratorAgent:
    def __init__(
        self,
        provider: Provider,
        *,
        model: str | None = None,
        system_prompt: str | None = None,
    ) -> None:
        self.provider = provider
        self.model = model or os.getenv("CLASSROOM_ORCHESTRATOR_MODEL") or None
        self.system_prompt = system_prompt or _read_prompt()
        self.agent = Agent(
            self.provider,
            system_prompt=self.system_prompt,
            model=self.model,
        )

    def plan(
        self,
        message: str,
        *,
        current_slide: Any,
        deck: Any,
        chat_history: list[str],
        target_hint: str = "all",
        reply_to_id: str | None = None,
        pending_prompt: dict[str, str] | None = None,
    ) -> OrchestratorPlan:
        history_str = "\n".join(
            entry if entry.startswith("[") else f"- {entry}"
            for entry in chat_history[-10:]
        ) or "- (no recent turns)"

        pending_str = (
            f"- active_mode: {pending_prompt.get('mode')}\n- active_question: {pending_prompt.get('question')}"
            if pending_prompt
            else "(none)"
        )

        prompt = (
            "Trusted classroom state\n"
            f"- current_position: slide {current_slide.number}\n"
            f"- current_slide_title: {current_slide.title}\n"
            f"- target_hint: {target_hint}\n"
            f"- reply_to_id: {reply_to_id or '(none)'}\n"
            f"- pending_student_prompt: {pending_str}\n"
            f"- chat_history:\n{history_str}\n\n"
            "current_segment\n"
            f"## Slide {current_slide.number} — {current_slide.title}\n\n{current_slide.content}\n\n"
            "covered_content\n"
            f"{deck.covered_content(current_slide.number)}\n\n"
            "User input to evaluate and dispatch\n"
            f"{message}\n\n"
            "Task\n"
            "Evaluate safety and guardrails, parse all user intents, and generate the Orchestrator Plan JSON response."
        )

        run = self.agent.run([{"role": "user", "content": prompt}])
        parsed = _parse_json(run.text)

        if not parsed:
            # Fallback heuristic if LLM output fails JSON parsing
            return self._heuristic_fallback(
                message,
                target_hint=target_hint,
                reply_to_id=reply_to_id,
                pending_prompt=pending_prompt,
            )

        guardrail_status = str(parsed.get("guardrail_status", "passed")).strip().lower()
        if guardrail_status not in {"passed", "rejected"}:
            guardrail_status = "passed"

        refusal_reason = parsed.get("refusal_reason")
        reply = parsed.get("reply")
        reasoning = str(parsed.get("reasoning", "")).strip()

        tasks: list[AgentTask] = []
        raw_tasks = parsed.get("agent_tasks") or []
        for t in raw_tasks:
            if not isinstance(t, dict):
                continue
            name = str(t.get("agent_name", "")).strip().lower()
            if name not in {"ta_agent", "student_agent", "generator_agent"}:
                continue
            channel = str(t.get("channel", "")).strip().lower()
            if channel not in {"shared", "private_ta", "private_student", "material"}:
                channel = "shared"
            instruction = str(t.get("instruction", "")).strip() or message
            task_reply_id = t.get("reply_to_id") or reply_to_id
            tasks.append(
                AgentTask(
                    agent_name=name,
                    channel=channel,
                    instruction=instruction,
                    reply_to_id=str(task_reply_id).strip() if task_reply_id else None,
                )
            )

        if guardrail_status == "passed" and not tasks:
            # Ensure at least one task is created
            tasks.append(
                AgentTask(
                    agent_name="ta_agent",
                    channel="shared" if target_hint == "all" else "private_ta",
                    instruction=message,
                    reply_to_id=reply_to_id,
                )
            )

        return OrchestratorPlan(
            guardrail_status=guardrail_status,
            refusal_reason=str(refusal_reason).strip() if refusal_reason else None,
            reply=str(reply).strip() if reply else None,
            reasoning=reasoning,
            agent_tasks=tasks,
        )

    def evaluate_student_question(
        self,
        question: str,
        *,
        current_slide: Any,
        deck: Any,
    ) -> ConceptEvaluation:
        prompt = (
            "Bạn là Orchestrator Agent (Điều phối viên Lớp học).\n"
            "Nhiệm vụ của bạn là kiểm duyệt sư phạm câu hỏi do Bạn học (Student Agent) chuẩn bị hỏi lớp.\n\n"
            f"## Slide {current_slide.number} — {current_slide.title}\n\n{current_slide.content}\n\n"
            f"Câu hỏi đề xuất của Student Agent: \"{question}\"\n\n"
            "Yêu cầu đánh giá:\n"
            "1. Xác định 1-3 khái niệm cốt lõi (key_concepts) của slide này.\n"
            "2. Kiểm tra xem câu hỏi có chạm đúng vào trọng tâm của slide và giúp người học ghi nhớ chủ động (active recall) không.\n"
            "3. Nếu câu hỏi tốt, approved = true. Nếu câu hỏi hời hợt hoặc lệch đề, approved = false và đề xuất 1 câu hỏi cải tiến ngắn gọn, sắc sảo hơn.\n\n"
            "Trả về JSON định dạng:\n"
            "{\n"
            '  "approved": true | false,\n'
            '  "key_concepts": ["khái niệm 1", "khái niệm 2"],\n'
            '  "covered_concept": "khái niệm được hỏi",\n'
            '  "feedback": "nhận xét ngắn",\n'
            '  "improved_question": "câu hỏi cải tiến nếu approved=false, hoặc null nếu approved=true"\n'
            "}"
        )
        run = self.agent.run([{"role": "user", "content": prompt}])
        parsed = _parse_json(run.text) or {}
        approved = bool(parsed.get("approved", True))
        key_concepts = parsed.get("key_concepts") if isinstance(parsed.get("key_concepts"), list) else []
        covered_concept = parsed.get("covered_concept")
        feedback = str(parsed.get("feedback", "")).strip()
        improved_question = parsed.get("improved_question")

        return ConceptEvaluation(
            approved=approved,
            key_concepts=[str(c) for c in key_concepts],
            covered_concept=str(covered_concept).strip() if covered_concept else None,
            feedback=feedback,
            improved_question=str(improved_question).strip() if improved_question else None,
        )

    def plan_timeout(
        self,
        student_question: str,
        mode: str,
        *,
        current_slide: Any,
        deck: Any,
        chat_history: list[str],
    ) -> OrchestratorPlan:
        system_event = (
            f"[SYSTEM_EVENT] Timeout: Người học đã không trả lời câu hỏi '{student_question}' "
            f"của Student Agent sau thời gian quy định (mode: {mode})."
        )
        return self.plan(
            system_event,
            current_slide=current_slide,
            deck=deck,
            chat_history=chat_history,
            target_hint="teacher" if mode != "student" else "all",
            pending_prompt={"mode": mode, "question": student_question},
        )

    def _heuristic_fallback(
        self,
        message: str,
        *,
        target_hint: str,
        reply_to_id: str | None,
        pending_prompt: dict[str, str] | None,
    ) -> OrchestratorPlan:
        lowered = message.lower()
        tasks: list[AgentTask] = []

        # Check material keywords
        if any(kw in lowered for kw in ("quiz", "flashcard", "mindmap", "trắc nghiệm", "thẻ ghi nhớ", "sơ đồ")):
            tasks.append(
                AgentTask(
                    agent_name="generator_agent",
                    channel="material",
                    instruction=message,
                    reply_to_id=reply_to_id,
                )
            )

        # Check if there is also an academic or peer intent
        if target_hint == "student":
            tasks.append(
                AgentTask(
                    agent_name="student_agent",
                    channel="private_student",
                    instruction=message,
                    reply_to_id=reply_to_id,
                )
            )
        elif target_hint == "teacher":
            tasks.append(
                AgentTask(
                    agent_name="ta_agent",
                    channel="private_ta",
                    instruction=message,
                    reply_to_id=reply_to_id,
                )
            )
        elif not tasks or any(kw in lowered for kw in ("giải thích", "tại sao", "là gì", "như thế nào", "thầy", "?")):
            channel = "shared"
            tasks.append(
                AgentTask(
                    agent_name="ta_agent",
                    channel=channel,
                    instruction=message,
                    reply_to_id=reply_to_id,
                )
            )

        return OrchestratorPlan(
            guardrail_status="passed",
            refusal_reason=None,
            reply=None,
            reasoning="Fallback heuristic plan",
            agent_tasks=tasks,
        )
