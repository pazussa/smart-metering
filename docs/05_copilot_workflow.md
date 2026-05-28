# Copilot Workflow

Use Copilot as a helper for small, reviewable tasks:

- Generate a function draft.
- Ask for edge cases.
- Ask for test ideas.
- Refactor a local block after tests exist.
- Explain a SQL query or protocol payload.

Control rules:

- Run `pytest` before accepting behavioral changes.
- Keep synthetic data marked as synthetic.
- Review SQL generated for destructive operations.
- Do not mix protocol experiments with core balance logic unless a test covers the change.

