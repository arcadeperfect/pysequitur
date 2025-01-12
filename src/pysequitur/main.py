from pysequitur import crawl
from pathlib import Path



print("hello")

p = Path("/Volumes/porb/test_seqs")


n = crawl.Node(p)


# print(n.nodes)

crawl.visualize_tree(n)