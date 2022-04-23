import re
from enum import Enum

from trainer.models import Problem


# class Trainer:
#
#     def __init__(self, set_id, problem_number):
#         self.set_id = set_id
#         self.problem_number = 0 if problem_number is None else problem_number
#         self.problems = Problem.objects.all()
#
#     def get_next_problem(self):
#         next_problem = self.problems[self.problem_number]
#         self.problem_number = self.problem_number + 1
#         return next_problem

class ProblemType(Enum):
    all_missing = 1
    some_missing = 2


class SolvableProblem:

    def __init__(self, problem, hidden_word_positions, length_hint):
        self.problem_type = ProblemType.all_missing if hidden_word_positions is None or len(
            hidden_word_positions) <= 0 else ProblemType.some_missing
        self.problem = problem
        self.hidden_word_positions = hidden_word_positions
        if self.problem_type == ProblemType.some_missing:  # and len(hidden_word_positions) <= len(problem.sentence.split()):
            self.partial_solution = ""
            for i, word in enumerate(problem.sentence.split()):
                word = re.sub(r'[.,!?\'\u2026]*', '', word)
                self.partial_solution = self.partial_solution + " " + (
                    ("$" if not length_hint else ''.join(
                        map(lambda x: "#", word))) if i in hidden_word_positions else word)
