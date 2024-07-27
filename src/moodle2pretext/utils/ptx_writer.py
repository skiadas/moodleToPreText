from typing import TextIO
from bs4 import BeautifulSoup
import re

from ptx_formatter import formatPretext

from moodle2pretext.question import *
from moodle2pretext.assignment import Assignment

# Pattern for which characters in a ID are to be
# replaced by whitespace
PATTERN = re.compile(r"[\s:]+")


class PtxWriter:

    def __init__(self):
        self.soup = BeautifulSoup(features="xml")
        self.chapter = self.soup.new_tag("chapter")
        self.soup.append(self.chapter)
        self.seenIds = {}

    def process(self, assignments: list[Assignment]):
        for assignment in assignments:
            sectionTag = self.soup.new_tag(
                "section",
                attrs={"xml:id": self.makeUniqueId("sec", assignment.name)})
            self.chapter.append(sectionTag)
            sectionTag.append(self.makeTagFromHTML("title", assignment.name))
            sectionTag.append(
                self.makeTagFromHTML("introduction", assignment.intro))
            exercisesTag = self.soup.new_tag("exercises")
            sectionTag.append(exercisesTag)
            for question in assignment.questions:
                exercisesTag.append(self.processQuestion(question))

    def toString(self) -> str:
        return formatPretext(str(self.soup))

    def makeTagFromHTML(self, tagName: str, contentHTML: str) -> Node:
        tag = self.soup.new_tag(tagName)
        tag.append(BeautifulSoup(contentHTML, "html.parser"))
        return tag

    def processQuestion(self, question: Question) -> Node:
        exerciseTag = self.soup.new_tag(
            "exercise",
            attrs={"xml:id": self.makeUniqueId("exer", question.name)})
        exerciseTag.append(self.makeTagFromHTML("title", question.title))
        exerciseTag.append(
            self.makeTagFromHTML("statement", question.questionText))
        if isinstance(question, MatchingQuestion):
            self.addMatchingQuestionParts(exerciseTag, question)
        return exerciseTag

    def addMatchingQuestionParts(self, tag, question: MatchingQuestion) -> None:
        matchesTag = self.soup.new_tag("matches")
        tag.append(matchesTag)
        for premise, response in question.matches:
            matchTag = self.soup.new_tag("match")
            matchesTag.append(matchTag)
            matchTag.append(self.makeTagFromHTML("premise", premise))
            matchTag.append(self.makeTagFromHTML("response", response))

    def makeUniqueId(self, prefix: str, id: str) -> str:
        encodedId = self.makeIdLike(id)
        counter = self.seenIds.setdefault(encodedId, 0) + 1
        self.seenIds[encodedId] = counter
        return "-".join([prefix, encodedId, str(counter)])

    def makeIdLike(self, s: str) -> str:
        return PATTERN.sub("-", s)
