import sys
from typing import Optional, Self
from xml.dom import Node

import bs4

from moodle2pretext.utils import getFirstText
from moodle2pretext.utils.html import pretextify, simplifyHTML


class Question:
  id: str  # the question id in the Moodle file
  name: str  # internal name
  questionText: str  # HTML escaped
  title: Optional[str] = None

  def __init__(self, id: str, name: str, questionText: str):
    self.id = id
    self.name = name
    questionText, title = processQuestionText(questionText)
    self.questionText = questionText
    self.title = title

  @staticmethod
  def fromEntry(questionEntry: Node) -> Self:
    return Question(
        id=questionEntry.getAttribute("id"),
        name=getFirstText(questionEntry, "name"),
        questionText=getFirstText(questionEntry, "questiontext"))


# TODO
def processQuestionText(text: str) -> tuple[str, str | None]:
  simplified = pretextify(text)
  soup = bs4.BeautifulSoup(simplified, "html.parser")
  firstTag = soup.contents[0]
  if (firstTag.name == "h3"):
    title = firstTag.get_text()
    firstTag.extract()
    return str(soup).strip(), title
  return simplified, "((Placeholder title))"
