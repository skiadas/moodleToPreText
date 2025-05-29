from dataclasses import dataclass
from typing import Self, Optional
from xml.dom import Node
from moodle2pretext.question.question import Question
from moodle2pretext.utils import getFirst, getFirstText


class TestCase:
  testCode: str
  expected: str
  stdInput: str
  useAsExample: bool
  show: bool

  def __init__(
      self,
      testCode: str,
      expected: str,
      stdInput: str,
      useAsExample: bool = False,
      show: bool = True):
    self.testCode = testCode
    self.expected = expected
    self.stdInput = stdInput
    self.useAsExample = useAsExample
    self.show = show

  def __repr__(self) -> str:
    return f"""TestCase(
    code='{self.testCode}',
    stdin='{self.stdInput}',
    expected='{self.expected}',
    example={self.useAsExample},
    display={self.show})"""

  @staticmethod
  def fromNode(tc: Node) -> Self:
    return TestCase(
        getFirstText(tc, "testcode"),
        getFirstText(tc, "expected"),
        getFirstText(tc, "stdin"),
        getFirstText(tc, "useasexample") == "1",
        getFirstText(tc, "display") == "SHOW")


class CodeRunnerQuestion(Question):
  type: str  # python3 or ...
  preload: str
  answer: str  # the correct answer
  preamble: Optional[str]
  testCases: list[TestCase]  # Array of test cases

  def __init__(
      self,
      id: str,
      name: str,
      questionText: str,
      type: str,
      preload: str,
      answer: str,
      preamble: Optional[str],
      testCases: list[TestCase]):
    super().__init__(id, name, questionText)
    self.type = type
    self.preload = preload
    self.answer = answer
    self.preamble = preamble
    self.testCases = testCases

  def __str__(self):
    return (
        "name: " + self.name + "\n" + "text: " + self.questionText + "\n" +
        "type: " + self.type + "\n" + "preload: " + self.preload + "\n" +
        "testCases: " + str(len(self.testCases)))

  @staticmethod
  def fromEntry(questionEntry: Node) -> Self:
    template = getFirstText(questionEntry, ["coderunner_option", "template"])
    preamble = None
    if template != "$@NULL@$":
      index = template.find("{{ STUDENT_ANSWER }}")
      if (index != -1):
        preamble = template[0:index]
    return CodeRunnerQuestion(
        id=questionEntry.getAttribute("id"),
        name=getFirstText(questionEntry, "name"),
        questionText=getFirstText(questionEntry, "questiontext"),
        type=getFirstText(questionEntry, "coderunnertype"),
        preload=getFirstText(questionEntry, "answerpreload"),
        answer=getFirstText(questionEntry, "answer"),
        preamble=preamble,
        testCases=[
            TestCase.fromNode(tc)
            for tc in questionEntry.getElementsByTagName("coderunner_testcase")
        ])
