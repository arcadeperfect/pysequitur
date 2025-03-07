from pysequitur.file_sequence import FileSequence, Item, ItemParser, Components
from pysequitur.crawl import Node
from pathlib import Path







f = "file_00100.exr"

item = Item.from_file_name(f)

print(item)
print(item.move_to(Path("test"), virtual=True))