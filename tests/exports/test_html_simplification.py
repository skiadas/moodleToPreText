import unittest

from moodle2pretext.utils.html import simplifyHTML

exampleHTML = """<h3>Make List Items Uppercase 2</h3><p>Define the function <strong><span class="" style="font-family: &quot;Courier New&quot;, Courier, mono; color: rgb(0, 61, 245);">make_uppercase_2(mylist)</span></strong>, which takes a list parameter <strong><span class="" style="font-family: &quot;Courier New&quot;, Courier, mono; color: rgb(0, 61, 245);">mylist</span></strong> (a list of strings) and modifies its items to be all uppercase.&nbsp;</p><p>For example, if mylist is <span class="" style="font-family: &quot;Courier New&quot;, Courier, mono;"><strong>['cat', 'Dog', 'frOG']</strong></span>, then after calling <strong><span class="" style="font-family: &quot;Courier New&quot;, Courier, mono;">make_uppercase_2(mylist), mylist ==&nbsp; ['CAT', 'DOG', 'FROG'].&nbsp;</span></strong></p><p>The function prints nothing and returns nothing; it simply modifies the items in <span class="" style="font-family: &quot;Courier New&quot;, Courier, mono;"><strong>mylist</strong></span>.</p><p>Hints:</p><p><ul><li>To get the uppercased version of any string X,&nbsp; use the syntax:&nbsp; <strong><span class="" style="font-family: &quot;Courier New&quot;, Courier, mono;">X.upper()</span></strong></li><li>We don't need an accumulator here. Iterate k over the indices for mylist and, inside the loop, replace <span class="" style="font-family: &quot;Courier New&quot;, Courier, mono;"><strong>mylist[k]</strong></span> with its uppercased version.</li></ul></p>"""

