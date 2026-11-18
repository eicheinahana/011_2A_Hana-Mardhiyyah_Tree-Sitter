import tree_sitter_python as tspython
from tree_sitter import Language, Parser

parser = Parser(Language(tspython.language()))

potongan = {
    "x = 1": b"x = 1\n",
    "fungsi": b"def sapa(nama):\n    return nama\n",
    "if_else": b"if x > 0:\n    y = 1\nelse:\n    y = 2\n",
    "kelas": b"class Hewan:\n    def bicara(self):\n        return 1\n",
    "rusak (titik dua dihapus)": b"def sapa(nama)\n    return nama\n",
}

for judul, kode in potongan.items():
    tree = parser.parse(kode)
    print("==", judul, "==")
    print(tree.root_node)
    print("has_error:", tree.root_node.has_error)
    print()

fungsi = parser.parse(potongan["fungsi"]).root_node.children[0]

print("== anak langsung function_definition: bernama atau anonim ==")
for c in fungsi.children:
    print(c.type, "bernama" if c.is_named else "anonim")
print()

print("== children vs named_children (function_definition) ==")
print("children       :", [c.type for c in fungsi.children])
print("named_children :", [c.type for c in fungsi.named_children])

print()
print("== anak dari parameters ==")
for c in fungsi.child_by_field_name("parameters").children:
    print(c.type, "bernama" if c.is_named else "anonim")