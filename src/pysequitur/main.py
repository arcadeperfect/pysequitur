# from pysequitur.item import Item
from pysequitur.file_sequence import Item, Parser, Renamer
from pathlib import Path
import os

files = ['frame.1.png', 
         'frame.2.png', 
         'frame.3.png', 
         'frame.4.png', 
         'frame.5.png']



path = Path('~/file.1001.exr').expanduser()
path.touch()



item = Parser.parse_filename(path.name, path.parent)





item.rename('test')


print(item.filename)
print(item.path)
print(item.exists)

item.rename(Renamer(name='test',
                     separator='_',
                     padding=2,
                     post_numeral='.post',
                     extension='png'))

print(item.filename)
print(item.path)

print(item.path.exists())


newdir = item.directory / 'test'
print(newdir)

item.move(newdir)

print(item.exists)