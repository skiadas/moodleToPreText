from xml.dom import Node
from moodle2pretext.question.coderunner_question import CodeRunnerQuestion
from moodle2pretext.question.fillin import FillInQuestion
from moodle2pretext.question.matching_question import MatchingQuestion
from moodle2pretext.question.multiplechoice import MultipleChoiceQuestion
from moodle2pretext.question.question import Question
from moodle2pretext.utils import getLast, getFirstText


def questionFromEntry(entry: Node) -> Question:
  questionEntry = getLast(entry, "question")
  qType = getFirstText(questionEntry, "qtype")
  match qType:
    case "description":
      return Question.fromEntry(questionEntry)
    case "coderunner":
      return CodeRunnerQuestion.fromEntry(questionEntry)
    case "matchwiris":
      return MatchingQuestion.fromEntry(questionEntry)
    case "shortanswer":
      return FillInQuestion.fromShortAnswerEntry(questionEntry)
    case "numerical":
      return FillInQuestion.fromNumericalEntry(questionEntry)
    case "multichoice":
      return MultipleChoiceQuestion.fromEntry(questionEntry)
    case _:
      raise RuntimeError("Unknown question type (" + qType + ")!")
