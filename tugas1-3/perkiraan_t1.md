# Pohon perkiraan Tugas 1

Perkiraan di bawah ini disusun oleh AI (Claude) dari pengetahuan tentang grammar
tree-sitter-python, sebelum t1.py dijalankan. Dibandingkan dengan hasil sebenarnya
di bagian paling bawah.

## Fungsi
```
def sapa(nama):
    return nama
```
Perkiraan:
```
(module
  (function_definition
    name: (identifier)
    parameters: (parameters
      (identifier))
    body: (block
      (return_statement
        (identifier)))))
```

## If/else
```
if x > 0:
    y = 1
else:
    y = 2
```
Perkiraan:
```
(module
  (if_statement
    condition: (comparison_operator
      (identifier)
      (integer))
    consequence: (block
      (expression_statement
        (assignment
          left: (identifier)
          right: (integer))))
    alternative: (else_clause
      body: (block
        (expression_statement
          (assignment
            left: (identifier)
            right: (integer)))))))
```

## Kelas
```
class Hewan:
    def bicara(self):
        return 1
```
Perkiraan:
```
(module
  (class_definition
    name: (identifier)
    body: (block
      (function_definition
        name: (identifier)
        parameters: (parameters
          (identifier))
        body: (block
          (return_statement
            (integer)))))))
```

## Kode rusak (titik dua setelah def sapa(nama) dihapus)
Perkiraan: pohonnya mirip pohon fungsi di atas, tetapi parser menyisipkan
node `(MISSING ":")` di dalam `function_definition`, dan `has_error` bernilai True.

## Node anonim yang tersembunyi
`def`, `:`, `(`, `)`, `if`, `else`, `class`, `return`, `=`, `>`.
(`(` dan `)` berada satu tingkat lebih dalam, di dalam node `parameters`.)

## Hasil sebenarnya dan selisihnya (isi setelah menjalankan t1.py)
## Hasil sebenarnya dan selisihnya

| Potongan | Perkiraan | Hasil sebenarnya |
| --- | --- | --- |
| `x = 1` | sesuai materi | **Cocok** |
| Fungsi | `function_definition` dengan `name`, `parameters`, `body: (block (return_statement ...))` | **Cocok** |
| If/else | `if_statement` dengan `condition: (comparison_operator ...)`, `consequence: (block ...)`, `alternative: (else_clause body: (block ...))` | **Cocok** |
| Kelas | `class_definition` dengan `body: (block (function_definition ...))` | **Cocok** |
| Kode rusak | Pohon fungsi tetap utuh, dengan `(MISSING ":")` di dalam `function_definition` | **Meleset.** Hasilnya `(module (ERROR (identifier) (parameters (identifier)) (identifier)))`. Tidak ada `function_definition` dan tidak ada `MISSING`. |

### Yang saya pelajari dari selisihnya
- Pada kode rusak, parser tidak menyisipkan token yang hilang. Ia membungkus potongan yang tidak bisa dicocokkan ke dalam satu node `ERROR`. Node `def` dan `return` (anonim) tidak tercetak, dan `has_error` bernilai `True`.
- Pohon valid hanya menampilkan field untuk operand yang diberi label di grammar. Pada `x > 0`, operandnya (`comparison_operator`) tidak berlabel, sedangkan `x = 1` punya `left:` dan `right:`.

### Node anonim yang ditemukan
`def` dan `:` (anak langsung `function_definition`, terlihat di output). Perkiraan: `(`, `)`, `if`, `else`, `class`, `return`, `=`, `>` juga anonim. Karena belum ada di output, buktikan dengan satu pengecekan tambahan (lihat di bawah).

### children vs named_children (dari output)
- `children` memuat 5 anak: `def`, `identifier`, `parameters`, `:`, `block`.
- `named_children` hanya 3: `identifier`, `parameters`, `block`.
- Selisihnya adalah dua node anonim (`def` dan `:`).