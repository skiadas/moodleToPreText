from typing import Dict, Iterable
from urllib.parse import unquote, quote
from bs4 import BeautifulSoup, NavigableString
import bs4
import re

from ptx_formatter import formatPretext

from moodle2pretext.question import *
from moodle2pretext.assignment import Assignment
from moodle2pretext.question.multiplechoice import Choice
from moodle2pretext.utils import yesOrNo
from moodle2pretext.utils.code_writer import CodeWriter
from moodle2pretext.utils.python_code_runner import PythonCodeRunner
from moodle2pretext.assetManager import AssetManager

# Pattern for which characters in a ID are to be
# replaced by dash
PATTERN = re.compile(r"[\W]+")
# Pattern to search for links to file assets
FILE_MATCHER = re.compile(r"@@PLUGINFILE@@/([^?\n]*)")


class PtxWriter:

  def __init__(self, assetManager: AssetManager):
    self.soup = BeautifulSoup(features="xml")
    self.seenIds = {}
    self.codeWriter = CodeWriter()
    self.assetManager = assetManager

  def createAssignmentFile(self, assignment: Assignment, filename: str) -> None:
    sectionTag = self.makeAssignment(assignment)
    ptxContents = formatPretext(str(sectionTag))
    self.assetManager.createSourceFile(filename, ptxContents)

  def generateAssignmentFiles(self, assignments: list[Assignment]):
    for idx, assignment in enumerate(assignments):
      filename = f"sec-{idx}-{self.makeIdLike(assignment.name)}.ptx"
      self.createAssignmentFile(assignment, filename)
      yield filename

  def generateChapter(self, assignments: list[Assignment]):
    yield self.makeTag("title", "Chapter Title")
    for filename in self.generateAssignmentFiles(assignments):
      yield self.makeTag("xi:include", "", {"href": f"./{filename}"})

  def createMainFile(self, chapter: Node) -> None:
    ptxTag = self.makeTag(
        "pretext",
        [self.makeTag("book", [self.makeTag("title", "Exercises"), chapter])], {
            "xml:lang": "en-US", "xmlns:xi": "http://www.w3.org/2001/XInclude"
        })
    self.assetManager.createSourceFile("main.ptx", formatPretext(str(ptxTag)))

  def process(self, assignments: list[Assignment]):
    chapter = self.makeTag("chapter", self.generateChapter(assignments))
    self.createMainFile(chapter)

  def makeAssignment(self, assignment):
    assignmentId = self.makeUniqueId("sec", assignment.name)
    exercisesTag = self.makeTag(
        "exercises",
        [self.processQuestion(q, assignmentId) for q in assignment.questions])
    return self.makeTag(
        "section",
        [
            self.makeTag("title", assignment.name),
            self.makeTag("introduction", assignment.intro),
            exercisesTag
        ],
        attrs={"xml:id": assignmentId})

  def toString(self) -> str:
    return formatPretext(str(self.soup))

  def makeTag(
      self,
      tagName: str,
      content: str | Iterable[Node],
      attrs: Dict[str, str] = {}) -> Node:
    tag = self.soup.new_tag(tagName, attrs=attrs)
    if isinstance(content, str):
      tag.append(BeautifulSoup(content, "html.parser"))
    else:
      tag.extend(content)
    return tag

  def processQuestion(
      self, question: Question, assignmentId: str) -> bs4.element.Tag:
    attrs = {
        "xml:id": self.makeUniqueId("exer", question.name),
        "label": f"exe-{assignmentId}-{question.id}"
    }

    if isinstance(question, ExerciseGroupQuestion):
      exerciseTag = self.makeTag("exercisegroup", [], attrs=attrs)
      if question.title is not None:
        exerciseTag.append(self.makeTag("title", question.title))
      exerciseTag.append(self.makeTag("introduction", question.questionText))
      for question in question.exercises:
        exerciseTag.append(self.processQuestion(question, assignmentId))
    else:
      exerciseTag = self.makeTag("exercise", [], attrs=attrs)
      if question.title is not None:
        exerciseTag.append(self.makeTag("title", question.title))
      exerciseTag.append(self.makeTag("statement", question.questionText))
      if isinstance(question, MatchingQuestion):
        exerciseTag.append(self.getMatchingQuestionParts(question))
      elif isinstance(question, MultipleChoiceQuestion):
        exerciseTag.append(self.getMCQuestionParts(question))
      elif isinstance(question, FillInQuestion):
        list(exerciseTag.children)[-1].extend(
            self.makeTag(
                "p",
                [
                    self.makeTag(
                        "fillin",
                        "", {
                            "answer": question.getCorrectAnswer(),
                            "width": "16"
                        })
                ]))
        exerciseTag.append(self.getFillinParts(question))
      elif isinstance(question, CodeRunnerQuestion):
        question.datafiles = self.assetManager.locateDatafiles(question.id)
        # Must extend the statement
        list(exerciseTag.children)[-1].extend(
            self.getCodeRunnerExamples(question))
        exerciseTag.append(self.getCodeRunnerParts(question))
    exerciseTag = self.fixAssetLinks(exerciseTag, question.id)
    return exerciseTag

  def fixAssetLinks(
      self, node: bs4.element.Tag, questionId: int) -> bs4.element.Tag:
    for el in node.find_all("image"):
      itemId = int(el.attrs.get("itemid", questionId))
      srcLink = el.attrs["source"]
      fileMatch = FILE_MATCHER.match(srcLink)
      if fileMatch is not None:
        filepath = unquote(fileMatch.group(1))
        newFilePath = self.assetManager.locateResource(itemId, filepath)
        el.attrs["source"] = quote(newFilePath)
        el.attrs.pop("itemid", None)
    return node

  def getMatchingQuestionParts(self, question: MatchingQuestion) -> Node:
    return self.makeTag("matches", map(self.makeMatch, question.matches))

  def makeMatch(self, match: tuple[str, str]) -> Node:
    premise, response = match
    return self.makeTag(
        "match",
        [self.makeTag("premise", premise), self.makeTag("response", response)])

  def getFillinParts(self, question: FillInQuestion) -> Node:
    answers = [
        self.makeFillinAnswer(answer, i == 0)
        for (i, answer) in enumerate(question.answers)
    ]
    return self.makeTag("evaluation", [self.makeTag("evaluate", answers)])

  def makeFillinAnswer(self, answer, isCorrect):
    (cond, feedback) = answer
    feedbackTag = self.makeTag("feedback", feedback)
    if isinstance(cond, tuple):  # numerical answer
      (value, tolerance) = cond
      comparison = self.makeTag(
          "numcmp", "", {
              "value": value, "tolerance": tolerance
          })
    else:
      comparison = self.makeTag("strcmp", cond)
    return self.makeTag(
        "test", [comparison, feedbackTag],
        {"correct": "yes"} if isCorrect else {})

  def getMCQuestionParts(self, question: MultipleChoiceQuestion) -> Node:
    return self.makeTag(
        "choices",
        map(self.makeChoice, question.choices),
        {
            "multiple-correct": yesOrNo(question.allowsMultipleAnswers),
            "randomize": "yes"
        })


