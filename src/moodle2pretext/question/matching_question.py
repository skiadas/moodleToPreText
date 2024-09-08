from dataclasses import dataclass
from typing import Self
from xml.dom import Node
from moodle2pretext.question.question import Question
from moodle2pretext.utils import getFirst, getFirstHtml, getFirstText


class MatchingQuestion(Question):
  matches: list[tuple[str, str]]

  def __init__(
      self,
      id: str,
      name: str,
      questionText: str,
      matches: list[tuple[str, str]]):
    super().__init__(id, name, questionText)
    self.matches = matches

  @staticmethod
  def fromEntry(questionEntry: Node) -> Self:
    return MatchingQuestion(
        id=questionEntry.getAttribute("id"),
        name=getFirstText(questionEntry, "name"),
        questionText=getFirstText(questionEntry, "questiontext"),
        matches=createMatches(getFirst(questionEntry, "matches")))


def createMatches(matchesEntry: Node) -> list[tuple[str, str]]:
  return [
      (getFirstHtml(m, "questiontext"), getFirstHtml(m, "answertext"))
      for m in matchesEntry.getElementsByTagName("match")
  ]
