from typing import Dict, Iterable, TextIO
from bs4 import BeautifulSoup
import re

from ptx_formatter import formatPretext

from moodle2pretext.question import *
from moodle2pretext.assignment import Assignment
from moodle2pretext.question.multiplechoice import Choice
from moodle2pretext.utils import yesOrNo

# Pattern for which characters in a ID are to be
# replaced by whitespace
PATTERN = re.compile(r"[\s:]+")


class PtxWriter:

  def __init__(self):
    self.soup = BeautifulSoup(features="xml")
    self.chapter = self.soup.new_tag("chapter")
    self.soup.append(self.chapter)
    self.seenIds = {}

  def process(self, assignments: list[Assignment]):
    self.chapter.extend(map(self.makeAssignment, assignments))

  def makeAssignment(self, assignment):
    exercisesTag = self.makeTag(
        "exercises", map(self.processQuestion, assignment.questions))
    return self.makeTag(
        "section",
        [
            self.makeTag("title", assignment.name),
            self.makeTag("introduction", assignment.intro),
            exercisesTag
        ],
        attrs={"xml:id": self.makeUniqueId("sec", assignment.name)})

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

  def processQuestion(self, question: Question) -> Node:
    exerciseTag = self.makeTag(
        "exercise",
        [
            self.makeTag("title", question.title),
            self.makeTag("statement", question.questionText)
        ],
        attrs={"xml:id": self.makeUniqueId("exer", question.name)})
    if isinstance(question, MatchingQuestion):
      exerciseTag.append(self.getMatchingQuestionParts(question))
    elif isinstance(question, MultipleChoiceQuestion):
      exerciseTag.append(self.getMCQuestionParts(question))
    elif isinstance(question, FillInQuestion):
      ...
    elif isinstance(question, CodeRunnerQuestion):
      ...
    return exerciseTag

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
