from xml.dom import Node

from moodle2pretext.utils.html import simplifyHTML

def getText(node: Node) -> str:
  if 'data' in dir(node):
    return node.data
  return ''.join([getText(child) for child in node.childNodes])

def getFirst(node: Node, tagName: str) -> Node:
  list = node.getElementsByTagName(tagName)
  if len(list) == 0:
    raise RuntimeError("No child tag: " + tagName)
  return list[0]

def getFirstText(node: Node, tagName: str) -> str:
  return getText(getFirst(node, tagName))

def getFirstHtml(node: Node, tagName: str) -> str:
  return simplifyHTML(getFirstText(node, tagName))
