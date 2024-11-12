# Copyright (c) 2024 Alex Harding (alexharding.ooo)
# This file is part of PySequitur which is released under MIT license.
# See file LICENSE for full license details.




from pysequitur.file_sequence import FileSequence, Item, Parser, Components


# item = Parser.item_from_filename("test.001.png", "test_dir")



# print(item.prefix)
# print(item.delimiter)
# print(item.frame_string)
# print(item.suffix)
# print(item.extension)
# print(item.directory)
# print(item.filename)
# print(item.path)
# print(item.absolute_path)


# item.rename(Components(prefix="new_name", padding=4))

# print(item.prefix)
# print(item.delimiter)
# print(item.frame_string)
# print(item.suffix)
# print(item.extension)
# print(item.directory)
# print(item.filename)
# print(item.path)
# print(item.absolute_path)


files = ["test.001.png", "test.002.png", "test.003.png", "test.004.png", "test.005.png"]

sequence = Parser.filesequences_from_file_list(files)[0]

for item in sequence.items:
    print(item.filename)

sequence.rename_to("new_name")

for item in sequence.items:
    print(item.filename)