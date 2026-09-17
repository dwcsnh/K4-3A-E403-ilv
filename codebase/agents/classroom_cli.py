from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import select
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agent import Agent, AgentRun
from env_loader import load_lab_env
from ingest.slides import ensure_slide_markdown
from providers import make_provider
from providers.base import ModelResponse, Provider, ToolCall
from tools import load_tool_declarations, to_openai_tools


ROOT = Path(__file__).resolve().parent
PROMPTS_DIR = ROOT / "artifacts" / "system_prompts"
TOOLS_DIR = ROOT / "artifacts" / "tools"
DEFAULT_INGEST_DIR = ROOT / "data" / "ingested"
SLIDE_HEADING_RE = re.compile(r"^##\s+Slide\s+(\d+)(?:\s*[—-]\s*(.*))?$", re.MULTILINE)
LIVE_PROVIDER_ENVS = {
    "openai": "OPENAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}
SINGLE_AGENT_CHOICES = {"ta", "student", "material"}


@dataclass
class SlideSection:
    number: int
    title: str
    content: str


@dataclass
class LectureDeck:
    source_path: Path
    markdown_path: Path
    slides: list[SlideSection]

    @classmethod
    def from_markdown(cls, source_path: Path, markdown_path: Path) -> "LectureDeck":
        markdown = markdown_path.read_text(encoding="utf-8")
        matches = list(SLIDE_HEADING_RE.finditer(markdown))
        if not matches:
            content = markdown.strip() or "_No lecture content available._"
            return cls(
                source_path=source_path,
                markdown_path=markdown_path,
                slides=[SlideSection(number=1, title=source_path.stem, content=content)],
            )

        slides: list[SlideSection] = []
        for index, match in enumerate(matches):
            slide_number = int(match.group(1))
            title = (match.group(2) or f"Slide {slide_number}").strip()
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
            content = markdown[start:end].strip() or "_No extractable text on this slide._"
            slides.append(SlideSection(number=slide_number, title=title, content=content))
        return cls(source_path=source_path, markdown_path=markdown_path, slides=slides)

    def max_slide(self) -> int:
        return max(slide.number for slide in self.slides)

    def get_slide(self, slide_number: int) -> SlideSection:
        for slide in self.slides:
            if slide.number == slide_number:
                return slide
        raise ValueError(f"Slide {slide_number} does not exist")

    def covered_content(self, slide_number: int) -> str:
        covered: list[str] = []
        for slide in self.slides:
            if slide.number > slide_number:
                break
            covered.append(f"## Slide {slide.number} — {slide.title}\n\n{slide.content}")
        return "\n\n".join(covered)


@dataclass
class ClassroomSession:
    deck: LectureDeck
    provider: Provider
    model: str | None = None
    chat_history: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.current_slide = 1
        self.ta_agent = Agent(
            self.provider,
            system_prompt=_read_text(PROMPTS_DIR / "ta_agent.md"),
            model=self.model,
        )
        self.student_agent = Agent(
            self.provider,
            system_prompt=_read_text(PROMPTS_DIR / "student_agent.md"),
            model=self.model,
        )
        learning_tools = to_openai_tools(
            load_tool_declarations(TOOLS_DIR / "generate_learning_material.yaml")
        )
        self.learning_material_agent = Agent(
            self.provider,
            system_prompt=_read_text(PROMPTS_DIR / "learning_material_generator.md"),
            tools=learning_tools,
            model=self.model,
        )

    def set_current_slide(self, slide_number: int) -> SlideSection:
        slide = self.deck.get_slide(slide_number)
        self.current_slide = slide.number
        return slide

    def get_current_slide(self) -> SlideSection:
        return self.deck.get_slide(self.current_slide)

    def describe_current_slide(self) -> str:
        slide = self.get_current_slide()
        excerpt = slide.content.splitlines()[:8]
        excerpt_text = "\n".join(excerpt).strip() or "_No extractable text on this slide._"
        return (
            f"Slide hiện tại: {slide.number} - {slide.title}\n"
            f"Nguồn markdown: {self.deck.markdown_path}\n"
            f"{excerpt_text}"
        )

    def ask_ta(self, question: str) -> dict[str, Any]:
        question = question.strip()
        if not question:
            raise ValueError("Question must not be empty")
        self._record_history("Learner", question)
        prompt = self._build_prompt(
            mode="private_ta_chat",
            task=(
                "Người học đang chat riêng với TA.\n"
                f"Câu hỏi của người học: {question}\n"
                "Hãy trả lời theo đúng response contract."
            ),
        )
        response = self._run_json_agent(self.ta_agent, prompt)
        self._record_history("TA", response.get("reply", ""))
        return response

    def start_shared_round(self) -> dict[str, Any]:
        prompt = self._build_prompt(
            mode="shared_classroom",
            task=(
                "Hãy quyết định xem có nên đặt 1 câu hỏi cho lớp ở slide hiện tại hay không.\n"
                "Nếu nên hỏi, hãy hỏi đúng 1 câu ngắn gọn. Nếu không cần hỏi, dùng intent='wait'."
            ),
        )
        response = self._run_json_agent(self.student_agent, prompt)
        if response.get("reply"):
            self._record_history("Student Agent", response["reply"])
        return response

    def finish_shared_round(self, student_question: str, learner_answer: str | None) -> dict[str, Any]:
        if learner_answer:
            self._record_history("Learner", learner_answer)
            task = (
                "Trong lớp học chung, student agent vừa hỏi người học.\n"
                f"Câu hỏi: {student_question}\n"
                f"Câu trả lời của người học: {learner_answer}\n"
                "Hãy đánh giá câu trả lời theo đúng response contract."
            )
        else:
            task = (
                "Trong lớp học chung, student agent đã hỏi nhưng người học không trả lời kịp.\n"
                "timeout_status: timed_out\n"
                f"Câu hỏi cần TA trả lời thay: {student_question}\n"
                "Hãy trả lời thay cho lớp theo đúng response contract."
            )
        prompt = self._build_prompt(mode="shared_classroom", task=task)
        response = self._run_json_agent(self.ta_agent, prompt)
        self._record_history("TA", response.get("reply", ""))
        return response

    def start_private_student_round(self) -> dict[str, Any]:
        prompt = self._build_prompt(
            mode="private_student_chat",
            task=(
                "Bạn đang chat riêng với người học.\n"
                "Hãy hỏi đúng 1 câu ngắn gọn về slide hiện tại theo response contract."
            ),
        )
        response = self._run_json_agent(self.student_agent, prompt)
        if response.get("reply"):
            self._record_history("Student Agent", response["reply"])
        return response

    def finish_private_student_round(self, student_question: str, learner_answer: str | None) -> dict[str, Any]:
        if learner_answer:
            self._record_history("Learner", learner_answer)
            task = (
                "Trong chat riêng, bạn vừa hỏi người học.\n"
                f"Câu hỏi: {student_question}\n"
                f"Câu trả lời của người học: {learner_answer}\n"
                "Hãy đánh giá câu trả lời theo đúng response contract."
            )
        else:
            task = (
                "Trong chat riêng, người học không trả lời kịp.\n"
                "timeout_status: timed_out\n"
                f"Câu hỏi: {student_question}\n"
                "Hãy phản hồi ngắn gọn theo response contract."
            )
        prompt = self._build_prompt(mode="private_student_chat", task=task)
        response = self._run_json_agent(self.student_agent, prompt)
        if response.get("reply"):
            self._record_history("Student Agent", response["reply"])
        return response

    def generate_material(self, material_type: str, instructions: str = "") -> dict[str, Any]:
        material_type = material_type.strip().lower()
        if material_type not in {"quiz", "flashcard", "mindmap"}:
            raise ValueError("material_type must be quiz, flashcard, or mindmap")

        prompt = self._build_prompt(
            mode="learning_material_generation",
            task=(
                "Người học muốn tạo học liệu từ phần đã học.\n"
                f"requested_material_type: {material_type}\n"
                f"additional_instructions: {instructions.strip() or '(none)'}\n"
                "Bắt buộc dùng tool generate_learning_material."
            ),
        )
        initial_run = self.learning_material_agent.run([{"role": "user", "content": prompt}], tool_choice="required")
        final_response = self._finalize_tool_run(self.learning_material_agent, prompt, initial_run)
        parsed_response = _parse_json_response(final_response.text)
        if not parsed_response:
            parsed_response = _fallback_material_payload(initial_run.tool_results, material_type)
        return {
            "agent_response": parsed_response,
            "tool_calls": [{"name": call.name, "args": call.args} for call in initial_run.tool_calls],
            "tool_results": initial_run.tool_results,
        }

    def _build_prompt(self, *, mode: str, task: str) -> str:
        slide = self.get_current_slide()
        history = "\n".join(f"- {entry}" for entry in self.chat_history[-10:]) or "- (no recent turns)"
        return (
            "Trusted classroom state\n"
            f"- mode: {mode}\n"
            f"- current_position: slide {slide.number}\n"
            f"- current_slide_title: {slide.title}\n"
            f"- source_file: {self.deck.source_path.name}\n"
            f"- markdown_file: {self.deck.markdown_path.name}\n"
            f"- chat_history:\n{history}\n\n"
            "current_segment\n"
            f"## Slide {slide.number} — {slide.title}\n\n{slide.content}\n\n"
            "covered_content\n"
            f"{self.deck.covered_content(slide.number)}\n\n"
            "Task\n"
            f"{task}"
        )

    def _run_json_agent(self, agent: Agent, prompt: str) -> dict[str, Any]:
        run = agent.run([{"role": "user", "content": prompt}])
        payload = _parse_json_response(run.text)
        if not payload:
            payload = {
                "intent": "raw_text",
                "action": "reply",
                "reply": (run.text or "").strip(),
                "citations": [],
            }
        return payload

    def _finalize_tool_run(self, agent: Agent, prompt: str, initial_run: AgentRun) -> AgentRun:
        if not initial_run.tool_results:
            return initial_run
        tool_results_json = json.dumps(initial_run.tool_results, ensure_ascii=False, indent=2)
        final_agent = Agent(
            self.provider,
            system_prompt=agent.system_prompt,
            model=agent.model,
        )
        follow_up_messages = [
            {"role": "user", "content": prompt},
            {
                "role": "assistant",
                "content": initial_run.text or "Tool call executed.",
            },
            {
                "role": "user",
                "content": (
                    "Trusted tool results\n"
                    f"{tool_results_json}\n\n"
                    "Dựa CHỈ trên trusted tool results ở trên, hãy trả response contract cuối cùng."
                ),
            },
        ]
        final_run = final_agent.run(follow_up_messages)
        return AgentRun(
            text=final_run.text,
            tool_calls=initial_run.tool_calls,
            tool_results=initial_run.tool_results,
        )

    def _record_history(self, speaker: str, message: str) -> None:
        cleaned = message.strip()
        if not cleaned:
            return
        self.chat_history.append(f"{speaker}: {cleaned}")
        self.chat_history = self.chat_history[-10:]


class MockProvider:
    """Useful for offline smoke tests and demos without live API keys."""

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        del model, temperature, tool_choice
        prompt = messages[-1]["content"]
        if "Trusted tool results" in prompt:
            return ModelResponse(
                text=json.dumps({
                    "intent": "generate_material",
                    "action": "return_material",
                    "reply": "Da tao hoc lieu thanh cong.",
                    "evidence_ids": ["generate_learning_material"],
                }, ensure_ascii=False)
            )
        if tools:
            return ModelResponse(
                text=None,
                tool_calls=[ToolCall(name="generate_learning_material", args={
                    "material_type": "quiz",
                    "title": "Mock Quiz",
                    "language": "vi",
                    "covered_until": "slide 1",
                    "instructions": "",
                    "quiz_items": [{
                        "question": "Slide nay noi ve gi?",
                        "options": ["A", "B"],
                        "correct_option": "A",
                        "explanation": "Mock explanation",
                        "citations": ["slide 1"],
                    }],
                })],
            )
        if "không trả lời kịp" in prompt or "timed_out" in prompt:
            return ModelResponse(text=json.dumps({
                "intent": "answer_after_timeout",
                "action": "step_in",
                "reply": "Het thoi gian, TA tra loi thay.",
                "citations": ["slide 1"],
            }, ensure_ascii=False))
        if "đánh giá câu trả lời" in prompt:
            return ModelResponse(text=json.dumps({
                "intent": "evaluate_answer",
                "action": "grade",
                "reply": "dung - Cau tra loi bam sat noi dung slide.",
                "citations": ["slide 1"],
            }, ensure_ascii=False))
        if "chat riêng với TA" in prompt:
            return ModelResponse(text=json.dumps({
                "intent": "answer_question",
                "action": "answer",
                "reply": "TA giai thich ngan gon theo slide hien tai.",
                "citations": ["slide 1"],
            }, ensure_ascii=False))
        return ModelResponse(text=json.dumps({
            "intent": "ask_question",
            "action": "ask",
            "reply": "Ban co the tom tat y chinh cua slide nay khong?",
            "citations": ["slide 1"],
        }, ensure_ascii=False))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI simulated classroom for slide-based lectures.")
    parser.add_argument("--provider", default="openai", help="openai | openrouter | anthropic | gemini")
    parser.add_argument("--model", default=None, help="Optional model override.")
    parser.add_argument("--slide-file", default=None, help="Path to slide/PDF/markdown file.")
    parser.add_argument("--current-slide", type=int, default=None, help="Initial current slide number.")
    parser.add_argument("--ingested-dir", default=str(DEFAULT_INGEST_DIR), help="Where cached markdown is stored.")
    parser.add_argument("--mode", choices=["classroom", "single-agent"], default=None, help="Interactive mode.")
    parser.add_argument("--agent", choices=sorted(SINGLE_AGENT_CHOICES), default=None, help="Single-agent target.")
    parser.add_argument("--timeout-seconds", type=int, default=45, help="Answer timeout in seconds for student-led turns.")
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    load_lab_env(ROOT)
    _validate_live_provider(args.provider)

    slide_path = _resolve_slide_path(args.slide_file)
    markdown_path = ensure_slide_markdown(slide_path, Path(args.ingested_dir))
    deck = LectureDeck.from_markdown(slide_path, markdown_path)
    provider = make_provider(args.provider)
    session = ClassroomSession(deck=deck, provider=provider, model=args.model)

    initial_slide = args.current_slide or _prompt_for_slide(deck)
    session.set_current_slide(initial_slide)
    interaction_mode = args.mode or _prompt_for_mode()
    single_agent = _resolve_single_agent_choice(interaction_mode, args.agent)

    print(f"Loaded lecture: {deck.source_path.name}")
    print(f"Markdown cache: {deck.markdown_path}")
    print(session.describe_current_slide())
    print(_help_text(interaction_mode, single_agent))

    while True:
        prompt_label = f"{interaction_mode}"
        if interaction_mode == "single-agent" and single_agent:
            prompt_label += f":{single_agent}"
        raw = input(f"\n{prompt_label}> ").strip()
        if not raw:
            continue
        if raw in {"exit", "quit"}:
            print("Thoat classroom.")
            return
        if raw == "help":
            print(_help_text(interaction_mode, single_agent))
            continue
        if raw == "context":
            print(session.describe_current_slide())
            continue
        if raw == "mode":
            interaction_mode = _prompt_for_mode()
            single_agent = _resolve_single_agent_choice(interaction_mode, None)
            print(_help_text(interaction_mode, single_agent))
            continue
        if raw == "agent":
            if interaction_mode != "single-agent":
                print("Lenh nay chi dung trong single-agent mode.")
                continue
            single_agent = _prompt_for_single_agent()
            print(f"Da chuyen sang agent: {single_agent}")
            continue
        if raw.startswith("slide "):
            try:
                slide_no = int(raw.split(maxsplit=1)[1])
                slide = session.set_current_slide(slide_no)
            except (ValueError, IndexError) as exc:
                print(f"Khong doi duoc slide: {exc}")
                continue
            print(f"Da chuyen sang slide {slide.number}: {slide.title}")
            continue
        if interaction_mode == "classroom":
            if raw != "round":
                print("Classroom mode chi nhan: round, slide <n>, context, mode, help, exit.")
                continue
            _run_shared_classroom_round(session, timeout_seconds=args.timeout_seconds)
            continue
        assert single_agent is not None
        _handle_single_agent_command(
            session,
            single_agent=single_agent,
            raw=raw,
            timeout_seconds=args.timeout_seconds,
        )


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_json_response(text: str | None) -> dict[str, Any]:
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return {}
        try:
            parsed = json.loads(match.group(0))
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}


