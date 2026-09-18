from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, TypeVar
from xml.etree import ElementTree

from classroom_cli import ClassroomSession, LectureDeck, _validate_live_provider
from classroom_logging import ClassroomLogger
from env_loader import load_lab_env
from lesson_store import LessonStore
from orchestrator import OrchestratorAgent
from providers import make_provider


ROOT = Path(__file__).resolve().parent
MATERIAL_KEYWORDS = {
    "flashcard": ("flashcard", "flash card", "thẻ", "the", "card"),
    "mindmap": ("mindmap", "mind map", "sơ đồ", "so do"),
    "quiz": ("quiz", "trắc nghiệm", "trac nghiem", "câu hỏi", "cau hoi"),
}
CONVERSATION_SCOPES = ("shared", "private_ta", "private_student", "material")
HistoryCallable = TypeVar("HistoryCallable")


def empty_artifact_store() -> dict[str, Any]:
    return {
        "quiz": None,
        "flashcard": None,
        "mindmap": None,
    }


def empty_channel_histories() -> dict[str, list[str]]:
    return {scope: [] for scope in CONVERSATION_SCOPES}


def _normalize_refs(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, (str, int, float)):
        text = str(raw).strip()
        return [text] if text else []
    if isinstance(raw, list):
        result: list[str] = []
        for item in raw:
            result.extend(_normalize_refs(item))
        return list(dict.fromkeys(result))
    text = str(raw).strip()
    return [text] if text else []


def _normalize_pending(raw: Any) -> dict[str, str] | None:
    if not isinstance(raw, dict):
        return None
    mode = str(raw.get("mode", "")).strip()
    question = str(raw.get("question", "")).strip()
    if mode not in {"shared", "student"} or not question:
        return None
    return {"mode": mode, "question": question}


def _infer_material_types(text: str) -> list[str]:
    lowered = text.lower()
    found: list[str] = []
    for material_type, keywords in MATERIAL_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            found.append(material_type)
    return found


def _infer_material_type(text: str) -> str:
    types = _infer_material_types(text)
    return types[0] if types else "quiz"


def _message_event(
    agent: str,
    payload: dict[str, Any],
    *,
    channel: str,
    event_id: str | None = None,
    reply_to_id: str | None = None,
) -> dict[str, Any]:
    resolved_id = str(event_id or payload.get("id") or f"msg_{uuid.uuid4().hex[:8]}").strip()
    resolved_reply_to = reply_to_id if reply_to_id is not None else payload.get("reply_to_id")
    if resolved_reply_to is not None:
        resolved_reply_to = str(resolved_reply_to).strip() or None
    return {
        "id": resolved_id,
        "kind": "message",
        "agent": agent,
        "channel": channel,
        "intent": str(payload.get("intent", "")).strip(),
        "reply": str(payload.get("reply", "")).strip(),
        "citations": _normalize_refs(payload.get("citations") or payload.get("evidence_ids")),
        "active_recall": agent == "student" and str(payload.get("intent")) == "ask_question",
        "reply_to_id": resolved_reply_to,
    }


def _parse_material_content(content_format: str, content: str) -> dict[str, Any]:
    if content_format == "json":
        parsed = json.loads(content)
        return parsed if isinstance(parsed, dict) else {}

    root = ElementTree.fromstring(content)

    def parse_branch(node: ElementTree.Element) -> dict[str, Any]:
        return {
            "label": node.attrib.get("label", "").strip(),
            "citations": [child.text.strip() for child in node.findall("citation") if child.text and child.text.strip()],
            "children": [parse_branch(child) for child in node.findall("branch")],
        }

    return {
        "type": "mindmap",
        "title": root.attrib.get("title", "").strip(),
        "language": root.attrib.get("language", "").strip(),
        "covered_until": root.attrib.get("covered_until", "").strip(),
        "instructions": root.attrib.get("instructions", "").strip(),
        "root_topic": (root.findtext("root_topic") or "").strip(),
        "citations": [child.text.strip() for child in root.findall("citation") if child.text and child.text.strip()],
        "branches": [parse_branch(child) for child in root.findall("branch")],
    }


