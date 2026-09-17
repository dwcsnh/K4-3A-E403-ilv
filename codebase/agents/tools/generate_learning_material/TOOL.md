---
name: generate_learning_material
track: core
kind: local_formatter
requires_env: []
inputs:
  [
    material_type,
    title,
    language,
    covered_until,
    instructions,
    quiz_items,
    flashcards,
    mindmap,
  ]
outputs:
  [
    material_type,
    title,
    language,
    covered_until,
    content_format,
    content,
    item_count,
    citations,
    status,
  ]
side_effect: false
---
# generate_learning_material

Serializes classroom study material into a stable machine-readable payload.

- `quiz` and `flashcard` outputs are JSON strings.
- `mindmap` output is an XML string.
- The tool validates that required fields exist for the selected
  `material_type`.
- The tool does not invent lecture content; the calling agent must provide only
  material grounded in covered lecture content and attach slide/timestamp
  citations.
