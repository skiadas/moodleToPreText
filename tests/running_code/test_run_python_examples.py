import unittest

from moodle2pretext.question.coderunner_question import CodeRunnerQuestion, TestCase
from moodle2pretext.utils.python_code_runner import PythonCodeRunner


class TestQuestionCreation(unittest.TestCase):

  def test_question_with_just_output(self):
    question = CodeRunnerQuestion(
        "id",
        "Q1",
        "Print your name",
        "python?!?",
        "",
        """print('Haris')""",
        "", [TestCase("", "Haris", "", True)])
    runner = PythonCodeRunner()
    cases = runner.runExampleCases(question)
    self.assertEqual(len(cases), 1)
    self.assertEqual(cases[0], ("", "", "Haris"))

  def test_question_with_input_and_output(self):
    question = CodeRunnerQuestion(
        "id",
        "Q1",
        "Echo the input",
        "python?!?",
        "",
        """print("Hi " + input())""",
        "",
        [
            TestCase("", "Hi Haris", "Haris", True),
            TestCase("", "Hi Barb", "Barb", True),
            TestCase("", "Hi Theresa", "Theresa", False),
        ])
    runner = PythonCodeRunner()
    cases = runner.runExampleCases(question)
    self.assertEqual(len(cases), 2)
    self.assertEqual(cases[0], ("", "Haris", "Hi Haris"))
    self.assertEqual(cases[1], ("", "Barb", "Hi Barb"))

  def test_question_with_test_code(self):
    question = CodeRunnerQuestion(
        "id",
        "Q1",
        "Write a function that adds 2 to x",
        "python?!?",
        "",
        """def add(x):\n  return x + 2""",
        "",
        [
            TestCase("print(add(2))", "4", "", True),
            TestCase("print(add(6))", "8", "", True)
        ])
    runner = PythonCodeRunner()
    cases = runner.runExampleCases(question)
    self.assertEqual(len(cases), 2)
    self.assertEqual(cases[0], ("print(add(2))", "", "4"))
    self.assertEqual(cases[1], ("print(add(6))", "", "8"))

  def test_question_with_test_code_input_and_preamble(self):
    question = CodeRunnerQuestion(
        "id",
        "Q1",
        "Write a function that adds the given number to y",
        "python?!?",
        "",
        """
def add():
  x = int(input())
  return x + y
""",
        "y = 3",
        [
            TestCase("print(add())", "5", "2", True),
            TestCase("print(add())", "9", "6", True)
        ])
    runner = PythonCodeRunner()
    cases = runner.runExampleCases(question)
    self.assertEqual(len(cases), 2)
    self.assertEqual(cases[0], ("print(add())", "2", "5"))
    self.assertEqual(cases[1], ("print(add())", "6", "9"))
