from typing import Self
from xml.dom import Node

from moodle2pretext.utils import getFirstText


class Section:

  def __init__(
      self: Self, number: int, name: str, summary: str, contents: list[str]):
    self.number = number
    self.name = name
    self.summary = summary
    self.contents = contents

  @staticmethod
  def fromFile(document: Node) -> Self:
    number = int(getFirstText(document, "number"))
    name = getFirstText(document, "name")
    summary = getFirstText(document, "summary")
    contents = getFirstText(document, "sequence").split(",")

    return Section(number, name, summary, contents)
