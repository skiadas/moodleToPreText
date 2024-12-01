from typing import Self
from xml.dom import Node

from moodle2pretext.question.multiplechoice import Choice, MultipleChoiceQuestion
from moodle2pretext.question.question import Question
from moodle2pretext.utils import getAll, getFirst, getFirstText, getFirstHtml, getText, isEmpty


class ExerciseGroupQuestion(Question):
  exercises: list[Question]

  def __init__(
      self,
      id: str,
      name: str,
      questionText: str,
      exercises: list[Question] = None):
    super().__init__(id, name, questionText)
    self.exercises = exercises if exercises is not None else []

  @staticmethod
  def fromMatchingCaseEntry(questionEntry: Node) -> Self:
    id = questionEntry.getAttribute("id")
    name = getFirstText(questionEntry, "name")
    return ExerciseGroupQuestion(
        id=id,
        name=name,
        questionText=getFirstText(questionEntry, "questiontext"),
        exercises=createSubExercises(
            getFirst(questionEntry, "matches"), id, name))


def createSubExercises(matchesEntry: Node, id: str,
                       name: str) -> list[MultipleChoiceQuestion]:
  allAnswers = [getText(m) for m in getAll(matchesEntry, "answertext")]
  actualEntries = [
      match for match in getAll(matchesEntry, "match")
      if (not isEmpty(getFirst(match, "questiontext")))
  ]
  return [
      MultipleChoiceQuestion(
          id=f"{id}-{index}",
          name=f"{name}-{index}",
          questionText=getFirstHtml(match, "questiontext"),
          choices=makeChoices(allAnswers, getFirstText(match, "answertext")),
          allowMultipleAnswers=False) for index,
      match in enumerate(actualEntries)
  ]


def makeChoices(answers: list[str], correct: str) -> Choice:
  return [
      Choice(statement=answer, feedback="", isCorrect=answer == correct)
      for answer in answers
  ]