def _fallback_material_payload(tool_results: list[dict[str, Any]], material_type: str) -> dict[str, Any]:
    if not tool_results:
        return {}
    first_result = tool_results[0].get("result", {})
    evidence_id = first_result.get("title") or first_result.get("tool") or material_type
    return {
        "intent": "generate_material",
        "action": "return_material",
        "reply": f"Da tao {material_type} cho phan bai hoc hien tai.",
        "evidence_ids": [str(evidence_id)],
    }


def _print_agent_payload(agent_name: str, payload: dict[str, Any]) -> None:
    print(f"\n[{agent_name}]")
    print(payload.get("reply", "(khong co noi dung)"))
    citations = _normalize_display_refs(payload.get("citations") or payload.get("evidence_ids"))
    if citations:
        print(f"Citations: {', '.join(citations)}")
    if payload.get("intent"):
        print(f"Intent: {payload['intent']}")


def _print_material_result(result: dict[str, Any]) -> None:
    payload = result.get("agent_response") or {}
    if payload:
        _print_agent_payload("Learning Material Agent", payload)
    tool_results = result.get("tool_results", [])
    if not tool_results:
        print("Khong co tool result.")
        return
    final_result = tool_results[0].get("result", {})
    print("\n[Material Output]")
    print(
        f"type={final_result.get('material_type')} | "
        f"format={final_result.get('content_format')} | "
        f"items={final_result.get('item_count')}"
    )
    print(final_result.get("content", ""))


