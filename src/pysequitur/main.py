# from pysequitur.item import Item
from pysequitur.file_sequence import Item, Parser, Renamer
from pathlib import Path
import os

directory = "/Volumes/borg/stock_project/sequences/cars/cars_03/out_copy"


# print(os.listdir(directory))

file_list = os.listdir(directory)

print(len(file_list))

ss = Parser.find_sequences(file_list, directory)

for x, sequence in enumerate(ss):
    print(f"{x} {sequence.name} {sequence.first_frame} {sequence.last_frame} {len(sequence.missing_frames)}")   



# # ss[1].rename("noob")

# # ss[11].delete()
# for s in ss:
#     s.delete()