class TestHtmlSimplification(unittest.TestCase):
    # def test_processHTML(self):
    #   self.maxDiff = None
    #   text = simplifyHTML(exampleHTML)
    #   self.assertEqual(exampleHTML, text)

    def test_inline_code(self):
        self.assertInputProducesOutput(
          "<code>print('hi')</code>",
          "<c>print('hi')</c>"
        )

    def test_strong_with_span(self):
        self.assertInputProducesOutput(
          "<p><strong><span style='something'>some words</span></strong></p>",
          '<p>some words</p>'
        )

    def test_span_around_b_removes_the_b(self):
        self.assertInputProducesOutput(
          "<p><span><b>something</b></span></p>",
          "<p>something</p>"
        )

    def test_strong_without_span_becomes_alert(self):
        self.assertInputProducesOutput(
          "<p><strong>some words</strong></p>",
          "<p><alert>some words</alert></p>"
        )

    def test_strong_with_style_becomes_code(self):
        self.assertInputProducesOutput(
        '<p><strong style="font-size: 0.9375rem; font-family: mono">current.</strong></p>',
        "<p><c>current.</c></p>"
        )

    def test_i_and_u_become_em(self):
        self.assertInputProducesOutput(
          '<p><u>here</u><i>there</i></p>',
          "<p><em>here</em><em>there</em></p>",
        )

    def test_spans_with_mono_become_code(self):
        self.assertInputProducesOutput(
          """<span class="" style='font-family: "Courier New", Courier, mono;'>D</span>""",
          '<c>D</c>',
        )

    def test_spans_without_mono_go_away(self):
        self.assertInputProducesOutput(
          """<p><span class="" style="font-family: Arial, Helvetica, sans-serif;"><span class="" style="color: rgb(0, 46, 184);">D</span></span></p>""",
          '<p>D</p>'
        )

    def test_sub_sup_become_text(self):
        self.assertInputProducesOutput(
          '<p><sub>here</sub></p>',
          "<p>&amp;lt;sub&amp;rt;here&amp;lt;/sub&amp;rt;</p>"
        )

    def test_b_within_span_removes_itself(self):
        self.assertInputProducesOutput(
          "<span><b><code>x</code></b></span>",
          "<c>x</c>"
        )

    def test_doubly_nested_empty_lists_unfold(self):
        self.assertInputProducesOutput(
          """<ul>
  <ul>
    <li>One</li>
    <li>Two</li>
  </ul>
</ul>""",
        """<ul>
  <li>
    One
  </li>
  <li>
    Two
  </li>
</ul>""")

    def test_ensure_nested_list_is_in_p_in_item(self):
        self.assertInputProducesOutput(
            """<ol>
  <li>one</li>
  <li>two</li>
  <ul>
    <li>two-a</li>
    <li>two-b</li>
  </ul>
  <li>three</li>
</ol>""", """<ol>
  <li>
    one
  </li>
  <li>
    <p>two
    <ul>
      <li>
        two-a
      </li>
      <li>
        two-b
      </li>
    </ul>
    </p>
  </li>
  <li>
    three
  </li>
</ol>""")

    def test_ensure_consecutive_nested_list_also_handled(self):
        self.assertInputProducesOutput(
          "<ol><li>one</li><li>two</li><ul><li>two-a</li></ul><ul><li>two-b</li></ul><li>three</li></ol>",
"""<ol>
  <li>
    one
  </li>
  <li>
    <p>two
    <ul>
      <li>
        two-a
      </li>
    </ul>
    </p>
    <p>
    <ul>
      <li>
        two-b
      </li>
    </ul>
    </p>
  </li>
  <li>
    three
  </li>
</ol>""")

    def test_remove_breaks_and_horizontal_rules(self):
        self.assertInputProducesOutput(
        '<p> stuff here <br /> more <hr /> stuff</p>',
        '<p> stuff here  more  stuff</p>'
        )

    def test_divs_with_editor_indent_class_are_removed(self):
        self.assertInputProducesOutput(
          '<div class="editor-indent">Stuff here <c>a</c></div>',
          'Stuff here <c>a</c>'
        )

    def test_non_empty_divs_without_class_indent_become_paragraphs(self):
        self.assertInputProducesOutput(
          '<div>Stuff here</div>',
          '<p>Stuff here</p>'
        )


    def test_empty_divs_are_removed(self):
        self.assertInputProducesOutput(
          '<div><br/></div>',
          ''
        )

    def test_h3_h4_get_simplified(self):
        self.assertInputProducesOutput(
          '<h4><strong>Divides</strong></h4>',
          '<h3>Divides</h3>'
        )

    def test_h5_become_paragraphs(self):
        self.assertInputProducesOutput(
          '<h5><strong>Something</strong></h5>',
          "<p><alert>Something</alert></p>")

    def test_a_becomes_url(self):
        self.assertInputProducesOutput(
          '<a href="https://thispointer.com/python-different-ways-to-iterate-over-a-list-in-reverse-order/" target="_blank"><span class="" style="color: rgb(0, 46, 184);"><u>here</u></span></a>',
          '<url href="https://thispointer.com/python-different-ways-to-iterate-over-a-list-in-reverse-order/">here</url>'
        )

    def test_tt_becomes_code(self):
        self.assertInputProducesOutput(
          """<tt><span class="" style='font-family: "Courier New", Courier, mono;'><b><span class="" style="color: rgb(0, 61, 245);">L</span></b></span></tt>""",
          '<c>L</c>'
        )

    def test_style_attributes_are_removed(self):
        self.assertInputProducesOutput(
          "<p style='text-indent:left;'>hi there</p>",
          '<p>hi there</p>')

    def test_span_elements_with_no_content_are_removed(self):
        self.assertInputProducesOutput(
          "<p>hi there<span style='mono'></span></p>",
          '<p>hi there</p>')

    def test_list_elements_with_no_content_are_removed(self):
        self.assertInputProducesOutput(
          "<ul>   </ul>",
          ""
        )
    def assertInputProducesOutput(self, input, output):
        self.assertEqual(output, simplifyHTML(input))
