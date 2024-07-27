import unittest

from moodle2pretext.utils.html import HtmlSimplifier, simplifyHTML


class TestHtmlPretextification(unittest.TestCase):

  def test_top_level_whitespace_strings_are_removed(self):
    self.assertInputProducesOutput(
        "<p>Something</p>       <p>More</p>", "<p>Something</p>\n<p>More</p>")

  def test_top_level_nonwhitespace_strings_become_paragraphs(self):
    self.assertInputProducesOutput(
        "<p>Something</p>  stuff here   <p>More</p>",
        "<p>Something</p>\n<p>  stuff here   </p>\n<p>More</p>")

  def test_top_level_sequence_inline_things_become_paragraphs(self):
    self.assertInputProducesOutput(
        """<p>Something</p>  stuff here <c>code!</c> more stuff <p>More</p>""",
        """
<p>Something</p>
<p>  stuff here <c>code!</c> more stuff </p>
<p>More</p>""".strip())

  def test_top_level_lists_merge_into_previous_paragraph(self):
    self.assertInputProducesOutput(
        """
<p>Something</p>
<ul>
  <li>stuff here</li>
</ul>
<p>More</p>""".strip(),
        """
<p>Something
<ul>
  <li>
    stuff here
  </li>
</ul>
</p>
<p>More</p>""".strip())

  def test_top_level_lists_without_preceding_paragraph_make_their_own(self):
    self.assertInputProducesOutput(
        "<ul><li>at front</li></ul><pre>Something</pre><ul><li>stuff here</li></ul><p>More</p>",
        """<p>
<ul>
  <li>
    at front
  </li>
</ul>
</p>
<pre>Something</pre>
<p>
<ul>
  <li>
    stuff here
  </li>
</ul>
</p>
<p>More</p>""")

  def test_c_inside_pre_gets_unwrapped(self):
    self.assertInputProducesOutput(
        "<pre><c>Something</c></pre>", "<pre>Something</pre>")

  def assertInputProducesOutput(self, input, output):
    simplifier = HtmlSimplifier(input)
    simplifier.pretextify()
    self.assertEqual(output, str(simplifier))
