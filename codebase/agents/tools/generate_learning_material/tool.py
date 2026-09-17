from __future__ import annotations

import json
from typing import Any
from xml.etree.ElementTree import Element, SubElement, tostring


SUPPORTED_MATERIAL_TYPES = {"quiz", "flashcard", "mindmap"}
SUPPORTED_LANGUAGES = {"vi", "en"}


def _require_non_empty(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _normalize_citations(raw: list[str] | None) -> list[str]:
    citations = [item.strip() for item in (raw or []) if item and item.strip()]
    return list(dict.fromkeys(citations))


def _serialize_quiz(
    *,
    title: str,
    language: str,
    covered_until: str,
    instructions: str,
    quiz_items: list[dict[str, Any]] | None,
) -> tuple[str, int, list[str]]:
    if not quiz_items:
        raise ValueError("quiz_items is required for material_type='quiz'")

    normalized_items: list[dict[str, Any]] = []
    all_citations: list[str] = []
    for index, item in enumerate(quiz_items, start=1):
        question = _require_non_empty(str(item.get("question", "")), f"quiz_items[{index}].question")
        options = [str(option).strip() for option in item.get("options", []) if str(option).strip()]
        if len(options) < 2:
            raise ValueError(f"quiz_items[{index}].options must contain at least 2 items")
        correct_option = _require_non_empty(
            str(item.get("correct_option", "")),
            f"quiz_items[{index}].correct_option",
        )
        if correct_option not in options:
            raise ValueError(f"quiz_items[{index}].correct_option must match one of the provided options")
        explanation = _require_non_empty(
            str(item.get("explanation", "")),
            f"quiz_items[{index}].explanation",
        )
        citations = _normalize_citations(item.get("citations"))
        normalized_items.append({
            "question": question,
            "options": options,
            "correct_option": correct_option,
            "explanation": explanation,
            "citations": citations,
        })
        all_citations.extend(citations)

    content = {
        "type": "quiz",
        "title": title,
        "language": language,
        "covered_until": covered_until,
        "instructions": instructions,
        "items": normalized_items,
    }
    return json.dumps(content, ensure_ascii=False, indent=2), len(normalized_items), _normalize_citations(all_citations)


def _serialize_flashcards(
    *,
    title: str,
    language: str,
    covered_until: str,
    instructions: str,
    flashcards: list[dict[str, Any]] | None,
) -> tuple[str, int, list[str]]:
    if not flashcards:
        raise ValueError("flashcards is required for material_type='flashcard'")

    normalized_cards: list[dict[str, Any]] = []
    all_citations: list[str] = []
    for index, card in enumerate(flashcards, start=1):
        front = _require_non_empty(str(card.get("front", "")), f"flashcards[{index}].front")
        back = _require_non_empty(str(card.get("back", "")), f"flashcards[{index}].back")
        citations = _normalize_citations(card.get("citations"))
        normalized_cards.append({
            "front": front,
            "back": back,
            "citations": citations,
        })
        all_citations.extend(citations)

    content = {
        "type": "flashcard",
        "title": title,
        "language": language,
        "covered_until": covered_until,
        "instructions": instructions,
        "items": normalized_cards,
    }
    return json.dumps(content, ensure_ascii=False, indent=2), len(normalized_cards), _normalize_citations(all_citations)


def _append_branch(parent: Element, node: dict[str, Any]) -> int:
    label = _require_non_empty(str(node.get("label", "")), "mindmap branch label")
    branch_el = SubElement(parent, "branch", {"label": label})
    citations = _normalize_citations(node.get("citations"))
    for citation in citations:
        citation_el = SubElement(branch_el, "citation")
        citation_el.text = citation

    count = 1
    for child in node.get("children", []) or []:
        count += _append_branch(branch_el, child)
    return count


def _collect_branch_citations(node: dict[str, Any]) -> list[str]:
    citations = _normalize_citations(node.get("citations"))
    for child in node.get("children", []) or []:
        citations.extend(_collect_branch_citations(child))
    return citations


def _serialize_mindmap(
    *,
    title: str,
    language: str,
    covered_until: str,
    instructions: str,
    mindmap: dict[str, Any] | None,
) -> tuple[str, int, list[str]]:
    if not mindmap:
        raise ValueError("mindmap is required for material_type='mindmap'")

    root_topic = _require_non_empty(str(mindmap.get("root_topic", "")), "mindmap.root_topic")
    branches = mindmap.get("branches", []) or []
    if not branches:
        raise ValueError("mindmap.branches must contain at least 1 branch")

    root = Element("mindmap", {
        "title": title,
        "language": language,
        "covered_until": covered_until,
    })
    if instructions:
        root.set("instructions", instructions)

    root_topic_el = SubElement(root, "root_topic")
    root_topic_el.text = root_topic

    root_citations = _normalize_citations(mindmap.get("citations"))
    for citation in root_citations:
        citation_el = SubElement(root, "citation")
        citation_el.text = citation

    branch_count = 0
    all_citations = list(root_citations)
    for branch in branches:
        branch_count += _append_branch(root, branch)
        all_citations.extend(_collect_branch_citations(branch))

    return tostring(root, encoding="unicode"), branch_count, _normalize_citations(all_citations)


def generate_learning_material(
    material_type: str,
    title: str,
    language: str = "vi",
    covered_until: str = "",
    instructions: str = "",
    quiz_items: list[dict[str, Any]] | None = None,
    flashcards: list[dict[str, Any]] | None = None,
    mindmap: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized_type = _require_non_empty(material_type, "material_type")
    if normalized_type not in SUPPORTED_MATERIAL_TYPES:
        raise ValueError(f"Unsupported material_type: {normalized_type}")

    normalized_title = _require_non_empty(title, "title")
    normalized_language = _require_non_empty(language, "language")
    if normalized_language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {normalized_language}")

    normalized_scope = _require_non_empty(covered_until, "covered_until")
    normalized_instructions = instructions.strip()

    if normalized_type == "quiz":
        content, item_count, citations = _serialize_quiz(
            title=normalized_title,
            language=normalized_language,
            covered_until=normalized_scope,
            instructions=normalized_instructions,
            quiz_items=quiz_items,
        )
        content_format = "json"
    elif normalized_type == "flashcard":
        content, item_count, citations = _serialize_flashcards(
            title=normalized_title,
            language=normalized_language,
            covered_until=normalized_scope,
            instructions=normalized_instructions,
            flashcards=flashcards,
        )
        content_format = "json"
    else:
        content, item_count, citations = _serialize_mindmap(
            title=normalized_title,
            language=normalized_language,
            covered_until=normalized_scope,
            instructions=normalized_instructions,
            mindmap=mindmap,
        )
        content_format = "xml"

    return {
        "tool": "generate_learning_material",
        "material_type": normalized_type,
        "title": normalized_title,
        "language": normalized_language,
        "covered_until": normalized_scope,
        "content_format": content_format,
        "content": content,
        "item_count": item_count,
        "citations": citations,
        "status": "success",
    }
