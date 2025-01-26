"""Module that handles preparing code blocks for CodeRunner questions"""

from jinja2 import Environment, PackageLoader

from moodle2pretext.question.coderunner_question import CodeRunnerQuestion


class CodeWriter():

  def __init__(self) -> None:
    self.env = Environment(loader=PackageLoader("moodle2pretext.utils"))
    self.env.filters['indent'] = indent
    self.env.tests['is_python_program'] = is_python_program
    self.codeRunnerPreamble = self.env.get_template(
        "codeRunner-preamble.py.jinja")
    self.codeRunnerInput = self.env.get_template("codeRunner-code.py.jinja")
    self.codeRunnerPostamble = self.env.get_template(
        "codeRunner-postamble.py.jinja")
    self.codeRunnerTests = self.env.get_template("codeRunner-tests.py.jinja")

  def getPreamble(self, question: CodeRunnerQuestion):
    return self.codeRunnerPreamble.render(question=question, testing=False)

  def getPostamble(self, question: CodeRunnerQuestion):
    return self.codeRunnerPostamble.render(question=question, testing=False)

  def getInput(self, question: CodeRunnerQuestion):
    return self.codeRunnerInput.render(question=question, testing=False)

  def getTests(self, question: CodeRunnerQuestion):
    return self.codeRunnerTests.render(question=question, testing=False)


def indent(value, spaces: int | str = 4, includeFirstLine=False):
  if isinstance(spaces, int):
    spaces = " " * spaces
  result = ("\n" + spaces).join(value.split("\n"))
  if includeFirstLine:
    return spaces + result
  return result


def is_python_program(value):
  if isinstance(value, CodeRunnerQuestion):
    return value.testCases[0].testCode.strip() == ""
  else:
    raise RuntimeError(
        "Can only use 'is_python_program' on coderunner questions.")
