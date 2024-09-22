import typer
from moodle2pretext.course import Course


def main(zip_path: str, out_file: str):
  """
  Reads a Moodle backup file with path zip_path
  and produces a PreText output file with path out_file
  """
  course = Course.fromZip(zip_path)


def run():
  typer.run(main)


if __name__ == "__main__":
  run()

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
