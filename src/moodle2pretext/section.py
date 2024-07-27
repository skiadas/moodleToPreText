from typing import IO, Self
from xml.dom.minidom import parse

from moodle2pretext.utils import getFirstText


class Section:

  def __init__(
      self: Self, number: int, name: str, summary: str, contents: list[str]):
    self.number = number
    self.name = name
    self.summary = summary
    self.contents = contents

  @staticmethod
  def fromFile(file: IO[bytes]) -> Self:
    document = parse(file)

    number = int(getFirstText(document, "number"))
    name = getFirstText(document, "name")
    summary = getFirstText(document, "summary")
    contents = getFirstText(document, "sequence").split(",")

    return Section(number, name, summary, contents)
