import unittest
from unittest.mock import patch, DEFAULT

from quiz import Quiz, flatten, SingleVerbChallenge


class QuizTestCase(unittest.TestCase):
    def setUp(self):
        self.under_test = Quiz('indicatiu present jo', 'puc', ['puc', 'pot', 'pots', 'podem'])

    def test_initial_state(self):
        self.assertFalse(self.under_test.answered)
        self.assertFalse(self.under_test.answered_correctly)

    def test_answered_correctly(self):
        self.under_test.answer('puc')
        self.assertTrue(self.under_test.answered)
        self.assertTrue(self.under_test.answered_correctly)

    def test_answered_incorrectly(self):
        self.under_test.answer('pots')
        self.assertTrue(self.under_test.answered)
        self.assertFalse(self.under_test.answered_correctly)


class FlattenTestCase(unittest.TestCase):
    def test_primary_use_case(self):
        expected = {'gerundi': 'anant', 'indicatiu present jo': 'vaig'}
        self.assertEqual(expected, flatten({'gerundi': 'anant', 'indicatiu': {'present': {'jo': 'vaig'}}}))


class SingleVerbChallengeTestCase(unittest.TestCase):
    def setUp(self):
        self.verb = {
            'indicatiu': {'present': {'jo': 'vaig', 'tu': 'vas', 'nosaltres': 'anem', 'vosaltres': 'aneu'}},
            'subjuntiu': {'present': {'jo': 'vagi', 'tu': 'vagis', 'nosaltres': 'anem', 'vosaltres': 'aneu'}}
        }

    def test_filtering_by_focus(self):
        under_test = SingleVerbChallenge(self.verb, focus=['indicatiu present'])
        self.assertEqual(4, under_test.size)
        under_test = svc = SingleVerbChallenge(self.verb, focus=['indicatiu present', 'subjuntiu present'])
        self.assertEqual(8, under_test.size)

    @patch.multiple('random', choice=DEFAULT, sample=DEFAULT)
    def test_primary_use_case(self, choice, sample):
        under_test = SingleVerbChallenge(self.verb, focus=['indicatiu present'])
        choice.side_effect = [x for x in under_test.questions[:4]]
        sample.method.return_value = sorted(list(set(under_test.verb.values())))[:4]
        under_test.start()
        self.assertEqual(0, under_test.get_answered_count())
        self.assertEqual(0, under_test.get_answered_correctly_count())
        current_quiz = under_test.get_current_quiz()
        self.assertEqual('vaig', current_quiz.correct_answer)
        self.assertEqual('indicatiu present jo', current_quiz.question)
        self.assertTrue(current_quiz.answer('vaig'))
        self.assertEqual(1, under_test.get_answered_count())
        self.assertEqual(1, under_test.get_answered_correctly_count())
        self.assertEqual(0, under_test.get_error_count())
        under_test.advance_to_next_quiz()
        current_quiz = under_test.get_current_quiz()
        self.assertEqual('anem', current_quiz.correct_answer)
        self.assertEqual('indicatiu present nosaltres', current_quiz.question)
        self.assertFalse(current_quiz.answer('vaig'))
        self.assertEqual(2, under_test.get_answered_count())
        self.assertEqual(1, under_test.get_answered_correctly_count())
        self.assertEqual(1, under_test.get_error_count())
        under_test.advance_to_next_quiz()
        self.assertIsNotNone(under_test.get_current_quiz())
        under_test.advance_to_next_quiz()
        self.assertIsNotNone(under_test.get_current_quiz())
        under_test.advance_to_next_quiz()
        self.assertIsNone(under_test.get_current_quiz())


if __name__ == '__main__':
    unittest.main()