def _normalize_display_refs(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, (str, int, float)):
        text = str(raw).strip()
        return [text] if text else []
    if not isinstance(raw, list):
        text = str(raw).strip()
        return [text] if text else []
    normalized: list[str] = []
    for item in raw:
        if item is None:
            continue
        text = str(item).strip()
        if text:
            normalized.append(text)
    return normalized


def _help_text(interaction_mode: str, single_agent: str | None) -> str:
    common = (
        "\nCommands:\n"
        "  context                         Xem slide hien tai va trich doan noi dung\n"
        "  slide <n>                       Doi slide hien tai\n"
        "  mode                            Chuyen giua classroom / single-agent\n"
        "  help                            Xem huong dan\n"
        "  exit                            Thoat\n"
    )
    if interaction_mode == "classroom":
        return common + (
            "\nClassroom mode:\n"
            "  round                           Student Agent hoi, hoc vien tra loi, TA danh gia/tra loi thay\n"
        )
    agent_hint = single_agent or "ta"
    return common + (
        "\nSingle-agent mode:\n"
        "  agent                           Chon lai agent (ta | student | material)\n"
        f"  Agent hien tai: {agent_hint}\n"
        "  ta: go truc tiep cau hoi cho TA\n"
        "  student: go `round` de Student Agent hoi va cham bai\n"
        "  material: go `quiz [ghi_chu]`, `flashcard [ghi_chu]`, hoac `mindmap [ghi_chu]`\n"
    )


