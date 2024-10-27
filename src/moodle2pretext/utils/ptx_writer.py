from typing import Dict, Iterable
from urllib.parse import unquote, quote
from bs4 import BeautifulSoup
import bs4
import re

from ptx_formatter import formatPretext

from moodle2pretext.question import *
from moodle2pretext.assignment import Assignment
from moodle2pretext.question.multiplechoice import Choice
from moodle2pretext.utils import yesOrNo
from moodle2pretext.utils.code_writer import CodeWriter
from moodle2pretext.assetManager import AssetManager

# Pattern for which characters in a ID are to be
# replaced by whitespace
PATTERN = re.compile(r"[\s:]+")
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
    exerciseTag = self.makeTag(
        "exercise",
        [
            self.makeTag("title", question.title),
            self.makeTag("statement", question.questionText)
        ],
        attrs={
            "xml:id": self.makeUniqueId("exer", question.name),
            "label": f"exe-{assignmentId}-{question.id}"
        })
    if isinstance(question, MatchingQuestion):
      exerciseTag.append(self.getMatchingQuestionParts(question))
    elif isinstance(question, MultipleChoiceQuestion):
      exerciseTag.append(self.getMCQuestionParts(question))
    elif isinstance(question, FillInQuestion):
      ...
    elif isinstance(question, CodeRunnerQuestion):
      exerciseTag.append(self.getCodeRunnerParts(question))
    exerciseTag = self.fixAssetLinks(exerciseTag, question.id)
    return exerciseTag

  def fixAssetLinks(
      self, node: bs4.element.Tag, questionId: int) -> bs4.element.Tag:
    for el in node.find_all("image"):
      srcLink = el.attrs["source"]
      fileMatch = FILE_MATCHER.match(srcLink)
      if fileMatch is not None:
        filepath = unquote(fileMatch.group(1))
        newFilePath = self.assetManager.locateResource(questionId, filepath)
        el.attrs["source"] = quote(newFilePath)
    return node

  def getMatchingQuestionParts(self, question: MatchingQuestion) -> Node:
    return self.makeTag("matches", map(self.makeMatch, question.matches))

  def makeMatch(self, match: tuple[str, str]) -> Node:
    premise, response = match
    return self.makeTag(
        "match",
        [self.makeTag("premise", premise), self.makeTag("response", response)])

  def getMCQuestionParts(self, question: MultipleChoiceQuestion) -> Node:
    return self.makeTag(
        "choices",
        map(self.makeChoice, question.choices),
        {"multiple-correct": yesOrNo(question.allowsMultipleAnswers)})


# TODO: Allow other languages?

  def getCodeRunnerParts(self, question: CodeRunnerQuestion) -> Node:
    return self.makeTag(
        "program",
        [
            self.makeTag("input", [self.codeWriter.getInput(question)]),
            self.makeTag("tests", [self.codeWriter.getTests(question)])
        ], {
            "language": "python", "interactive": "activecode"
        })

  def makeChoice(self, choice: Choice) -> Node:
    return self.makeTag(
        "choice",
        [
            self.makeTag("statement", choice.statement),
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
