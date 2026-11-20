import sys
from pathlib import Path
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY = Language(tspython.language())
parser = Parser(PY)

BATAS_BARIS = 30
ABAIKAN = {"venv", ".venv", ".git", "node_modules", "__pycache__"}

Q_TODO = Query(PY, '((comment) @c (#match? @c "TODO|FIXME"))')
Q_FUNGSI = Query(PY, "(function_definition name: (identifier) @nama) @fungsi")


def cari_error(node):
    """Node pertama (urutan dokumen) yang ERROR atau MISSING, atau None."""
    if node.is_error or node.is_missing:
        return node
    if node.has_error:
        for anak in node.children:
            hasil = cari_error(anak)
            if hasil is not None:
                return hasil
    return None


def cek_file(path):
    try:
        kode = path.read_bytes()
    except OSError as e:
        print(f"[BACA]  {path}: tidak bisa dibaca ({e})")
        return
    root = parser.parse(kode).root_node

    # Fitur 1: komentar TODO / FIXME
    for node in QueryCursor(Q_TODO).captures(root).get("c", []):
        teks = node.text.decode(errors="replace").strip()
        print(f"[TODO]  {path}:{node.start_point[0] + 1}: {teks}")

    # Fitur 2: fungsi lebih dari 30 baris (semua fungsi dihitung, termasuk
    # method di dalam kelas dan fungsi bersarang)
    for _, cap in QueryCursor(Q_FUNGSI).matches(root):
        fungsi = cap["fungsi"][0]
        nama = cap["nama"][0].text.decode(errors="replace")
        baris = fungsi.end_point[0] - fungsi.start_point[0] + 1
        if baris > BATAS_BARIS:
            print(f"[PANJANG] {path}:{fungsi.start_point[0] + 1}: "
                  f"fungsi {nama} = {baris} baris")

    # Fitur 3: file dengan syntax error
    if root.has_error:
        n = cari_error(root) or root
        jenis = f"MISSING {n.type}" if n.is_missing else n.type
        print(f"[ERROR] {path}:{n.start_point[0] + 1}: syntax error ({jenis})")


def main():
    if len(sys.argv) != 2:
        print("Pemakaian: python cek.py <folder>")
        sys.exit(1)
    folder = Path(sys.argv[1])
    jumlah = 0
    for path in sorted(folder.rglob("*.py")):
        if ABAIKAN & set(path.parts):
            continue
        jumlah += 1
        cek_file(path)
    print(f"-- selesai: {jumlah} file diperiksa")


main()