def _resolve_slide_path(raw_path: str | None) -> Path:
    if raw_path:
        candidate = Path(raw_path).expanduser()
        if candidate.exists():
            return candidate.resolve()
        if not candidate.is_absolute():
            rooted_candidate = (ROOT / raw_path).resolve()
            if rooted_candidate.exists():
                return rooted_candidate
        raise FileNotFoundError(f"Slide file not found: {candidate}")

    slide_files = sorted((ROOT / "data" / "slides").glob("*"))
    if not slide_files:
        raise FileNotFoundError("Khong tim thay file slide trong codebase/agents/data/slides")
    if len(slide_files) == 1:
        return slide_files[0]

    print("Chon file slide:")
    for index, slide_file in enumerate(slide_files, start=1):
        print(f"  {index}. {slide_file.name}")
    while True:
        choice = input("Nhap so thu tu: ").strip()
        try:
            selected = slide_files[int(choice) - 1]
            return selected
        except (ValueError, IndexError):
            print("Lua chon khong hop le, thu lai.")


def _prompt_for_slide(deck: LectureDeck) -> int:
    while True:
        raw = input(f"Nhap slide hien tai (1-{deck.max_slide()}): ").strip()
        try:
            slide_number = int(raw)
            deck.get_slide(slide_number)
            return slide_number
        except (ValueError, TypeError):
            print("Slide khong hop le, thu lai.")


