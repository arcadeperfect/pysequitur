# from pysequitur.item import Item
from pysequitur.file_sequence import Item, Parser, Renamer
from pathlib import Path
import os


files = ["file.01.jpg",
         "file.001.jpg",
         "file.0001.jpg",
         "file.0003.jpg",
         "file.04.jpg",
         "file.004.jpg",
         "file.0004.jpg",
         "file.0005.jpg",
         "file.0006.jpg",
         "file.007.jpg",
         "file.0007.jpg",
         "file2.001.jpg",
         "file2.002.jpg",
         "file2.03.jpg",
        #  "file2.003.jpg",
         "file2.004.jpg",
         "file2.0005.jpg",
         ]

seqs = Parser.find_sequences(files)

for s in seqs:
    print(s)
iter