from dataclasses import dataclass
from typing import List, Union, Optional

from text.processing import remove_new_line, processed_string, default_word_processors
from trainer.models import Problem, Word


@dataclass(frozen=True)
class ProblemSolution:
    number: int
    wrong: str
    right: str


@dataclass(frozen=True)
class StatRecord:
    score: str
    last_played_date: str
    played: int
    success: int
    record_stats: str


def get_real_problem_no(set_id: int, fake_problem_number: int) -> int:
    all_problem_numbers = [k.problem_number for k in Problem.objects.filter(problem_set_id=set_id, active=True)]
    total_in_set = len(all_problem_numbers)
    problem_number = fake_problem_number % total_in_set
    return all_problem_numbers[problem_number]


def get_fake_problem_no(set_id: int, real_problem_number: int) -> int:
    all_problem_until_this = Problem.objects.filter(problem_set_id=set_id, problem_number__lt=real_problem_number).all()
    return len(all_problem_until_this)


def get_lines(file: Union[List[str], List[bytes], None]) -> List[str]:
    lines = []
    if file is None:
        return lines
    state = 0
    sentence = []
    for line in file:
        current_line = str(line, encoding="utf8") if not isinstance(line, str) else line
        if state == 2:
            if current_line in ["\r\n", "\n", "\r", ""]:
                state = 0
                sentence = " ".join(sentence)
                lines.append(sentence)
                sentence = []
            else:
                current_line = remove_new_line(current_line.rstrip())
                sentence.append(current_line)
        else:
            lines.append(remove_new_line(current_line))
            state = state + 1
    return lines


def guess_trans_line(start_time: float, end_time: float, trans_lines: List[str], time_delta: float) -> Optional[str]:
    for i, line in enumerate(trans_lines):
        if i % 3 == 1:
            trans_start_time, trans_end_time = timetext_to_time(line)
            if (
                start_time - time_delta <= trans_start_time <= start_time + time_delta
                or end_time - time_delta <= trans_end_time <= end_time + time_delta
            ):
                return trans_lines[i + 1]
    return None


def timetext_to_time(time_text: str) -> (float, float):
    def _parse_timestamp(timestamp: str) -> float:
        parts = timestamp.split(":")
        start_hour = int(parts[0])
        start_minute = int(parts[1])
        start_second = float(parts[2].replace(",", "."))
        return start_second + (60 * start_minute) + (3600 * start_hour)

    start_text, end_text = time_text.split(" --> ")
    return _parse_timestamp(start_text), _parse_timestamp(end_text)


def update_problem_score(problem: Problem) -> Problem:
    words_in_problem = [processed_string(k, default_word_processors()) for k in problem.sentence.split()]
    word_scores = []
    db_words = Word.objects.filter(id__in=words_in_problem).all()
    word_scores = []
    for word in db_words:
        word_scores.append((word.wrong / word.played) if word.played != 0 else 1)  # values between 0 and 1
    if len(word_scores) == 0:
        score_from_now = (problem.success_number / problem.played) if problem.played != 0 else 0
    else:
        score_from_now = 1 - (sum(word_scores) / len(word_scores))  # value between 0 and 1; the higher the better
    problem.score = score_from_now * (1 / problem.played) + problem.score * (1 - (1 / problem.played))
    # problem.score = score_from_now * 0.5 + problem.score * 0.5
    return problem