def _prompt_for_mode() -> str:
    while True:
        raw = input("Chon mode (`classroom` / `single-agent`): ").strip().lower()
        if raw in {"classroom", "single-agent"}:
            return raw
        print("Mode khong hop le, thu lai.")


def _prompt_for_single_agent() -> str:
    while True:
        raw = input("Chon agent (`ta` / `student` / `material`): ").strip().lower()
        if raw in SINGLE_AGENT_CHOICES:
            return raw
        print("Agent khong hop le, thu lai.")


def _resolve_single_agent_choice(interaction_mode: str, agent_name: str | None) -> str | None:
    if interaction_mode != "single-agent":
        return None
    if agent_name in SINGLE_AGENT_CHOICES:
        return agent_name
    return _prompt_for_single_agent()


def _run_shared_classroom_round(session: ClassroomSession, *, timeout_seconds: int) -> None:
    student_turn = session.start_shared_round()
    _print_agent_payload("Student Agent", student_turn)
    if student_turn.get("intent") == "wait":
        return
    answer = _input_with_timeout(
        f"Ban tra loi trong {timeout_seconds}s (de trong hoac het gio se de TA tra loi): ",
        timeout_seconds,
    )
    ta_turn = session.finish_shared_round(student_turn.get("reply", ""), answer)
    _print_agent_payload("TA", ta_turn)


