import re
from tarfile import open, TarFile
from typing import Self
from xml.dom.minidom import parse

from moodle2pretext.assignment import Assignment
from moodle2pretext.utils.ptx_writer import PtxWriter


class Course:

  def __init__(self):
    pass

  @staticmethod
  def fromZip(zip_path: str) -> Self:
    course = Course()
    with open(zip_path, "r:gz") as tar:
      course.processAllQuestions(tar)
      course.processAllAssignments(tar)
    return course

  def processAllQuestions(self, tar: TarFile):
    f = tar.extractfile("questions.xml")
    self.questions = parse(f).getElementsByTagName("question_bank_entry")

  def processAllAssignments(self: Self, tar: TarFile) -> None:
    prog = re.compile(r"activities/quiz_[0-9]+/quiz\.xml")
    self.assignments = [
        Assignment.fromFile(tar.extractfile(tarInfo), self.questions)
        for tarInfo in tar.getmembers()
        if prog.match(tarInfo.name)
    ]

  def toPretext(self: Self) -> str:
    ptx_writer = PtxWriter()
    ptx_writer.process(self.assignments)
    return ptx_writer.toString()
