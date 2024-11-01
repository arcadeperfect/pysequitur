# from pysequitur.item import Item
from pysequitur.file_sequence import Item, Parser, Renamer
from pathlib import Path
import os

d = Path("~/test").expanduser()



for i in range(10):
    Path(d / f"test{i}.txt").touch()


s = Parser.scan_directory(d)

s[0].copy("copy")