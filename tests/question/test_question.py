from os import path
import unittest
from xml.dom.minidom import parseString

from moodle2pretext.question import *
from moodle2pretext.question.multiplechoice import Choice


def readfile(filepath):
  return open(
      path.join(path.dirname(__file__), filepath), "r", encoding="utf-8")


class TestQuestionCreation(unittest.TestCase):

  def test_coderunner(self):
    node = parseFile("coderunner_example.xml")
    question: CodeRunnerQuestion = CodeRunnerQuestion.fromEntry(node)
    self.assertEqual("sum_2d_array", question.name)
    self.assertEqual("Sum Number Array", question.title)
    self.assertEqual("<p>Stuff here</p>", question.questionText)
    self.assertEqual("", question.preload)
    self.assertEqual("python3", question.type)
    self.assertEqual(7, len(question.testCases))
    self.assertEqual(
        "nums = [[3, 1], [4, 0], [-2, 5]]\n          print(sum_array(nums))",
        question.testCases[0].testCode)
    self.assertEqual("11\n", question.testCases[0].expected)
    self.assertTrue(question.testCases[0].show)
    self.assertFalse(question.testCases[0].useAsExample)
    self.assertEqual("", question.testCases[0].stdInput)

  def test_matching(self):
    node = parseFile("matching_example.xml")
    question: MatchingQuestion = MatchingQuestion.fromEntry(node)
    self.assertEqual("file_reading_match", question.name)
    self.assertEqual(
        """<p>Suppose <alert>pet_names.txt</alert> is the name</p>""",
        question.questionText)
    self.assertEqual(7, len(question.matches))
    self.assertEqual(
        "<pre>x = pets.readlines() # NOTICE the 's' on readlines</pre>",
        question.matches[0][0])
    self.assertEqual(
        """<p>x is a list of strings; x contains each line in pet_names.txt as a list item.</p>""",
        question.matches[0][1])

  def test_description(self):
    node = parseFile("description_example.xml")
    questionText = """<p><h3>Other Priority Queue Implementations</h3></p>"""
    question: Question = Question.fromEntry(node)
    self.assertEqual(
        "priority_queue_other_implementations_introduction", question.name)
    self.assertEqual(questionText, question.questionText)

  def test_multichoice(self):
    node = parseFile("multichoice_example.xml")
    questionText = """
<p><h3>Example: Directed Graph</h3></p>""".strip()
    question: MultipleChoiceQuestion = MultipleChoiceQuestion.fromEntry(node)
    self.assertEqual("digraph_shortest_path_mc", question.name)
    self.assertEqual(questionText, question.questionText)
    self.assertEqual(True, question.allowsMultipleAnswers)
    self.assertEqual(10, len(question.choices))
    self.assertEqual(Choice("<p>1</p>", "", True), question.choices[0])
    self.assertEqual(Choice("<p>2</p>", "", False), question.choices[1])

  def test_shortanswer(self):
    node = parseFile("shortanswer_example.xml")
    questionText = """<p>What is the <alert>name</alert> of the class</p>""".strip(
    )
    question: FillInQuestion = FillInQuestion.fromShortAnswerEntry(node)
    self.assertEqual("pogil_1a_classname", question.name)
    self.assertEqual(questionText, question.questionText)
    self.assertEqual(2, len(question.answers))
    self.assertEqual(("Sentence", ""), question.answers[0])
    self.assertEqual(
        (
            "sentence",
            """<p>Spell it exactly right, including capitalization.</p>"""),
        question.answers[1])

  def test_numerical(self):
    node = parseFile("numerical_example.xml")
    question: FillInQuestion = FillInQuestion.fromNumericalEntry(node)
    self.assertEqual("pogil_2a_main_num_objects", question.name)
    self.assertEqual("<p>In the question here</p>", question.questionText)
    self.assertEqual(2, len(question.answers))
    self.assertEqual(((2.0, 0.5), "Correct!"), question.answers[0])
    self.assertEqual(((4.0, 0.3), "Almost!"), question.answers[1])


def parseFile(filename: str) -> Node:
  with readfile(filename) as f:
    exampleXML = f.read()
    return parseString(exampleXML).getElementsByTagName("question")[0]
