import sys
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY = Language(tspython.language())
parser = Parser(PY)

kode = open(sys.argv[1], "rb").read()
pola = open(sys.argv[2]).read()
tree = parser.parse(kode)

jumlah = 0
for _, cap in QueryCursor(Query(PY, pola)).matches(tree.root_node):
    bagian = []
    for nama in cap:
        for n in cap[nama]:
            teks = n.text.decode(errors="replace")
            if len(teks) > 40:
                teks = teks[:40] + "..."
            bagian.append(f"@{nama}[baris {n.start_point[0] + 1}]={teks!r}")
    if "params" in cap:
        bagian.append(f"jumlah_parameter={cap['params'][0].named_child_count}")
    print("  ".join(bagian))
    jumlah += 1
print(f"-- total: {jumlah} hasil")
