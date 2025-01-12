from pysequitur import crawl
from pathlib import Path



print("hello")

p = Path("/Volumes/porb/test_seqs")


n = crawl.Node(p)




# crawl.visualize_tree(n)

sqs =crawl.collect_sequences(n)

for s in sqs:
    print(s.frame_count)