# TODO: Allow other languages?

  def getCodeRunnerExamples(self, question: CodeRunnerQuestion) -> list[Node]:
    results = PythonCodeRunner().runExampleCases(question)

    if len(results) == 0:
      return [self.makeTag("p", "For example:")]

    includeTestCode = results[0][0] != ""
    includeInput = results[0][1] != ""
    mask = [includeTestCode, includeInput, True]

    def choose(lst):
      return [a for a, include in zip(lst, mask) if include]

    def precodify(s):
      return self.makeTag("p", [self.makeTag("cd", [NavigableString(s)])])

    if not includeTestCode:
      columnWidths = [0, 30, 70]
    elif not includeInput:
      columnWidths = [40, 0, 60]
    else:
      columnWidths = [40, 20, 40]

    def cell(s):
      return self.makeTag("cell", s, {"bottom": "minor", "right": "minor"})

    def codeCell(s):
      attrs = {"bottom": "minor", "right": "minor"}
      return self.makeTag("cell", [precodify(s)], attrs)

    def col(w):
      return self.makeTag("col", [], {"width": f"{w}%", "top": "minor"})

    def row(lst, header=False):
      attrs = {"left": "minor", "header": "yes" if header else "no"}
      return self.makeTag("row", choose(lst), attrs)

    cols = choose([col(width) for width in columnWidths])
    header = row([cell("Test"), cell("Input"), cell("Result")], True)
    rows = [
        row([codeCell(testCode), codeCell(stdinput), codeCell(result)])
        for (testCode, stdinput, result) in results
    ]

    return [
        self.makeTag("p", "For example:"),
        self.makeTag("tabular", [*cols, header, *rows])
    ]

  def getCodeRunnerParts(self, question: CodeRunnerQuestion) -> Node:
    return self.makeTag(
        "program",
        [
            self.makeTag(
                "preamble", [self.codeWriter.getPreamble(question)],
                {"visible": "no"}),
            self.makeTag("code", [self.codeWriter.getInput(question)]),
            self.makeTag(
                "postamble", [self.codeWriter.getPostamble(question)],
                {"visible": "no"}),
            self.makeTag("tests", [self.codeWriter.getTests(question)])
        ], {
            "language": "python", "interactive": "activecode"
        })

  def makeChoice(self, choice: Choice) -> Node:
    return self.makeTag(
        "choice",
        [
            self.makeTag("statement", [self.makeTag('p', choice.statement)]),
            self.makeTag("feedback", choice.feedback)
        ],
        attrs={"correct": yesOrNo(choice.isCorrect)})

  def makeUniqueId(self, prefix: str, id: str) -> str:
    encodedId = self.makeIdLike(id)
    counter = self.seenIds.setdefault(encodedId, 0) + 1
    self.seenIds[encodedId] = counter
    return "-".join([prefix, encodedId, str(counter)])

  def makeIdLike(self, s: str) -> str:
    return PATTERN.sub("-", s)
