import random


class Quiz:
    def __init__(self, verb: dict, focus: list):
        super().__init__()
        self.verb = verb
        self.questions = self.__focus_keys(verb.keys(), focus)
        self.size = len(self.questions)
        self.quiz_iterator: iter = (self.create_quiz() for x in range(self.size))

    def create_quiz(self):
        answer = random.choice(self.questions)
        self.questions.remove(answer)
        options = [answer] + random.sample(sorted(self.verb.keys()), 4)
        random.shuffle(options)
        return answer, [self.verb[x] for x in options]

    @staticmethod
    def __is_in_focus(value, focus):
        return any([x for x in focus if value.startswith(x)])

    @staticmethod
    def __focus_keys(keys, focus):
        return [x for x in sorted(keys) if Quiz.__is_in_focus(x, focus)]
