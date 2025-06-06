from dataclasses import dataclass
from typing import Self, TypeAlias
from xml.dom import Node

from moodle2pretext.question.question import Question
from moodle2pretext.utils import getFirst, getFirstText
from moodle2pretext.utils.html import pretextify

# either a string RegEx or (number, tolerance)
conditionType: TypeAlias = str | tuple[float, float]


class FillInQuestion(Question):
  # Implicitly first answer is the "correct" one
  answers: list[tuple[conditionType, str]]  # (condition, feedback)

  def __init__(
      self,
      id: str,
      name: str,
      questionText: str,
      answers: list[tuple[conditionType, str]]):
    super().__init__(id, name, questionText)
    self.answers = answers

  def getCorrectAnswer(self):
    (cond, _) = self.answers[0]
    if isinstance(cond, str):
      return cond
    else:
      (value, _) = cond
      return value

  @staticmethod
  def fromShortAnswerEntry(questionEntry: Node) -> Self:
    return FillInQuestion(
        id=questionEntry.getAttribute("id"),
        name=getFirstText(questionEntry, "name"),
        questionText=getFirstText(questionEntry, "questiontext"),
        answers=makeShortAnswers(questionEntry.getElementsByTagName("answer")))

  @staticmethod
  def fromNumericalEntry(questionEntry: Node) -> Self:
    return FillInQuestion(
        id=questionEntry.getAttribute("id"),
        name=getFirstText(questionEntry, "name"),
        questionText=getFirstText(questionEntry, "questiontext"),
        answers=makeNumericalAnswers(
            getFirst(questionEntry, "answers"),
            getFirst(questionEntry, "numerical_records")))


def makeShortAnswers(answerNodes: list[Node]) -> list[tuple[str, str]]:
  triples = [
      (
          getFirstText(node, "answertext"),
          float(getFirstText(node, "fraction")),
          pretextify(getFirstText(node, "feedback"))) for node in answerNodes
  ]
  triples.sort(key=lambda tr: tr[1], reverse=True)
  return [(text, feedback) for (text, _, feedback) in triples]


def makeNumericalAnswers(
    answersNode: Node,
    numericalRecords: Node) -> list[tuple[tuple[float, float], str]]:
  answers = [
      (
          node.attributes["id"].value,
          float(getFirstText(node, "answertext")),
          float(getFirstText(node, "fraction")),
          pretextify(getFirstText(node, "feedback")))
      for node in answersNode.getElementsByTagName("answer")
  ]
  answers.sort(key=lambda tr: tr[2], reverse=True)
  tolerances = {
      getFirstText(node, "answer"): float(getFirstText(node, "tolerance"))
      for node in numericalRecords.getElementsByTagName("numerical_record")
  }

  return [
      ((number, tolerances[id]), feedback)
      for (id, number, _, feedback) in answers
  ]
