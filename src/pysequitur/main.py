from pysequitur.file_sequence import FileSequence, Item, Parser

files = ['frame.001.png', 
         'frame.2.png', 
         'frame.3.png', 
         'frame.4.png', 
         'frame.5.png']


i = Parser.parse_filename(files[0])


print (i)