def _material_artifacts(result: dict[str, Any]) -> list[dict[str, Any]]:
    tool_results = result.get("tool_results") or []
    artifacts: list[dict[str, Any]] = []
    for item in tool_results:
        final_result = item.get("result") or {}
        content_format = str(final_result.get("content_format", "")).strip()
        content = str(final_result.get("content", "")).strip()
        if not content_format or not content:
            continue
        artifacts.append({
            "material_type": str(final_result.get("material_type", "")).strip(),
            "title": str(final_result.get("title", "")).strip(),
            "covered_until": str(final_result.get("covered_until", "")).strip(),
            "content_format": content_format,
            "item_count": int(final_result.get("item_count", 0) or 0),
            "citations": _normalize_refs(final_result.get("citations")),
            "content": _parse_material_content(content_format, content),
        })
    return artifacts


def _material_artifact(result: dict[str, Any]) -> dict[str, Any] | None:
    artifacts = _material_artifacts(result)
    return artifacts[0] if artifacts else None


def _resolve_ta_model(provider: Any, fallback_model: str | None) -> str | None:
    env_override = os.getenv("CLASSROOM_TA_MODEL", "").strip()
    if env_override:
        return env_override
    provider_module = type(provider).__module__
    if provider_module.endswith("openrouter_provider"):
        return "openai/gpt-4o"
    if provider_module.endswith("openai_provider"):
        return "gpt-4o"
    return fallback_model


