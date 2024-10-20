import unittest

from moodle2pretext.question.question import processQuestionText


class TestQuestionCreation(unittest.TestCase):

  def test_can_extract_title(self):
    content, title = processQuestionText("<h3>title here</h3><p>stuff</p>")
    self.assertEqual(title, "title here");
    self.assertEqual(content, "<p>stuff</p>")

  def test_can_extract_title_if_empty_tags_first(self):
    content, title = processQuestionText("<h4></h4>\n<h3>title here</h3><p>stuff</p>")
    self.assertEqual(title, "title here")
    self.assertEqual(content, "<p>stuff</p>")
