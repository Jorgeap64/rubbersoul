from typing import Literal

from pydantic import BaseModel, Field

"""
===============================================================================

    Schema

===============================================================================
"""


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
    ] = Field(description="The type of change being committed")
    scope: str | None = Field(
        default=None,
        description="The module, component, or area of the"
        "codebase affected (e.g. 'auth', 'api', 'parser')",
    )
    description: str = Field(
        description="Short imperative summary of the change, max 50 chars",
        max_length=50,
    )
    body: str | None = Field(
        default=None, description="Bullet point started with '-' longer explanation of what and why, not how"
    )
    breaking_change: str | None = Field(
        default=None,
        description="Description of breaking change if any"
        "(becomes BREAKING CHANGE footer)",
    )

    def format(self) -> str:
        header = f"{self.type}"
        if self.scope:
            header += f"({self.scope})"
        if self.breaking_change:
            header += "!"
        header += f": {self.description}"

        parts = [header]
        if self.body:
            parts += ["", self.body]
        if self.breaking_change:
            parts += ["", f"BREAKING CHANGE: {self.breaking_change}"]

        return "\n".join(parts)
