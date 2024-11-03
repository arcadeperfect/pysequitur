# from pysequitur.item import Item
from pysequitur.file_sequence import Item, Parser, Renamer
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

files = ["file.1.jpg",
         "file_2.jpg",
         "file-3.jpg",
         "file-4.jpg",
         "file-5.jpg",
         "file-06.jpg",
         "file-07.jpg",
         "file-08.jpg",
         "file-09.jpg",
         "file-10.jpg",
         "file-11.jpg",
         "file-12.jpg",
         "file-13.jpg",
         "file-14.jpg",
         "file-15.jpg",
         "file-16.jpg",
]

seq = Parser.find_sequences(files)[0]



seq.offset_frames(10)
print(seq)