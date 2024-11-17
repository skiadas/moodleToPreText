from xml.dom import Node
from bs4 import BeautifulSoup

from ptx_formatter import formatPretext


def simplifyHTML(html: str) -> str:
  simplifier = HtmlSimplifier(html)
  simplifier.simplify()
  # simplifier.printTopLevels()
  return str(simplifier)


def pretextify(html: str, contextId: int | None = None) -> str:
  simplifier = HtmlSimplifier(html)
  simplifier.simplify()
  simplifier.pretextify()
  if contextId is not None:
    simplifier.addIdToImages(contextId)
  return str(simplifier)


class HtmlSimplifier:

  def __init__(self, html: str) -> None:
    self.soup = BeautifulSoup(html, 'html.parser')

  def __str__(self) -> str:
    return str(self.soup)

  def printTopLevels(self) -> None:
    print([c.name if c.name is not None else "str" for c in self.soup.contents])

  def pretextify(self) -> None:
    self.soup.smooth()
    # Step 1: Find top level whitespace strings and remove them
    for tag in [t for t in self.soup.contents]:
      if tag.name is None and tag.isspace():
        tag.extract()
    # Step 2: sequence of top-level tags not p/pre become a paragraph
    for tag in self.soup.contents:
      if tag.name is None:
        newTag = self.soup.new_tag("p")
        newTag.string = tag  # first one is a string
        curr = tag.next_sibling
        # We absorb any subsequent tags that are meant to be
        # part of the same paragraph
        while curr is not None and curr.name not in ["p", "pre"]:
          next = curr.next_sibling
          newTag.append(curr)
          curr = next
        tag.replace_with(newTag)
    # Step 3: lists following a paragraph are appended to the paragraph
    # and lists not following a paragraph form their own paragraph
    for tag in [t for t in self.soup.contents]:
      if tag.name in ["ol", "ul"]:
        if tag.previous_sibling is not None and tag.previous_sibling.name == "p":
          tag.previous_sibling.append(tag)
        else:
          tag.wrap(self.soup.new_tag("p"))
    # Step 4: c inside pre is unwrapped
    for preTag in self.soup.find_all("pre"):
      for cTag in preTag.find_all("c"):
        cTag.unwrap()
    # Step 5: Remove empty paragraph tags
    for pTag in self.soup.find_all("p"):
      if not pTag.contents:
        pTag.extract()

  def simplify(self) -> None:
    for tag in self.soup.find_all("code"):
      tag.name = "c"
    for tag in self.soup.find_all(["strong", "b"]):
      if tag.span is not None and len(tag.contents) == 1:
        tag.replace_with(tag.span)
      elif "style" in tag.attrs and "mono" in tag["style"]:
        tag.name = "c"
        del tag["style"]
      elif tag.parent.name == "span" and len(tag.parent.contents) == 1:
        tag.unwrap()
      else:
        tag.name = "alert"
    for tag in self.soup.find_all(["i", "u"]):
      tag.name = "em"
    for tag in self.soup.find_all(["br", "hr"]):
      tag.extract()
    for tag in self.soup.find_all(["ol", "ul"]):
      stripBlanks(tag)
      # If nothing left, just remove tag
      if len(tag.contents) == 0:
        tag.extract()
      elif len(tag.contents) == 1 and tag.contents[0].name in ["ol", "ul"]:
        innerTag = tag.contents[0].extract()
        tag.replace_with(innerTag)
      else:
        self.handle_inner_list_outside_item(tag)
    for tag in self.soup.find_all("div", {"class": "editor-indent"}):
      tag.unwrap()
    for tag in self.soup.find_all("div"):
      if len(tag.contents) == 0:
        tag.extract()
      else:
        tag.name = "p"
    for tag in self.soup.find_all(["h3", "h4"]):
      if len(tag.contents) == 0:
        tag.extract()
      else:
        self.putStringContentInNewTag(tag, "h3")
    for tag in self.soup.find_all("h5"):
      tag.name = "p"
    for tag in self.soup.find_all("a"):
      newTag = self.putStringContentInNewTag(tag, "url")
      newTag.attrs["href"] = tag.attrs["href"]
    for tag in self.soup.find_all("img"):
      newTag = self.putStringContentInNewTag(tag, "image")
      newTag.attrs["source"] = tag.attrs["src"]
      newTag.attrs["width"] = "90%"
      if tag.attrs["alt"] == "":
        newTag.attrs["decorative"] = "yes"
      else:
        shortDescr = self.soup.new_tag("shortdescription")
        shortDescr.contents = tag.attrs["alt"]
        newTag.append(shortDescr)
    for tag in self.soup.find_all("tt"):
      self.putStringContentInNewTag(tag, "c")
    for tag in self.soup.find_all(["sup", "sub"]):
      tag.replace_with(
          "&lt;" + tag.name + "&rt;" + tag.string + "&lt;/" + tag.name + "&rt;")
    for tag in self.soup.find_all("span"):
      if tag.get_text() == '':
        tag.extract()
      elif "style" in tag.attrs and "mono" in tag.attrs["style"]:
        self.putStringContentInNewTag(tag, "c")
      elif "style" in tag.attrs and "x-large" in tag.attrs["style"]:
        self.putStringContentInNewTag(tag, "h3")
      else:
        tag.unwrap()
    for tag in self.soup.find_all(True):
      tag.attrs.pop("style", None)
    if len(self.soup.contents) == 1 and self.soup.contents[0].name is None:
      # Single string content. Wrap in paragraph
      self.putStringContentInNewTag(self.soup.contents[0], "p")

  def putStringContentInNewTag(self, tag: Node, newName: str) -> Node:
    newTag = self.soup.new_tag(newName)
    newTag.string = tag.get_text()
    tag.replace_with(newTag)
    return newTag

  # tag is a ul or ol node. We look for immediate
  # children who are ul or ol. If they are outside
  # of a li, we add them to the preceding li
  def handle_inner_list_outside_item(self, tag: Node):
    for child in tag.contents:
      if child.name in ["ol", "ul"]:
        # Search for previous non-text sibling
        pr = child.previous_sibling
        while pr.name is None:
          pr = pr.previous_sibling

        if pr is None:
          # No list item before the list element
          # nothing we can do
          raise RuntimeError(
              "Shouldn't happen: Sublist as the first thing in a list without a containing li"
          )
        else:
          # Can now add to this previous item
          pr.append(child)
          child.wrap(self.soup.new_tag("p"))
          parent_p = child.parent
          prev_text = parent_p.previous_sibling
          if prev_text is not None and prev_text.name is None:
            child.insert_before(prev_text)
          pr.insert_after("")

  def addIdToImages(self, contextId: int):
    for tag in self.soup.find_all("image"):
      tag.attrs["itemid"] = contextId

def stripBlanks(tag: Node):
  for idx in [0, -1]:
    # must account for case where this is a list containing at most empty
    # spaces
    # in this case we want to remove the tag
    if len(tag.contents) == 0:
      return
    if tag.contents[idx].name is None:
      newString = tag.contents[idx].strip(" \t\n")
      if newString == "":
        del tag.contents[idx]
      else:
        tag.contents[idx] = newString
