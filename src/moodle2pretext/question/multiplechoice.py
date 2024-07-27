from typing import Self
from xml.dom import Node

from moodle2pretext.question.question import Question
from moodle2pretext.utils import getFirstText, getFirstHtml


class MultipleChoiceQuestion(Question):
  choices : list[tuple[str, bool]]

  def __init__(self, name: str, questionText: str, choices: list[tuple[str, bool]]):
    super().__init__(name, questionText)
    self.choices = choices

  @staticmethod
  def fromEntry(questionEntry: Node) -> Self:
    return MultipleChoiceQuestion(
      name=getFirstText(questionEntry, "name"),
      questionText=getFirstText(questionEntry, "questiontext"),
      choices=[
        makeChoice(node)
        for node in questionEntry.getElementsByTagName("answer")
      ]
    )

def makeChoice(node: Node) -> tuple[str, bool]:
  return (getFirstHtml(node, "answertext"),
          float(getFirstText(node, "fraction")) > 0)
