from typing import Self
from xml.dom import Node


from moodle2pretext.question import Question, questionFromEntry
from moodle2pretext.utils import getFirst, getFirstText, getText
from moodle2pretext.utils.html import simplifyHTML


class Assignment:

  def __init__(self, id, name, intro, questions):
    self.id = id
    self.name = name
    self.intro = simplifyHTML(intro)
    self.questions = questions

  @staticmethod
  def fromFile(document: Node, all_questions: list[Node]) -> Self:
    id = getFirst(document, "activity").attributes["moduleid"].value
    quizEl = getFirst(document, "quiz")
    name = getFirstText(quizEl, "name")
    intro = getFirstText(quizEl, "intro")
    qbEntries = [
        getText(entry)
        for entry in quizEl.getElementsByTagName("questionbankentryid")
    ]
    questions = {
        entry.getAttribute("id"): questionFromEntry(entry)
        for entry in all_questions
        if entry.getAttribute("id") in qbEntries
    }
    questionsInOrder = [questions[entry] for entry in qbEntries]

    return Assignment(id, name, intro, questionsInOrder)