def _handle_single_agent_command(
    session: ClassroomSession,
    *,
    single_agent: str,
    raw: str,
    timeout_seconds: int,
) -> None:
    if single_agent == "ta":
        response = session.ask_ta(raw)
        _print_agent_payload("TA", response)
        return

    if single_agent == "student":
        if raw != "round":
            print("Student mode dung lenh `round` de bat dau mot luot hoi dap.")
            return
        student_turn = session.start_private_student_round()
        _print_agent_payload("Student Agent", student_turn)
        if student_turn.get("intent") == "wait":
            return
        answer = _input_with_timeout(
            f"Ban tra loi trong {timeout_seconds}s (het gio thi agent se bao timeout): ",
            timeout_seconds,
        )
        student_feedback = session.finish_private_student_round(student_turn.get("reply", ""), answer)
        _print_agent_payload("Student Agent", student_feedback)
        return

    parts = raw.split(maxsplit=1)
    material_type = parts[0].lower()
    instructions = parts[1] if len(parts) > 1 else ""
    if material_type not in {"quiz", "flashcard", "mindmap"}:
        print("Material mode dung: quiz [ghi_chu] | flashcard [ghi_chu] | mindmap [ghi_chu]")
        return
    result = session.generate_material(material_type, instructions)
    _print_material_result(result)


def _input_with_timeout(prompt: str, timeout_seconds: int) -> str | None:
    print(prompt, end="", flush=True)
    try:
        ready, _, _ = select.select([sys.stdin], [], [], max(timeout_seconds, 1))
    except (OSError, ValueError):
        value = input()
        cleaned = value.strip()
        return cleaned or None
    if not ready:
        print()
        return None
    value = sys.stdin.readline().rstrip("\n")
    cleaned = value.strip()
    return cleaned or None


def _validate_live_provider(provider_name: str) -> None:
    if provider_name == "mock":
        raise ValueError("task2 yeu cau live provider; khong the chay voi mock.")
    env_var = LIVE_PROVIDER_ENVS.get(provider_name)
    if env_var and not os.getenv(env_var):
        raise RuntimeError(f"Missing API key env var for provider '{provider_name}': {env_var}")

    module_name = {
        "openai": "openai",
        "openrouter": "openai",
        "anthropic": "anthropic",
        "gemini": "google.genai",
    }[provider_name]
    if importlib.util.find_spec(module_name) is None:
        raise RuntimeError(
            f"Provider SDK for '{provider_name}' is not installed in this Python environment: {module_name}"
        )


if __name__ == "__main__":
    main()
