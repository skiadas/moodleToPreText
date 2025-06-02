from re import compile
import shutil
from typing import Self
from collections.abc import Generator
from tarfile import TarFile
from xml.dom.minidom import parse
from xml.dom import Node
from dataclasses import dataclass
from os import makedirs
from os import path
from io import BytesIO

from moodle2pretext.utils import getFirstInt, getFirstText


@dataclass
class Asset:
  assetId: int
  itemId: int
  contentHash: str
  filePath: str
  fileName: str
  fileArea: str
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
        getFirstText(e, "filearea"),
        getFirstText(e, "filesize"),
        getFirstText(e, "mimetype"),
        getFirstInt(e, "timecreated"),
        getFirstInt(e, "timemodified"))
    return asset

  def getPathToResource(self: Self) -> str:
    return path.join("files", self.contentHash[:2], self.contentHash)


class AssetManager:

  def __init__(self, tar: TarFile, directory: str):
    self.tar = tar
    self.imageDir = path.join(directory, "assets", "images")
    self.sourceDir = path.join(directory, "source")
    makedirs(self.imageDir)
    makedirs(self.sourceDir)
    pathToHere = path.dirname(__file__)
    shutil.copytree(
        path.join(pathToHere, "utils", "ptxProjectFiles"),
        directory,
        dirs_exist_ok=True)

    entries = self.parseXML("files.xml").getElementsByTagName("file")
    self.assets: list[Asset] = [Asset.fromEntry(e) for e in entries]

  def parseXML(self: Self, filename: str) -> Node:
    return parse(self.tar.extractfile(filename))

  def parseList(self: Self, regex: str) -> Generator[Node, None, None]:
    prog = compile(regex)
    for tarInfo in self.tar.getmembers():
      if prog.match(tarInfo.name):
        yield parse(self.tar.extractfile(tarInfo))

  def getAssetAsFileHandler(self, asset: Asset):
    return self.tar.extractfile(asset.getPathToResource())

  def getAssetAsString(self, asset: Asset) -> str:
    with self.getAssetAsFileHandler(asset) as f:
      return f.read().decode("utf-8")

  def locateResource(self, itemId: int | str, filepath: str) -> str:
    for asset in self.assets:
      if asset.itemId == int(itemId) and asset.fileName == filepath:
        baseFilename = f"{itemId}-{filepath}"
        f = self.getAssetAsFileHandler(asset)
        with open(path.join(self.imageDir, baseFilename), "wb") as out:
          out.write(f.read())
        return path.join("images", baseFilename)
    raise Exception(f"Cannot find: {itemId} {filepath}")

  def createSourceFile(self, filename, contents: str) -> None:
    with open(path.join(self.sourceDir, filename), "w") as f:
      f.write(contents)

  def locateDatafiles(self, itemId: int | str) -> dict[str, str]:
    """For now, return list of the datafiles linked to a specific item id."""
    return {
        asset.fileName: self.getAssetAsString(asset)
        for asset in self.assets
        if asset.itemId == int(itemId) and asset.fileArea == "datafile" and
        asset.fileName != "."
    }
