from tarfile import open as tarOpen, TarFile
from typing import Self
from tempfile import TemporaryDirectory
import os
import shutil

from moodle2pretext.assignment import Assignment
from moodle2pretext.section import Section
from moodle2pretext.utils.ptx_writer import PtxWriter
from moodle2pretext.assetManager import AssetManager


class Course:

  assignments: list[Assignment]

  def __init__(self):
    pass

  @staticmethod
  def fromZip(zip_path: str) -> Self:
    course = Course()
    with tarOpen(zip_path, "r:gz") as tar:
      with TemporaryDirectory() as directory:
        course.prepareAssetManager(tar, directory)
        course.processAllQuestions()
        course.processAllAssignments(tar)
        course.processSections(tar)
        course.sortAssignmentsBySection()
        course.preparePtxResources(directory)
        outputDir = os.path.join(os.getcwd(), "outputs")
        shutil.copytree(directory, outputDir)
    return course

  def prepareAssetManager(self, tar: TarFile, directory: str):
    self.assetManager = AssetManager(tar, directory)

  def processAllQuestions(self):
    questionsDoc = self.assetManager.parseXML("questions.xml")
    self.questions = questionsDoc.getElementsByTagName("question_bank_entry")

  def processAllAssignments(self: Self, tar: TarFile) -> None:
    regex = r"activities/quiz_[0-9]+/quiz\.xml"

    self.assignments = [
        Assignment.fromFile(doc, self.questions)
        for doc in self.assetManager.parseList(regex)
    ]

  def processSections(self: Self, tar: TarFile) -> None:
    regex = r"sections/section_[0-9]+/section\.xml"
    self.sections = [
        Section.fromFile(doc)
        for doc in self.assetManager.parseList(regex)
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
    ptx_writer = PtxWriter(self.assetManager)
    ptx_writer.process(self.assignments)
    return ptx_writer.toString()

  def preparePtxResources(self: Self, directory: str) -> None:
    # TODO: Create different files and write them
    self.ptxString = self.toPretext()
    filename = os.path.join(directory, "exercises.ptx")
    with open(filename, "w") as f:
      f.write(self.ptxString)
