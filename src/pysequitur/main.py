# from pysequitur.item import Item
from pysequitur.file_sequence import Item, Parser, Components, FileSequence
from pathlib import Path
import os


# files = ["file.01.jpg",
#          "file.001.jpg",
#          "file.0001.jpg",
#          "file.0003.jpg",
#          "file.04.jpg",
#          "file.004.jpg",
#          "file.0004.jpg",
#          "file.0005.jpg",
#          "file.0006.jpg",
#          "file.007.jpg",
#          "file.0007.jpg",
#          "file2.001.jpg",
#          "file2.002.jpg",
#          "file2.03.jpg",
#         #  "file2.003.jpg",
#          "file2.004.jpg",
#          "file2.0005.jpg",
#          ]

files = [
    "file-01.jpg",
    "file-02.jpg",
    "file-03.jpg",
    "file-04.jpg",
    "file-06.jpg",
    "img-01.exr",
    "img-02.exr",
    "img-03.exr",
    "img-04.exr",
    "render-1001.png",
    "render-1002.png",
    "render-1003.png",
    "render-1004.png",
    "render-1005.png",
    "render-1006.png",
    "render-1007.png",
    "render.1001.png",
    "render.1002.png",
    "render.1003.png",
    "render.1004.png",
    "render.1005.png",
    "render.1006.png",
    "render.1007.png",
]

# f = FileSeq

seqs = Parser.match_components(Components(prefix="render", delimiter="."), files)


for seq in seqs:
    print(seq)
