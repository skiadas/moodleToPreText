import tarfile
import typer
import re
from xml.dom.minidom import parse
from moodle2pretext import Assignment
from moodle2pretext.utils.ptx_writer import PtxWriter

def main(zip_path: str, out_file: str):
  """
  Reads a Moodle backup file with path zip_path
  and produces a PreText output file with path out_file
  """
  with tarfile.open(zip_path, "r:gz") as tar:
    prog = re.compile(r"activities/quiz_[0-9]+/quiz\.xml")
    f = tar.extractfile("questions.xml")
    ALL_QUESTIONS_DOC = parse(f)
    ALL_QUESTIONS = ALL_QUESTIONS_DOC.getElementsByTagName("question_bank_entry")
    assignments = [
      Assignment.fromFile(tar.extractfile(tarInfo), ALL_QUESTIONS)
      for tarInfo in tar.getmembers()
      if prog.match(tarInfo.name)
    ]
    ptx_writer = PtxWriter()
    ptx_writer.process(assignments)
    with open(out_file, "w") as f:
      f.write(ptx_writer.toString())

if __name__ == "__main__":
    typer.run(main)

# main("sampleZip.zip", "example.ptx")

# tagNames = dict()
# styles = dict()

# from bs4 import BeautifulSoup as bs
# from moodle2pretext.question import *


# def collectTagsFromText(text: str):
#   soup = bs(text, "html.parser")
#   for tag in soup.find_all(True):
#     tagNames[tag.name] = tagNames.get(tag.name, 0) + 1
#     if "style" in tag.attrs:
#       key = tag.name + "#" + tag["style"]
#       styles[key] = styles.get(key, 0) + 1
#     # if tag.name in ["strong"]:
#     #   print(tag)

# def collectTagsFromQuestion(question: Question):
#   collectTagsFromText(question.questionText)
#   if isinstance(question, FillInQuestion):
#     for (_, feedback) in question.answers:
#       collectTagsFromText(feedback)
#   elif isinstance(question, MatchingQuestion):
#     for (a, b) in question.matches:
#       collectTagsFromText(a)
#       collectTagsFromText(b)
#   elif isinstance(question, MultipleChoiceQuestion):
#     for (s, _) in question.choices:
#       collectTagsFromText(s)

# def collectTags(assignment : Assignment):
#   collectTagsFromText(assignment.intro)
#   for question in assignment.questions:
#     collectTagsFromQuestion(question)

# for assignment in assignments:
#   collectTags(assignment)

# import pprint
# pprint.pprint(tagNames)
# pprint.pprint(styles)

# activities/quiz_45647/quiz.xml
# ALL_QUESTIONS_DOC = parse("sampleData/questions.xml")


## TODO
## - What HTML transformation do we need?
## - make title from lines in question text
## - What to do with description questions
## - Create pretext from the assignments
## - Figure out image stuff
