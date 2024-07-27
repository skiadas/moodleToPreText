from typing import Self
from xml.dom import Node
from xml.dom.minidom import parse

from moodle2pretext.question import Question, questionFromEntry
from moodle2pretext.utils import getFirst, getFirstText, getText
from moodle2pretext.utils.html import simplifyHTML


class Assignment:

  def __init__(self, name, intro, questions):
    self.name = name
    self.intro = simplifyHTML(intro)
    self.questions = questions

  @staticmethod
  def fromFile(filename, all_questions: list[Node]) -> Self:
    document = parse(filename)

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

    return Assignment(name, intro, questionsInOrder)
