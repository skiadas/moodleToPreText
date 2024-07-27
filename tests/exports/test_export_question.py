import unittest
from xml.dom import Node

from moodle2pretext.question import Question
# from moodle2pretext.export import Exporter


class TestExportQuestion(unittest.TestCase):

  def test_description(self):
    pass
    # question = Question("the-question-name", "<p>The Question Text Goes Here</p>")
    # exporter = Exporter()
    # node : Node = exporter.exportQuestion(question)
    # expectedXML = """<exercise id="the-question-name"></exercise>"""
    # self.assertEqual(expectedXML, node.toxml())
