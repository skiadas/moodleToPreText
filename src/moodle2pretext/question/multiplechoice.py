from dataclasses import dataclass
from typing import Self
from xml.dom import Node

from moodle2pretext.question.question import Question
from moodle2pretext.utils import getFirst, getFirstText, getFirstHtml


@dataclass
class Choice:
  statement: str
  feedback: str
  isCorrect: bool


class MultipleChoiceQuestion(Question):
  allowsMultipleAnswers: bool
  choices: list[Choice]

  def __init__(
      self,
      id: str,
      name: str,
      questionText: str,
      choices: list[Choice],
      allowMultipleAnswers: bool):
    super().__init__(id, name, questionText)
    self.choices = choices
    self.allowsMultipleAnswers = allowMultipleAnswers

  @staticmethod
  def fromEntry(questionEntry: Node) -> Self:
    choices = [
        makeChoice(node) for node in getFirst(
            questionEntry, ["plugin_qtype_multichoice_question", "answers"]).
        getElementsByTagName("answer")
    ]
    allowMultipleAnswers = int(
        getFirstText(
            questionEntry,
            ["plugin_qtype_multichoice_question", "multichoice", "single"
            ])) == 0

    return MultipleChoiceQuestion(
        id=questionEntry.getAttribute("id"),
        name=getFirstText(questionEntry, "name"),
        questionText=getFirstText(questionEntry, "questiontext"),
        choices=choices,
        allowMultipleAnswers=allowMultipleAnswers)


def makeChoice(node: Node) -> tuple[str, bool]:
  return Choice(
      getFirstHtml(node, "answertext"),
      getFirstHtml(node, "feedback"),
      float(getFirstText(node, "fraction")) > 0)
