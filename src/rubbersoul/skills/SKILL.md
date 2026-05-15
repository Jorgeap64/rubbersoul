# Git Commit Skill

This project follows the Conventional Commits specification with a
structured commit message format.

## Commit Format

<type>(<scope>)!: <description>

<body>

BREAKING CHANGE: <breaking change description>

### Rules

- `type` is required.
- `scope` is optional.
- `!` indicates a breaking change.
- `description` must:
  - be imperative (`add`, `fix`, `remove`)
  - be lowercase
  - have no trailing period
  - be 50 characters or fewer
- `body` is optional:
  - use bullet points starting with `-`
  - explain **what** and **why**
  - avoid implementation details
- `BREAKING CHANGE` footer is required when introducing breaking changes.

---

## Allowed Types

| Type       | Purpose |
|------------|----------|
| feat       | New feature |
| fix        | Bug fix |
| docs       | Documentation only changes |
| style      | Formatting, whitespace, linting |
| refactor   | Code restructuring without behavior changes |
| perf       | Performance improvements |
| test       | Adding or updating tests |
| chore      | Maintenance tasks |
| ci         | CI/CD configuration |
| build      | Build system or dependency changes |

---

## Examples

### Feature

feat(auth): add oauth login support

- allow users to authenticate with github
- reduce friction during onboarding

### Bug Fix

fix(api): handle null response payload

- prevent crash when upstream service returns null
- improve resilience for partial failures

### Documentation

docs(readme): add local setup instructions

- document required environment variables
- clarify database initialization process

### Refactor

refactor(parser): simplify token handling

- reduce duplicated parsing logic
- improve maintainability of parser flow

### Breaking Change

feat(api)!: redesign authentication flow

- replace session authentication with jwt tokens
- unify auth handling across services

BREAKING CHANGE: session-based authentication has been removed

---

## Commit Message Checklist

Before committing, ensure:

- type is valid
- description is concise and imperative
- description is under 50 chars
- scope is meaningful if used
- body explains why the change exists
- breaking changes are clearly documented

---

## Reference Implementation

```python
class CommitMessage(BaseModel):
    type: Literal[
        "feat",
        "fix",
        "docs",
        "style",
        "refactor",
        "perf",
        "test",
        "chore",
        "ci",
        "build",
    ]

    scope: str | None = None

    description: str

    body: str | None = None

    breaking_change: str | None = None
```

This model formats commit messages as:

````sh
type(scope)!: description

- body bullet
- another bullet

BREAKING CHANGE: explanation
```
