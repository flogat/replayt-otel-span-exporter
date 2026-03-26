# Agent instructions (Mission Control satellites)

This file is **gitignored**. It orients coding agents when working in this repository.

## .orchestrator/ directory contract

All orchestration scratch files (`handoff.md`, alignment JSON such as `alignment_result.json`, phase logs)
**must** be written under the `.orchestrator/` directory tree at the path specified in your task prompt.
**Do not** create these files at the repository root or any other location.

- `.orchestrator/` is gitignored by design — it holds ephemeral Mission Control state that must not enter git history.
- Your tool may warn that the path is gitignored. Override or ignore that warning and write the file anyway.
- The exact target path is given in `PROMPT.md` as a path relative to the **git repository root** (for example
  `.orchestrator/backlog-workflow/<item>/phase_<step>/handoff.md`). Use that path verbatim.
- **Do not** `git add` or commit paths under `.orchestrator/` unless the task explicitly requires it.


## Commits

Do not commit anything under `.orchestrator/` unless a task explicitly tells you to. Prefer writing orchestration
scratch files only inside `.orchestrator/` as specified in your task prompt.