@dataclass
class LiveClassroomSession:
    session_id: str
    artifact_id: str
    lesson_name: str
    session: ClassroomSession
    store: LessonStore
    orchestrator: OrchestratorAgent | None = None
    pending_prompt: dict[str, str] | None = None
    artifacts: dict[str, Any] = field(default_factory=empty_artifact_store)
    channel_histories: dict[str, list[str]] = field(default_factory=empty_channel_histories)
    auto_mode: str = "all"

    def __post_init__(self) -> None:
        if self.orchestrator is None:
            self.orchestrator = OrchestratorAgent(
                self.session.provider,
                model=self.session.model,
            )

    def bootstrap(self, *, current_slide: int, auto_mode: str) -> dict[str, Any]:
        self.auto_mode = auto_mode
        self.pending_prompt = None
        self._load_persisted_artifacts()
        self._load_persisted_history()
        self.session.set_current_slide(current_slide, reason="bootstrap", emit_log=False)
        events = self._immediate_mode_events(auto_mode)
        self._persist_agent_events(events)
        return self._snapshot(events)

    def sync_slide(self, *, current_slide: int, auto_mode: str) -> dict[str, Any]:
        previous_slide = self.session.current_slide
        previous_mode = self.auto_mode
        self.auto_mode = auto_mode
        self.pending_prompt = None
        self.session.set_current_slide(current_slide, reason="state_restore", emit_log=False)
        if previous_slide != current_slide:
            self.session.logger.log_event(
                "slide_changed",
                actor="learner",
                reason="frontend_navigation",
                previous_slide=previous_slide,
                current_slide=current_slide,
                current_slide_title=self.session.get_current_slide().title,
                source_file=self.session.deck.source_path.name,
                markdown_file=self.session.deck.markdown_path.name,
                slide_number=self.session.current_slide,
                slide_title=self.session.get_current_slide().title,
            )
        elif previous_mode != auto_mode:
            self.session.logger.log_event(
                "mode_changed",
                actor="learner",
                previous_mode=previous_mode,
                current_mode=auto_mode,
                source_file=self.session.deck.source_path.name,
                markdown_file=self.session.deck.markdown_path.name,
                slide_number=self.session.current_slide,
                slide_title=self.session.get_current_slide().title,
            )
        events = self._immediate_mode_events(auto_mode)
        self._persist_agent_events(events)
        return self._snapshot(events)

    def trigger_delayed_student_prompt(self) -> dict[str, Any]:
        if self.pending_prompt:
            return self._snapshot([])
        events: list[dict[str, Any]] = []

        if self.auto_mode == "all":
            student_turn = self._run_in_scope("shared", self.session.start_shared_round)
            raw_question = str(student_turn.get("reply", "")).strip()
            if raw_question:
                eval_result = self.orchestrator.evaluate_student_question(
                    raw_question,
                    current_slide=self.session.get_current_slide(),
                    deck=self.session.deck,
                )
                if not eval_result.approved and eval_result.improved_question:
                    student_turn["reply"] = eval_result.improved_question
                    self.session.logger.log_event(
                        "orchestrator_student_critique",
                        actor="orchestrator",
                        channel="shared",
                        original_question=raw_question,
                        improved_question=eval_result.improved_question,
                        feedback=eval_result.feedback,
                        key_concepts=eval_result.key_concepts,
                    )
                event = _message_event("student", student_turn, channel="shared")
                if event["reply"]:
                    self.pending_prompt = {"mode": "shared", "question": event["reply"]}
                    events.append(event)

        elif self.auto_mode == "student":
            student_turn = self._run_in_scope("private_student", self.session.start_private_student_round)
            raw_question = str(student_turn.get("reply", "")).strip()
            if raw_question:
                eval_result = self.orchestrator.evaluate_student_question(
                    raw_question,
                    current_slide=self.session.get_current_slide(),
                    deck=self.session.deck,
                )
                if not eval_result.approved and eval_result.improved_question:
                    student_turn["reply"] = eval_result.improved_question
                    self.session.logger.log_event(
                        "orchestrator_student_critique",
                        actor="orchestrator",
                        channel="private_student",
                        original_question=raw_question,
                        improved_question=eval_result.improved_question,
                        feedback=eval_result.feedback,
                        key_concepts=eval_result.key_concepts,
                    )
                event = _message_event("student", student_turn, channel="private_student")
                if event["reply"]:
                    self.pending_prompt = {"mode": "student", "question": event["reply"]}
                    events.append(event)

        self._persist_agent_events(events)
        return self._snapshot(events)

    def handle_timeout(self) -> dict[str, Any]:
        if not self.pending_prompt:
            return self._snapshot([])
        question = self.pending_prompt["question"]
        mode = self.pending_prompt.get("mode", "shared")
        scope = "shared" if mode == "shared" else "private_student"

        self.session._log_event(
            "learner_timeout",
            actor="learner",
            target="student",
            channel=scope,
            related_question=question,
        )

        history = self.channel_histories.get(scope, [])
        plan = self.orchestrator.plan_timeout(
            question,
            mode=mode,
            current_slide=self.session.get_current_slide(),
            deck=self.session.deck,
            chat_history=history,
        )

        events: list[dict[str, Any]] = []
        new_artifacts: list[dict[str, Any]] = []
        self.pending_prompt = None

        for task in plan.agent_tasks:
            task_channel = task.channel if task.channel in CONVERSATION_SCOPES else scope
            if task.agent_name == "ta_agent":
                ta_turn = self._teacher_reply_after_timeout(
                    question,
                    channel=task_channel,
                    mode="shared_classroom" if task_channel == "shared" else "private_student_chat",
                    instruction=task.instruction,
                )
                events.append(_message_event("teacher", ta_turn, channel=task_channel))
            elif task.agent_name == "student_agent":
                student_turn = self._run_in_scope(
                    task_channel,
                    lambda: self.session.chat_student(
                        task.instruction,
                        channel=task_channel,
                    ),
                )
                events.append(_message_event("student", student_turn, channel=task_channel))
            elif task.agent_name == "generator_agent":
                self._handle_generator_turn(
                    task.instruction,
                    events,
                    new_artifacts,
                    channel="material",
                    record_user_turn=False,
                )

        if not events:
            ta_turn = self._teacher_reply_after_timeout(
                question,
                channel=scope,
                mode="shared_classroom" if scope == "shared" else "private_student_chat",
            )
            event = _message_event("teacher", ta_turn, channel=scope)
            if event["reply"]:
                events.append(event)

        self._merge_artifacts(new_artifacts)
        self._persist_agent_events(events)
        return self._snapshot(events)

    def handle_message(
        self,
        *,
        current_slide: int,
        target: str,
        text: str,
        message_id: str | None = None,
        reply_to_id: str | None = None,
    ) -> dict[str, Any]:
        self.session.set_current_slide(current_slide, reason="state_restore", emit_log=False)
        events: list[dict[str, Any]] = []
        new_artifacts: list[dict[str, Any]] = []
        trimmed = text.strip()
        user_turn_id = message_id or f"msg_{uuid.uuid4().hex[:8]}"

        target_channel = (
            "private_ta" if target == "teacher"
            else "private_student" if target == "student"
            else "material" if target == "generator"
            else "shared"
        )
        relevant_history = self.channel_histories.get(target_channel, [])

        plan = self.orchestrator.plan(
            trimmed,
            current_slide=self.session.get_current_slide(),
            deck=self.session.deck,
            chat_history=relevant_history,
            target_hint=target,
            reply_to_id=reply_to_id,
            pending_prompt=self.pending_prompt,
        )

        if plan.guardrail_status == "rejected":
            self._persist_user_turn(
                target_channel,
                trimmed,
                intent="guardrail_rejected",
                turn_id=user_turn_id,
                reply_to_id=reply_to_id,
            )
            refusal_reply = plan.reply or "Nội dung yêu cầu không phù hợp hoặc không liên quan đến bài giảng. Vui lòng đặt câu hỏi liên quan đến nội dung học tập!"
            refusal_agent = "student" if target == "student" else "teacher"
            refusal_event = {
                "id": f"msg_{uuid.uuid4().hex[:8]}",
                "kind": "message",
                "agent": refusal_agent,
                "channel": target_channel,
                "intent": "guardrail_refusal",
                "reply": refusal_reply,
                "citations": [],
                "active_recall": False,
                "reply_to_id": user_turn_id,
            }
            events.append(refusal_event)
            self._persist_agent_events(events)
            return self._snapshot(events)

        self._persist_user_turn(
            target_channel,
            trimmed,
            intent="learner_turn",
            turn_id=user_turn_id,
            reply_to_id=reply_to_id,
        )

        for task in plan.agent_tasks:
            task_channel = task.channel if task.channel in CONVERSATION_SCOPES else target_channel
            task_reply_to = task.reply_to_id or user_turn_id

            if task.agent_name == "ta_agent":
                if self.pending_prompt and self.pending_prompt.get("mode") == "shared" and task_channel == "shared":
                    ta_turn = self._teacher_follow_up_shared(
                        self.pending_prompt["question"],
                        task.instruction,
                        user_turn_id=user_turn_id,
                        reply_to_id=task_reply_to,
                    )
                    self.pending_prompt = None
                    events.append(_message_event("teacher", ta_turn, channel=task_channel, reply_to_id=task_reply_to))
                else:
                    ta_turn = self._teacher_private_reply(
                        task.instruction,
                        channel=task_channel,
                        user_turn_id=user_turn_id,
                        reply_to_id=task_reply_to,
                    )
                    events.append(_message_event("teacher", ta_turn, channel=task_channel, reply_to_id=task_reply_to))

            elif task.agent_name == "student_agent":
                if self.pending_prompt and self.pending_prompt.get("mode") == "student":
                    student_feedback = self._run_in_scope(
                        "private_student",
                        lambda: self.session.finish_private_student_round(
                            self.pending_prompt["question"],
                            task.instruction,
                            msg_id=user_turn_id,
                            reply_to_id=task_reply_to,
                        ),
                    )
                    self.pending_prompt = None
                    events.append(_message_event("student", student_feedback, channel="private_student", reply_to_id=task_reply_to))
                else:
                    student_turn = self._run_in_scope(
                        task_channel,
                        lambda: self.session.chat_student(
                            task.instruction,
                            channel=task_channel,
                            msg_id=user_turn_id,
                            reply_to_id=task_reply_to,
                        ),
                    )
                    events.append(_message_event("student", student_turn, channel=task_channel, reply_to_id=task_reply_to))

            elif task.agent_name == "generator_agent":
                self._handle_generator_turn(
                    task.instruction,
                    events,
                    new_artifacts,
                    channel="material",
                    user_turn_id=user_turn_id,
                    reply_to_id=task_reply_to,
                    record_user_turn=False,
                )

        if not events and plan.reply:
            events.append({
                "id": f"msg_{uuid.uuid4().hex[:8]}",
                "kind": "message",
                "agent": "teacher",
                "channel": target_channel,
                "intent": "orchestrator_reply",
                "reply": plan.reply,
                "citations": [],
                "active_recall": False,
                "reply_to_id": user_turn_id,
            })

        self._merge_artifacts(new_artifacts)
        self._persist_agent_events(events)
        return self._snapshot(events)

    def _handle_generator_turn(
        self,
        trimmed: str,
        events: list[dict[str, Any]],
        new_artifacts: list[dict[str, Any]],
        *,
        channel: str = "material",
        user_turn_id: str | None = None,
        reply_to_id: str | None = None,
        record_user_turn: bool = True,
    ) -> None:
        if record_user_turn:
            self._persist_user_turn(channel, trimmed, intent="generate_material", turn_id=user_turn_id, reply_to_id=reply_to_id)
        types = _infer_material_types(trimmed)
        mat_type = types[0] if len(types) == 1 else None
        result = self._run_in_scope(channel, lambda: self.session.generate_material(mat_type, trimmed))
        payload = result.get("agent_response") or {}
        artifacts = _material_artifacts(result)
        for art in artifacts:
            new_artifacts.append(art)

        type_names = {
            "quiz": "Quiz trắc nghiệm",
            "flashcard": "Bộ thẻ ghi nhớ (Flashcard)",
            "mindmap": "Sơ đồ tư duy (Mindmap)",
        }

        if len(artifacts) == 0:
            if payload.get("reply"):
                events.append(_message_event("generator", payload, channel=channel, reply_to_id=user_turn_id))
        elif len(artifacts) == 1:
            art = artifacts[0]
            t_name = type_names.get(art["material_type"], art["material_type"])
            reply = payload.get("reply") or f"Đã tạo thành công {t_name}: **{art['title']}** ({art['item_count']} mục)."
            events.append({
                "id": f"msg_{uuid.uuid4().hex[:8]}",
                "kind": "message",
                "agent": "generator",
                "channel": channel,
                "intent": "generate_material",
                "reply": reply,
                "citations": art.get("citations", []),
                "active_recall": False,
                "reply_to_id": user_turn_id,
            })
        else:
            for art in artifacts:
                t_name = type_names.get(art["material_type"], art["material_type"])
                item_label = (
                    "câu hỏi" if art["material_type"] == "quiz"
                    else "thẻ ghi nhớ" if art["material_type"] == "flashcard"
                    else "nhánh kiến thức"
                )
                reply = f"⚡ Đã tạo thành công **{t_name}**: **{art['title']}** ({art['item_count']} {item_label})."
                events.append({
                    "id": f"msg_{uuid.uuid4().hex[:8]}",
                    "kind": "message",
                    "agent": "generator",
                    "channel": channel,
                    "intent": "generate_material",
                    "reply": reply,
                    "citations": art.get("citations", []),
                    "active_recall": False,
                    "reply_to_id": user_turn_id,
                })


    def close(self) -> None:
        logger = self.session.logger
        if logger:
            logger.log_event(
                "session_closed",
                actor="system",
                day_id=self.artifact_id,
                slide_number=self.session.current_slide,
                slide_title=self.session.get_current_slide().title,
            )

    def _immediate_mode_events(self, auto_mode: str) -> list[dict[str, Any]]:
        if auto_mode != "teacher":
            return []
        ta_turn = self._teacher_slide_summary()
        event = _message_event("teacher", ta_turn, channel="private_ta")
        return [event] if event["reply"] else []

    def _teacher_slide_summary(self) -> dict[str, Any]:
        return self._run_ta_turn(
            scope="private_ta",
            channel="private_ta",
            mode="private_ta_chat",
            task=(
                "Người học vừa dừng ở slide hiện tại và đang chờ TA chủ động hỗ trợ.\n"
                "Hãy tóm tắt ngắn ý chính của slide này và nhắc đúng 1 điểm quan trọng cần chú ý."
            ),
        )

    def _teacher_private_reply(
        self,
        learner_message: str,
        *,
        channel: str,
        user_turn_id: str | None = None,
        reply_to_id: str | None = None,
    ) -> dict[str, Any]:
        mode = "shared_classroom" if channel == "shared" else "private_ta_chat"
        reply_hint = f"\n(Người học đang reply tin nhắn: {reply_to_id})" if reply_to_id else ""
        return self._run_ta_turn(
            scope="shared" if channel == "shared" else "private_ta",
            channel=channel,
            mode=mode,
            learner_message=learner_message,
            message_kind="question",
            log_target="teacher",
            user_turn_id=user_turn_id,
            reply_to_id=reply_to_id,
            task=(
                "Người học đang trao đổi trực tiếp với TA.\n"
                f"Tin nhắn của người học: {learner_message}{reply_hint}\n"
                "Hãy trả lời rõ ràng, có thể xác nhận/chỉnh sửa hiểu nhầm nếu cần, và bám sát nội dung bài giảng."
            ),
        )

    def _teacher_follow_up_shared(
        self,
        student_question: str,
        learner_message: str,
        *,
        user_turn_id: str | None = None,
        reply_to_id: str | None = None,
    ) -> dict[str, Any]:
        reply_hint = f"\n(Người học đang reply tin nhắn: {reply_to_id})" if reply_to_id else ""
        return self._run_ta_turn(
            scope="shared",
            channel="shared",
            mode="shared_classroom",
            learner_message=learner_message,
            message_kind="learner_turn",
            log_target="student",
            related_question=student_question,
            user_turn_id=user_turn_id,
            reply_to_id=reply_to_id,
            task=(
                "Trong lớp học chung, student agent vừa hỏi người học.\n"
                f"Câu hỏi của student agent: {student_question}\n"
                f"Tin nhắn mới của người học: {learner_message}{reply_hint}\n"
                "Hãy tự xác định đây là câu trả lời cho câu hỏi của student agent hay là một câu hỏi/thắc mắc mới.\n"
                "Nếu là câu trả lời, hãy đánh giá bằng đúng một nhãn: đúng | thiếu | sai | không đủ thông tin, rồi xác nhận/chỉnh sửa ngắn gọn.\n"
                "Nếu là câu hỏi mới, hãy trả lời câu hỏi đó rõ ràng và có thể liên hệ ngắn gọn tới câu hỏi trước nếu hữu ích."
            ),
        )

    def _teacher_reply_after_timeout(
        self,
        student_question: str,
        *,
        channel: str,
        mode: str,
        instruction: str | None = None,
    ) -> dict[str, Any]:
        scope = "shared" if channel == "shared" else "private_student"
        self.session._log_event(
            "learner_timeout",
            actor="learner",
            target="student",
            channel=channel,
            related_question=student_question,
        )
        task_prompt = instruction or (
            "Student agent đã hỏi người học nhưng sau thời gian quy định vẫn không nhận được câu trả lời.\n"
            "timeout_status: timed_out\n"
            f"Câu hỏi cần TA trả lời thay: {student_question}\n"
            "Hãy nói rõ rằng đã hết thời gian và trả lời ngắn gọn, chính xác thay cho người học."
        )
        return self._run_ta_turn(
            scope=scope,
            channel=channel,
            mode=mode,
            task=task_prompt,
        )

    def _run_ta_turn(
        self,
        *,
        scope: str,
        channel: str,
        mode: str,
        task: str,
        learner_message: str | None = None,
        message_kind: str = "question",
        log_target: str = "teacher",
        related_question: str | None = None,
        user_turn_id: str | None = None,
        reply_to_id: str | None = None,
    ) -> dict[str, Any]:
        def invoke() -> dict[str, Any]:
            if learner_message:
                self.session._log_event(
                    "learner_message",
                    actor="learner",
                    target=log_target,
                    channel=channel,
                    message_kind=message_kind,
                    related_question=related_question,
                    message=learner_message,
                    reply_to_id=reply_to_id,
                )
                self.session._record_history("Learner", learner_message, msg_id=user_turn_id)
            prompt = self._build_ta_prompt(mode=mode, task=task)
            response = self.session._run_json_agent(self.session.ta_agent, prompt)
            if reply_to_id and not response.get("reply_to_id"):
                response["reply_to_id"] = reply_to_id
            elif not response.get("reply_to_id"):
                response["reply_to_id"] = user_turn_id
            agent_msg_id = self.session._record_history("TA", response.get("reply", ""))
            response["id"] = agent_msg_id
            self.session._log_agent_message("teacher", response, channel=channel, target="learner")
            return response

        return self._run_in_scope(scope, invoke)

    def _build_ta_prompt(self, *, mode: str, task: str) -> str:
        slide = self.session.get_current_slide()
        history = "\n".join(entry if entry.startswith("[") else f"- {entry}" for entry in self.session.chat_history[-10:]) or "- (no recent turns)"
        lecture_content = "\n\n".join(
            f"## Slide {item.number} — {item.title}\n\n{item.content}" for item in self.session.deck.slides
        )
        return (
            "Trusted classroom state\n"
            f"- mode: {mode}\n"
            f"- current_position: slide {slide.number}\n"
            f"- current_slide_title: {slide.title}\n"
            f"- source_file: {self.session.deck.source_path.name}\n"
            f"- markdown_file: {self.session.deck.markdown_path.name}\n"
            f"- chat_history:\n{history}\n\n"
            "current_segment\n"
            f"## Slide {slide.number} — {slide.title}\n\n{slide.content}\n\n"
            "covered_content\n"
            f"{self.session.deck.covered_content(slide.number)}\n\n"
            "lecture_content\n"
            f"{lecture_content}\n\n"
            "Task\n"
            f"{task}"
        )

    def _run_in_scope(self, scope: str, fn: Callable[[], HistoryCallable]) -> HistoryCallable:
        scoped_history = list(self.channel_histories.get(scope, []))
        self.session.chat_history = scoped_history
        result = fn()
        self.channel_histories[scope] = list(self.session.chat_history[-10:])
        return result

    def _persist_user_turn(
        self,
        scope: str,
        message: str,
        *,
        intent: str,
        turn_id: str | None = None,
        reply_to_id: str | None = None,
    ) -> str:
        return self.store.append_conversation_turn(
            artifact_id=self.artifact_id,
            session_id=self.session_id,
            scope=scope,
            actor="learner",
            message=message,
            intent=intent,
            slide_number=self.session.current_slide,
            slide_title=self.session.get_current_slide().title,
            turn_id=turn_id,
            reply_to_id=reply_to_id,
        )

    def _persist_agent_events(self, events: list[dict[str, Any]]) -> None:
        for event in events:
            reply = str(event.get("reply", "")).strip()
            if not reply:
                continue
            self.store.append_conversation_turn(
                artifact_id=self.artifact_id,
                session_id=self.session_id,
                scope=str(event.get("channel", "shared")).strip() or "shared",
                actor=str(event.get("agent", "unknown")).strip() or "unknown",
                message=reply,
                intent=str(event.get("intent", "")).strip(),
                citations=_normalize_refs(event.get("citations")),
                slide_number=self.session.current_slide,
                slide_title=self.session.get_current_slide().title,
                turn_id=str(event.get("id", "")).strip() or None,
                reply_to_id=str(event.get("reply_to_id", "")).strip() if event.get("reply_to_id") is not None else None,
            )

    def _load_persisted_history(self) -> None:
        try:
            for scope in CONVERSATION_SCOPES:
                turns = self.store.get_conversation_turns(
                    self.artifact_id,
                    self.session_id,
                    scope,
                    limit=10,
                )
                formatted_turns: list[str] = []
                for turn in turns:
                    msg_id = turn.get("id") or f"msg_{uuid.uuid4().hex[:6]}"
                    actor = str(turn.get("actor", "unknown")).strip()
                    speaker = "Learner" if actor == "learner" else "TA" if actor in {"teacher", "ta"} else "Student Agent" if actor == "student" else actor
                    msg = str(turn.get("message", "")).strip()
                    if msg:
                        formatted_turns.append(f"[{msg_id}] {speaker}: {msg}")
                self.channel_histories[scope] = formatted_turns[-10:]
        except Exception as exc:
            print(f"[WARN] Failed to load persisted history: {exc}")

    def _load_persisted_artifacts(self) -> None:
        try:
            persisted = self.store.list_generated_materials(self.artifact_id, limit=50)
            for mat in reversed(persisted):
                m_type = str(mat.get("material_type", "")).strip()
                if m_type in self.artifacts and self.artifacts[m_type] is None:
                    self.artifacts[m_type] = mat
        except Exception:
            pass

    def _merge_artifacts(self, artifacts: list[dict[str, Any]]) -> None:
        for artifact in artifacts:
            material_type = str(artifact.get("material_type", "")).strip()
            if material_type in self.artifacts:
                self.artifacts[material_type] = artifact

            try:
                saved = self.store.save_generated_material(
                    artifact_id=self.artifact_id,
                    session_id=self.session_id,
                    material_type=material_type,
                    title=str(artifact.get("title", "")).strip(),
                    content=artifact.get("content"),
                    content_format=str(artifact.get("content_format", "json")),
                    item_count=int(artifact.get("item_count", 0) or 0),
                    citations=artifact.get("citations", []),
                    covered_until=str(artifact.get("covered_until", "")),
                    slide_number=self.session.current_slide,
                    slide_title=self.session.get_current_slide().title,
                )
                artifact["id"] = saved.get("id")
            except Exception as exc:
                print(f"[WARN] Failed to persist generated material: {exc}")

    def _snapshot(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        current = self.session.get_current_slide()
        try:
            mat_count = len(self.store.list_generated_materials(self.artifact_id))
        except Exception:
            mat_count = 0
        return {
            "sessionId": self.session_id,
            "dayId": self.artifact_id,
            "currentSlide": current.number,
            "currentSlideTitle": current.title,
            "maxSlide": self.session.deck.max_slide(),
            "pendingPrompt": _normalize_pending(self.pending_prompt),
            "artifacts": self.artifacts,
            "historyTopics": self.store.list_recent_topics(self.artifact_id, limit=8),
            "materialsCount": mat_count,
            "events": events,
        }


def create_live_classroom_session(
    artifact_id: str,
    *,
    store: LessonStore,
    current_slide: int,
    provider_name: str | None = None,
    model: str | None = None,
    source: str = "frontend_websocket",
    session_id: str | None = None,
) -> LiveClassroomSession:
    load_lab_env(ROOT)
    lesson = store.get_lesson_bundle(artifact_id)
    resolved_provider = (provider_name or os.getenv("CLASSROOM_PROVIDER") or "openai").strip()
    _validate_live_provider(resolved_provider)
    deck = LectureDeck.from_markdown(lesson.slide_path, lesson.markdown_path)
    session_uuid = session_id or f"ws-{uuid.uuid4()}"
    logger = ClassroomLogger(session_id=session_uuid, source=source)
    provider = make_provider(resolved_provider)
    session = ClassroomSession(deck=deck, provider=provider, model=model, logger=logger)
    session.ta_agent.model = _resolve_ta_model(provider, model)
    session.set_current_slide(current_slide, reason="state_restore", emit_log=False)
    logger.log_event(
        "session_started",
        actor="system",
        day_id=artifact_id,
        provider=resolved_provider,
        model=model,
        ta_model=session.ta_agent.model,
        source_file=session.deck.source_path.name,
        markdown_file=session.deck.markdown_path.name,
        slide_number=session.current_slide,
        slide_title=session.get_current_slide().title,
    )
    orchestrator = OrchestratorAgent(provider, model=model)
    return LiveClassroomSession(
        session_id=session_uuid,
        artifact_id=artifact_id,
        lesson_name=lesson.name,
        session=session,
        store=store,
        orchestrator=orchestrator,
    )
