from xml.dom import Node

from moodle2pretext.utils.html import pretextify


def getText(node: Node) -> str:
  if 'data' in dir(node):
    return node.data
  return ''.join([getText(child) for child in node.childNodes])


def getFirst(node: Node, tagName: str | list[str]) -> Node:
  return _getAtIndex(node, tagName, 0)


def isEmpty(node: Node) -> bool:
  return getText(node).strip() == ""


def getLast(node: Node, tagName: str | list[str]) -> Node:
  return _getAtIndex(node, tagName, -1)


def getAll(node: Node, tagName: str) -> list[Node]:
  return node.getElementsByTagName(tagName)


def _getAtIndex(node: Node, tagName: str | list[str], index: int) -> Node:
  tagNameList = tagName.split("/") if isinstance(tagName, str) else tagName
  for tag in tagNameList:
    nodeList = node.getElementsByTagName(tag)
    if len(nodeList) == 0:
      raise RuntimeError("No child tag: " + tag)
    node = nodeList[index]
  return node


def getFirstText(node: Node, tagName: str | list[str]) -> str:
  return getText(getFirst(node, tagName))


def getFirstInt(node: Node, tagName: str | list[str]) -> str:
  return int(getFirstText(node, tagName))


def getFirstHtml(
    node: Node, tagName: str | list[str], itemId: int | None = None) -> str:
  return pretextify(getFirstText(node, tagName), itemId)


def yesOrNo(cond: bool) -> str:
  return "yes" if cond else "no"
