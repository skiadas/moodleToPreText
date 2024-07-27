import re
from tarfile import open, TarFile
from typing import Self
from xml.dom.minidom import parse

from moodle2pretext.assignment import Assignment
from moodle2pretext.section import Section
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
      course.processSections(tar)
      course.sortAssignmentsBySection()
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

  def processSections(self: Self, tar: TarFile) -> None:
    prog = re.compile(r"sections/section_[0-9]+/section\.xml")
    self.sections = [
        Section.fromFile(tar.extractfile(tarInfo))
        for tarInfo in tar.getmembers()
        if prog.match(tarInfo.name)
    ]
    self.sections.sort(key=lambda s: s.number)

  def sortAssignmentsBySection(self: Self) -> None:
    assignmentsById = {
        assignment.id: assignment
        for assignment in self.assignments
    }

    orderedAssignments = [
        assignmentsById[contentId]
        for section in self.sections
        for contentId in section.contents
        if contentId in assignmentsById
    ]
    # Add to the end any assignments not present in sections
    for assignment in self.assignments:
      if assignment not in orderedAssignments:
        orderedAssignments.append(assignment)
    self.assignments = orderedAssignments

  def toPretext(self: Self) -> str:
    ptx_writer = PtxWriter()
    ptx_writer.process(self.assignments)
    return ptx_writer.toString()
