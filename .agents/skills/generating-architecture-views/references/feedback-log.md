# Feedback log fallback

Read this file only when `append_feedback.py` fails or another task cites a log.

## Manual fallback

Append the saved view exactly as it exists after `build_diagram.py` and before
`apply_hover.py`:

````markdown
## Round N — <ISO date>
**Request**: <all relevant turns since the previous round, lightly edited>

**Response**:
<the saved view>
````

Initial generation and a colliding new slug start a fresh Round 1. Regeneration
keeps every existing round and appends the next number. If the configured log
location has no log, start Round 1 there. Never summarize, analyze, or prune old
rounds.

The request includes only turns that shaped the view, including purpose
clarification. Leave unrelated conversation out.

## Citation

Logs remain ignored unless another task actually reads and cites one. At that
point stage only that log with `git add -f <log path>`. Never move old logs when
`log.directory` changes and never change `.gitignore` for a custom log location.
