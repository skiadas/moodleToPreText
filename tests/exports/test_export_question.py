import unittest

from moodle2pretext.question import Question
from moodle2pretext.question.fillin import FillInQuestion
from moodle2pretext.question.matching_question import MatchingQuestion
from moodle2pretext.question.multiplechoice import Choice, MultipleChoiceQuestion
from moodle2pretext.utils.ptx_writer import PtxWriter


class TestExportQuestion(unittest.TestCase):

  def test_description(self):
    question = Question(
        "questionId",
        "the-question-name",
        "<h3>The title here</h3><p>The Question Text Goes Here</p>")
    node = PtxWriter(None).processQuestion(question)
    self.assertEqual("exercise", node.name)
    self.assertEqual("exer-the-question-name-1", node["xml:id"])
    self.assertEqual("The title here", node.title.get_text())
    self.assertEqual(
        "<p>The Question Text Goes Here</p>", node.statement.decode_contents())

  def test_matching(self):
    question = MatchingQuestion(
        "questionId",
        "name",
        "<p>text</p>",
        [
            ("premise1", "response1"), ("premise2", "response2"),
            ("premise3", "response3")
        ])
    node = PtxWriter(None).processQuestion(question)
    self.assertIsNotNone(node.matches)
    self.assertEqual(3, len(node.matches.contents))
    firstMatch = node.matches.contents[0]
    self.assertEqual("premise1", firstMatch.premise.decode_contents())
    self.assertEqual("response1", firstMatch.response.decode_contents())

  def test_multiple_choice(self):
    question = MultipleChoiceQuestion(
        "questionId",
        "name",
        "<p>text</p>",
        [
            Choice("choice1", "correct!", True),
            Choice("choice2", "wrong!", False),
            Choice("choice3", "wrong!", False)
        ],
        allowMultipleAnswers=False)
    node = PtxWriter(None).processQuestion(question)
    self.assertIsNotNone(node.choices)
    self.assertEqual(3, len(node.choices.contents))
    self.assertEqual("no", node.choices["multiple-correct"])
    self.assertEqual(
        "choice1", node.choices.contents[0].statement.decode_contents())
    self.assertEqual(
        "correct!", node.choices.contents[0].feedback.decode_contents())
    self.assertEqual("yes", node.choices.contents[0]["correct"])
    self.assertEqual(
        "choice2", node.choices.contents[1].statement.decode_contents())
    self.assertEqual(
        "wrong!", node.choices.contents[1].feedback.decode_contents())
    self.assertEqual("no", node.choices.contents[1]["correct"])
