# cek.py - pemeriksa file Python berbasis tree-sitter

Melaporkan tiga hal pada semua file `*.py` di sebuah folder:

1. komentar `TODO` / `FIXME`,
2. fungsi dengan panjang lebih dari 30 baris,
3. file yang mengandung syntax error (beserta baris pertama yang bermasalah).

## Cara memasang dependensi

```bash
python3 -m venv ~/venv-plp
source ~/venv-plp/bin/activate
pip install tree-sitter tree-sitter-python
```

## Cara menjalankan

```bash
python cek.py <folder>
# contoh: python cek.py uji
```

Folder `venv/`, `.venv/`, `.git/`, `node_modules/`, dan `__pycache__/` dilewati.

## Contoh output

[PANJANG] uji/panjang.py:1: fungsi fungsi_panjang = 37 baris
[ERROR] uji/rusak.py:1: syntax error (ERROR)
[TODO]  uji/todo.py:1: # TODO: tambahkan validasi input
[TODO]  uji/todo.py:3: # FIXME: belum menangani x negatif
-- selesai: 3 file diperiksa

## Catatan

- Semua fungsi dihitung, termasuk method di dalam kelas dan fungsi bersarang.
- Panjang fungsi dihitung dari baris `def` sampai baris terakhir badannya.
