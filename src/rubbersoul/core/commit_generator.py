import logging
import re

import tiktoken
from langchain_core.documents import Document
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rubbersoul.core.commit_schema import CommitMessage
from rubbersoul.core.git_ops import get_git_diff
from rubbersoul.utils.utils import SKILLS_DIR
from rubbersoul.config.config import (
    get_available_ram_gb,
    get_available_vram_gb,
)

"""
===============================================================================

    Generator

===============================================================================
"""

log = logging.getLogger(__name__)


def _resolve_macros() -> tuple[int, int, int]:
    ram_gb = get_available_ram_gb()
    vram_gb = get_available_vram_gb()
    effective_gb = ram_gb + vram_gb

    log.info(
        f"Hardware: {ram_gb:.1f} GB RAM free, {vram_gb:.1f} GB VRAM free "
        f"→ effective {effective_gb:.1f} GB"
    )

    if effective_gb >= 32:
        tier = "large"
        params = (24_000, 2_500, 200)
    elif effective_gb >= 16:
        tier = "medium"
        params = (16_000, 2_000, 150)
    elif effective_gb >= 8:
        tier = "default"
        params = (12_000, 1_500, 100)
    else:
        tier = "small"
        params = (6_000, 1_000, 50)

    log.info(
        f"Macro tier: {tier} → MAX_TOKENS={params[0]}, "
        f"MAX_CHUNK_SIZE={params[1]}, CHUNK_OVERLAP={params[2]}"
    )
    return params


_MAX_TOKENS, _MAX_CHUNK_SIZE, _CHUNK_OVERLAP = _resolve_macros()

Str = StrOutputParser()
Json = JsonOutputParser()

map_prompt = ChatPromptTemplate.from_template("Summarize the following text:\n\n{text}")

reduce_prompt = ChatPromptTemplate.from_template(
    "Combine these summaries into a final summary:\n\n{summaries}"
)

final_prompt = ChatPromptTemplate.from_template(
    "{skill}\nNow generate a structured conventional commit message"
    "for this diff:\n{diff}"
)


def compress_diff(diff: str) -> str:
    lines = diff.splitlines()
    filtered = []
    for line in lines:
        # Skip binary file notices, index hashes, timestamps
        if re.match(r"^(index |Binary files|old mode|new mode|\\ No newline)", line):
            continue
        # Skip blank context lines (lines starting with just a space)
        if line == " ":
            continue
        filtered.append(line)

    return "\n".join(filtered)


def count_tokens(text: str, model: str) -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")  # safe fallback for unknown models
    return len(enc.encode(text))


def summarize_diff(llm, diff: str) -> str:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=_MAX_CHUNK_SIZE,
        chunk_overlap=_CHUNK_OVERLAP,
        separators=["\ndiff --git", "\n@@", "\n"],  # split on diff boundaries
    )
    chunks = splitter.split_text(diff)
    docs = [Document(page_content=chunk) for chunk in chunks]

    # map step
    map_chain = map_prompt | llm | Str
    summaries = map_chain.batch([{"text": doc.page_content} for doc in docs])

    # Reduce step
    reduce_chain = reduce_prompt | llm | Str
    final_summary = reduce_chain.invoke({"summaries": "\n".join(summaries)})

    return final_summary


def process_diff(llm, raw_diff: str, skill_tokens: int) -> str:
    compressed = compress_diff(raw_diff)
    token_count = count_tokens(compressed, llm.model) + skill_tokens
    log.info(f"Token count after compression: {token_count}")

    if token_count > _MAX_TOKENS:
        log.info(
            f"Context too large ({token_count} tokens > {_MAX_TOKENS}), summarizing..."
        )
        result = summarize_diff(llm, compressed)
        return result
    else:
        return compressed


def get_commit(llm) -> str:
    raw_diff = get_git_diff()
    with SKILLS_DIR.open("r", encoding="utf-8") as f:
        skill = f.read()
    skill_tokens = count_tokens(skill, llm.model)
    diff = process_diff(llm, raw_diff, skill_tokens)

    struct_llm = llm.with_structured_output(CommitMessage)
    chain = final_prompt | struct_llm
    response = chain.invoke({"diff": diff, "skill": skill})
    log.info(f"CommitMessage obj: {response}...")
    result = response.format()
    return result
