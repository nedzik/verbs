import random
from collections.abc import MutableMapping
from dataclasses import dataclass


def flatten(dictionary, parent_key='', separator=' '):
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten(value, new_key, separator=separator).items())
        else:
            items.append((new_key, value))
    return dict(items)


@dataclass
class Quiz:
    question: str
    correct_answer: str
    answer_choices: list[str]
    answered: bool = False
    answered_correctly: bool = False

    def answer(self, answer):
        self.answered = True
        if self.correct_answer == answer.strip():
            self.answered_correctly = True
        return self.answered_correctly


class SingleVerbChallenge:
    def __init__(self, verb: dict, focus: list):
        super().__init__()
        self.verb: dict[str, str] = flatten(verb)
        self.questions: list[str] = self.__focus_keys(self.verb.keys(), focus)
        self.size: int = len(self.questions)
        self.quizzes: list[Quiz] = []
        self.current_quiz: int = 0

    def start(self) -> None:
        self.quizzes = [self.__create_quiz() for x in range(self.size)]
        self.current_quiz: int = 0

    def get_current_quiz(self) -> Quiz:
        return self.quizzes[self.current_quiz] if self.current_quiz < len(self.quizzes) else None

    def advance_to_next_quiz(self):
        self.current_quiz += 1

    def get_answered_count(self) -> int:
        return sum([x.answered for x in self.quizzes])

    def get_answered_correctly_count(self) -> int:
        return sum([x.answered_correctly for x in self.quizzes])

    def get_error_count(self):
        return self.get_answered_count() - self.get_answered_correctly_count()

    def __create_quiz(self):
        answer_key = random.choice(self.questions)
        self.questions.remove(answer_key)
        answer = self.verb[answer_key]
        options = [answer] + random.sample(sorted(list(set(self.verb.values()))), 4)
        random.shuffle(options)
        return Quiz(answer_key, answer, options)

    @staticmethod
    def __is_in_focus(value, focus) -> bool:
        return any([x for x in focus if value.startswith(x)])

    @staticmethod
    def __focus_keys(keys, focus) -> list[str]:
        return [x for x in sorted(keys) if SingleVerbChallenge.__is_in_focus(x, focus)]
