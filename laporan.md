## Tugas 1 - Membaca pohon

Saya mem-parse lima potongan kode Python dengan `tree-sitter-python` lewat
`t1.py`: `x = 1`, fungsi, if/else, kelas, dan fungsi yang sengaja dirusak
(titik dua dihapus). Untuk tiga potongan pertama saya membuat pohon perkiraan
terlebih dahulu (`tugas1-3/perkiraan_t1.md`), lalu membandingkannya dengan hasil
sebenarnya.

### Perbandingan perkiraan dan hasil

| Potongan | Hasil perbandingan |
| --- | --- |
| `x = 1` | Cocok dengan output di materi |
| Fungsi | Cocok: `function_definition` dengan `name`, `parameters`, `body: (block (return_statement ...))` |
| If/else | Cocok: `if_statement` dengan `condition`, `consequence`, dan `alternative: (else_clause ...)` |
| Kelas | Cocok: `class_definition` dengan `body: (block (function_definition ...))` |
| Kode rusak | **Meleset.** Perkiraan: pohon fungsi utuh dengan `(MISSING ":")`. Hasil: `(module (ERROR (identifier) (parameters (identifier)) (identifier)))` |

### Node bernama dan anonim

Node bernama tampil di S-expression, contohnya `module`, `function_definition`,
`identifier`, `parameters`, dan `block`. Node anonim berasal dari string literal
di grammar dan tersembunyi dari tampilan itu. Dari anak langsung
`function_definition` ditemukan dua node anonim: `def` dan `:`. Tanda kurung
`(` dan `)` berada satu tingkat lebih dalam, di dalam node `parameters`.

`children` memuat semua child (`def`, `identifier`, `parameters`, `:`, `block`),
sedangkan `named_children` hanya yang bernama (`identifier`, `parameters`,
`block`). Selisihnya adalah node anonim.

### Kode rusak: ERROR

Setelah `:` dihapus dari `def sapa(nama)`, parser tetap menghasilkan pohon
(error recovery) dan `has_error` bernilai `True`. Parser tidak menyisipkan
token yang hilang. Ia membungkus potongan yang tidak cocok dengan grammar ke
dalam satu node `ERROR`.

### Output

```
== x = 1 ==
(module (expression_statement (assignment left: (identifier) right: (integer))))
has_error: False

== fungsi ==
(module (function_definition name: (identifier) parameters: (parameters (identifier)) body: (block (return_statement (identifier)))))
has_error: False

== if_else ==
(module (if_statement condition: (comparison_operator (identifier) (integer)) consequence: (block (expression_statement (assignment left: (identifier) right: (integer)))) alternative: (else_clause body: (block (expression_statement (assignment left: (identifier) right: (integer)))))))
has_error: False

== kelas ==
(module (class_definition name: (identifier) body: (block (function_definition name: (identifier) parameters: (parameters (identifier)) body: (block (return_statement (integer)))))))
has_error: False

== rusak (titik dua dihapus) ==
(module (ERROR (identifier) (parameters (identifier)) (identifier)))
has_error: True

== anak langsung function_definition: bernama atau anonim ==
def anonim
identifier bernama
parameters bernama
: anonim
block bernama

== children vs named_children (function_definition) ==
children       : ['def', 'identifier', 'parameters', ':', 'block']
named_children : ['identifier', 'parameters', 'block']

== anak dari parameters ==
( anonim
identifier bernama
) anonim

```

### Kendala dan solusi

`python` tidak ditemukan meskipun prompt menampilkan `(venv)`, karena `venv`
dipindahkan setelah dibuat dan `activate` masih menunjuk ke path lama. Solusi:
membuat `venv` baru di `~/venv-plp`.

### Catatan penggunaan AI

1. **Yang diminta:** pohon perkiraan dan kode `t1.py`.
2. **Kesalahan AI yang ditemukan:** AI memperkirakan kode rusak menghasilkan
   `(MISSING ":")` di dalam `function_definition`. Hasil sebenarnya adalah node
   `ERROR` tanpa `function_definition`.
3. **Bukti:** output `t1.py` pada bagian "kode rusak" (`output_t1.txt`).


## Tugas 2 - Penjelajah node

`jelajah.py` menelusuri pohon secara rekursif (preorder) dan hanya mencetak
node bernama. Tiap baris berisi indentasi sesuai kedalaman, tipe node, posisi
`[baris:kolom]`, dan nama field jika ada. Nama field diambil dengan
`node.field_name_for_child(i)`, dengan `i` adalah indeks di `node.children`
(semua child), bukan di `named_children`, karena field dihitung dari urutan
semua child termasuk yang anonim.

Hasil pada `kecil.py` (`x = 1`) cocok dengan output di materi:

```
module [1:0]
  expression_statement [1:0]
    assignment [1:0]
      left: identifier [1:0]
      right: integer [1:4]
```

Skrip juga dijalankan pada `uji_nyata.py` (salinan modul `textwrap` dari pustaka
standar Python, lebih dari 100 baris). Output lengkap ada di
`tugas1-3/output_t2_nyata.txt`. Kebenaran output diverifikasi dengan mencocokkan hasil pada kecil.py dengan
output di materi, dan membandingkan hasil pada fungsi_kecil.py dengan output
Tugas 1 (output_t1.txt) untuk nama node dan label field.

Catatan penggunaan AI: kode ditulis oleh AI (Claude). Verifikasi dilakukan dengan
mencocokkan output `kecil.py` dengan output di materi.
