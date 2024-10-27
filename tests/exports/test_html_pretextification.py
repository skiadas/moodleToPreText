import unittest

from moodle2pretext.utils.html import HtmlSimplifier, simplifyHTML
from ptx_formatter import formatPretext


class TestHtmlPretextification(unittest.TestCase):

  def test_top_level_whitespace_strings_are_removed(self):
    self.assertInputProducesOutput(
        "<p>Something</p>       <p>More</p>",
        "<p>Something</p><p>More</p>",
        False)

  def test_empty_paragraph_tags_are_removed(self):
    self.assertInputProducesOutput(
        "<p>Something</p><p></p><p /><p>More</p>",
        "<p>Something</p><p>More</p>",
        False)

  def test_paragraph_tags_with_no_text_but_images_are_not_removed(self):
    self.assertInputProducesOutput(
        "<p>Something</p><p><image source=\"something.jpg\"/></p><p>More</p>",
        "<p>Something</p><p><image source=\"something.jpg\"/></p><p>More</p>",
        False)

  def test_top_level_nonwhitespace_strings_become_paragraphs(self):
    self.assertInputProducesOutput(
        "<p>Something</p>  stuff here   <p>More</p>",
        "<p>Something</p><p>  stuff here   </p><p>More</p>",
        False)

  def test_top_level_sequence_inline_things_become_paragraphs(self):
    self.assertInputProducesOutput(
        """<p>Something</p>  stuff here <c>code!</c> more stuff <p>More</p>""",
        """
<p>Something</p><p>  stuff here <c>code!</c> more stuff </p><p>More</p>""".
        strip(),
        False)

  def test_top_level_lists_merge_into_previous_paragraph(self):
    self.assertInputProducesOutput(
        """
<p>Something</p>
<ul>
  <li>stuff here</li>
</ul>
<p>More</p>""".strip(),
        """
<p>
  Something
  <ul>
    <li>stuff here</li>
  </ul>
</p>
<p>More</p>""".strip(),
        True,
        True)

  def test_top_level_lists_without_preceding_paragraph_make_their_own(self):
    self.assertInputProducesOutput(
        "<ul><li>at front</li></ul><pre>\nSomething\n</pre><ul><li>stuff here</li></ul><p>More</p>",
        """<p>
  <ul>
    <li>at front</li>
  </ul>
</p>
<pre>
Something
</pre>
<p>
  <ul>
    <li>stuff here</li>
  </ul>
</p>
<p>More</p>""",
        True,
        True)

  def test_c_inside_pre_gets_unwrapped(self):
    self.assertInputProducesOutput(
        "<pre>   <c>Something # stuff\n</c>   </pre>",
        "<pre>   Something # stuff\n</pre>")
    self.assertInputProducesOutput(
        "<premise><pre>   <c>Something # stuff\n</c>   </pre></premise>",
        "<premise>\n  <pre>   Something # stuff\n  </pre>\n</premise>")

  def assertInputProducesOutput(
      self,
      input,
      output,
      shouldCallFormatPretext=True,
      shouldWrapInSection=False):
    simplifier = HtmlSimplifier(input)
    simplifier.pretextify()
    actual = str(simplifier)
    if shouldWrapInSection:
      actual = "<section>\n  " + (
          "\n  ".join(actual.split("\n"))) + "\n</section>"
      output = "<section>\n  " + (
          "\n  ".join(output.split("\n"))) + "\n</section>"
    if shouldCallFormatPretext:
      actual = formatPretext(actual)
      print(actual)
    self.assertEqual(output, actual)
