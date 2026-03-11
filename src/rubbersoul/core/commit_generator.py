import logging
import re

import tiktoken

from typing import Final

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from rubbersoul.utils.utils import SKILLS_DIR 
from rubbersoul.core.git_ops import get_git_diff
from rubbersoul.core.commit_schema import CommitMessage

"""
===============================================================================

    Generator 

===============================================================================
"""

log = logging.getLogger(__name__)

_MAX_TOKENS: Final[int] = 3000
_MAX_CHUNK_SIZE: Final[int] = 1500
_CHUNK_OVERLAP: Final[int] = 100

Str = StrOutputParser()
Json = JsonOutputParser()

map_prompt = ChatPromptTemplate.from_template(
    "Summarize the following text:\n\n{text}"
)

reduce_prompt = ChatPromptTemplate.from_template(
    "Combine these summaries into a final summary:\n\n{summaries}"
)

final_prompt = ChatPromptTemplate.from_template(
    "{skill}\nNow generate a structured conventional commit message for this diff:\n{diff}"
)

def compress_diff(diff: str) -> str:
    lines = diff.splitlines()
    filtered = []
    for line in lines:
        # Skip binary file notices, index hashes, timestamps
        if re.match(r'^(index |Binary files|old mode|new mode|\\ No newline)', line):
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
            separators=["\ndiff --git", "\n@@", "\n"]  # split on diff boundaries
            )
    chunks = splitter.split_text(diff)
    docs = [Document(page_content=chunk) for chunk in chunks]

    # map step
    map_chain = map_prompt | llm | Str
    summaries = map_chain.batch([{"text": doc.page_content} for doc in docs])

    # Reduce step
    reduce_chain = reduce_prompt | llm | Str
    final_summary = reduce_chain.invoke({
        "summaries": "\n".join(summaries)
    })
    
    return final_summary


def process_diff(llm, raw_diff: str, skill_tokens: int) -> str:
    compressed = compress_diff(raw_diff)
    token_count = count_tokens(compressed, llm.model) + skill_tokens
    log.info(f"Token count after compression: {token_count}")

    if token_count > _MAX_TOKENS:
        log.info(f"Context too large ({token_count} tokens > {_MAX_TOKENS}), summarizing...")
        result = summarize_diff(llm, compressed)
        return result
    else:
        return compressed 


def get_commit(llm) -> str:
    raw_diff = get_git_diff()
    with open(SKILLS_DIR) as f:
        skill = f.read()
    skill_tokens = count_tokens(skill, llm.model)
    diff = process_diff(llm, raw_diff, skill_tokens)

    struct_llm = llm.with_structured_output(CommitMessage)
    chain = final_prompt | struct_llm
    response = chain.invoke({
        "diff": diff,
        "skill": skill
    })
    result = response.format()
    log.info(f"Result: {result}...")
    return result
