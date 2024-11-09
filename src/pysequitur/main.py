# Copyright (c) 2024 Alex Harding (alexharding.ooo)
# This file is part of PySequitur which is released under MIT license.
# See file LICENSE for full license details.




from pysequitur.file_sequence import FileSequence


files = ["image.001_final.exr", "image.002_final.exr", "image.003_final.exr"]

seqeuences = FileSequence.from_file_list(files)

item = seqeuences[0].items[0]

print(item.check_rename("bottom"))