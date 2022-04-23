import functools
import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Callable


def without_square_brackets(x: str) -> str:
    return re.sub(r"\[[^]]*]", "", x)


def without_round_brackets(x: str) -> str:
    return re.sub(r"\([^)]*\)", "", x)


def without_dash(x: str) -> str:
    return re.sub(r" *- ", " ", x)


def without_quoted_text(x: str) -> str:
    return re.sub(r'"[^"]*"', "", x)


def without_angle_brackets(x: str) -> str:
    return re.sub(r"<[^>]*>", "", x)


def with_reduced_spaces(x: str) -> str:
    return re.sub(r" +", " ", x)


def remove_new_line(x: str) -> str:
    return x.replace("\n", "").replace("\r", "").replace("\r\n", "")


def stripped(x: str) -> str:
    return x.strip()


def line_allowed_chars(x: str) -> str:
    return re.sub(r"[^(A-z가-힣 \d.,?!\"\':)]", "", x)


def word_allowed_chars(x: str) -> str:
    return re.sub(r"[^(A-z가-힣\d)]", "", x)


def solution_allowed_chars(x: str) -> str:
    return re.sub(r"[^(A-z가-힣\d )]", "", x)


def default_line_processors() -> List[Callable[[str], str]]:
    return [
        without_square_brackets,
        without_round_brackets,
        without_angle_brackets,
        without_dash,
        without_quoted_text,
        line_allowed_chars,
        with_reduced_spaces,
        stripped,
    ]


def default_word_processors() -> List[Callable[[str], str]]:
    return [word_allowed_chars]


def default_solution_processors() -> List[Callable[[str], str]]:
    return [solution_allowed_chars]


def default_extractors() -> List[str]:
    return [
        r"^<c\.korean><c\.bg_transparent>&lrm;(.*)</c\.bg_transparent></c\.korean>$",
        r"^<c\.korean><c\.bg_transparent>(.*)</c\.bg_transparent></c\.korean>$",
        r"^<c\.korean>(.*)</c\.korean>$",
    ]


def processed_string(line: str, processors: List[Callable[[str], str]]) -> str:
    return functools.reduce(lambda x, f: f(x), processors, line)


def standard_date(dt: datetime) -> str:
    return dt.strftime("%Y.%m.%d %H:%M:%S")


@dataclass(frozen=True)
class SrtConversionSettings:
    extractors: List[str]
    processors: List[Callable[[str], str]]
    one_line: bool


def extracted_sub(line: str, extractors: List[str]) -> str:
    if len(extractors) == 0:
        return ""
    extractor = re.search(extractors[0], line)
    if extractor is not None:
        return extractor.group(1)
    return extracted_sub(line, extractors[1:])
