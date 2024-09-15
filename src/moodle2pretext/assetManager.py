from re import compile
from typing import Self
from collections.abc import Generator
from tarfile import TarFile
from xml.dom.minidom import parse
from xml.dom import Node
from dataclasses import dataclass
from os import makedirs
from os import path

from moodle2pretext.utils import getFirstInt, getFirstText


class AssetManager:

  def __init__(self, tar: TarFile, directory: str):
    self.tar = tar
    self.imageDir = path.join(directory, "assets", "images")
    makedirs(self.imageDir)
    entries = self.parseXML("files.xml").getElementsByTagName("file")
    self.assets: list[Asset] = [Asset.fromEntry(e) for e in entries]
    lst = sorted([f"{a.itemId}{a.fileName}" for a in self.assets])
    # s = set()
    # for l in lst:
    #   if l in s:
    #     print(l)
    #   s.add(l)
    # TODO

  def parseXML(self: Self, filename: str) -> Node:
    return parse(self.tar.extractfile(filename))

  def parseList(self: Self, regex: str) -> Generator[Node, None, None]:
    prog = compile(regex)
    for tarInfo in self.tar.getmembers():
      if prog.match(tarInfo.name):
        yield parse(self.tar.extractfile(tarInfo))

  def locateResource(self, questionId: str, filepath: str) -> str:
    for asset in self.assets:
      if asset.itemId == int(questionId) and asset.fileName == filepath:
        baseFilename = f"{questionId}-{filepath}"
        f = self.tar.extractfile(asset.getPathToResource())
        with open(path.join(self.imageDir, baseFilename), "wb") as out:
          out.write(f.read())
        return path.join("images", baseFilename)
    raise Exception("Cannot find: " + questionId + " " + filepath)


@dataclass
class Asset:
  assetId: int
  itemId: int
  contentHash: str
  filePath: str
  fileName: str
  fileSize: int
  mimeType: str
  timeCreated: int
  timeModified: int

  @staticmethod
  def fromEntry(e: Node) -> Self:
    asset = Asset(
        int(e.attributes["id"].value),
        getFirstInt(e, "itemid"),
        getFirstText(e, "contenthash"),
        getFirstText(e, "filepath"),
        getFirstText(e, "filename"),
        getFirstText(e, "filesize"),
        getFirstText(e, "mimetype"),
        getFirstInt(e, "timecreated"),
        getFirstInt(e, "timemodified"))
    return asset

  def getPathToResource(self: Self) -> str:
    return path.join("files", self.contentHash[:2], self.contentHash)
