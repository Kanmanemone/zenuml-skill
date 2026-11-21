# Missing export choices

Read this file only when format, scope, or document layout remains unresolved
after applying settings.

Ask every missing choice together in one structured call when available, or one
plain-text question otherwise. Never ask again for a value already stated.

## Resolution

- With `questions.enabled=false`, fill a missing value from its `defaults.*`.
  Ask only when the corresponding default is `none`.
- With `questions.enabled=true`, ask for each value the request did not state.
  Mark the option matching the resolved setting with ` (기본값)`; mark none when
  that setting is `none`. Do not reorder options.
- Page layout matters only while scope is `document` or unresolved. Ignore a
  layout answer when final scope is `diagram`.

## Questions

Use this order:

1. `출력 형식`: SVG, PNG, PDF. If scope is already `document`, offer only PDF
   and PNG.
2. `변환 범위`: 다이어그램만, 문서 전체. Explain that whole-document export
   supports PDF and PNG, not SVG.
3. `페이지 구성`: `1페이지 연속`, `표준 인쇄 규격`. State that it applies only
   to whole-document export.

If scope and format are asked together, keep SVG available because diagram-only
may still be chosen. If the final answers combine whole-document scope with SVG,
do not substitute silently: ask one second-round format question offering only
PDF and PNG. This incompatibility is the only reason for another question round.
