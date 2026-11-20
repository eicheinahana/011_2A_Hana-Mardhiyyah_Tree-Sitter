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


## Tugas 3 - Query pertama

`q.py` membaca file kode dari `argv[1]` dan file pola `.scm` dari `argv[2]`, lalu
mencetak hasil `QueryCursor.matches` beserta nomor baris, sehingga cukup mengedit
file `.scm` tanpa mengubah kode Python. Tiga query yang dibuat:

1. **Fungsi dan jumlah parameter** (`fungsi.scm`): menangkap `name` dan
   `parameters` dalam satu pola, lalu jumlah parameter dihitung dari
   `named_child_count` node `parameters`. Dipakai `matches`, bukan `captures`,
   karena butuh pasangan nama dan parameter.
2. **Pemanggilan print** (`print.scm`): `call` dengan `function` berupa
   `identifier` yang dibatasi predikat `#eq? @fn "print"`.
3. **Import** (`import.scm`): `import_statement` dan `import_from_statement`.
   Nama node dilihat dulu dari pohon hasil `jelajah.py`
   (`output_t3_pohon.txt`), tidak ditebak.

Hasil dicocokkan dengan hitungan manual pada `contoh.py`: tiga fungsi (`tambah`
2 parameter, `sapa` 1, `kali` 4 karena `self` ikut terhitung), dua pemanggilan
`print` (baris 10 dan 19), dan dua import (`os` dan `pathlib`).

Fungsi:
```
@nama[baris 5]='tambah'  @params[baris 5]='(a, b)'  jumlah_parameter=2
@nama[baris 9]='sapa'  @params[baris 9]='(nama)'  jumlah_parameter=1
@nama[baris 15]='kali'  @params[baris 15]='(self, a, b, c)'  jumlah_parameter=4
-- total: 3 hasil

```
Print:
```
@fn[baris 10]='print'  @args[baris 10]='("halo", nama)'
@fn[baris 19]='print'  @args[baris 19]='(tambah(1, 2))'
-- total: 2 hasil

```
Import:
```
@modul[baris 1]='os'
@modul[baris 2]='pathlib'
-- total: 2 hasil

```

### Kendala dan solusi
tidak ada kendala

### Catatan penggunaan AI
1. **Yang diminta:** menulis `q.py`, `contoh.py`, dan ketiga file query.
2. **Kesalahan atau kekurangan AI yang ditemukan:** (PILIH yang benar-benar terjadi)
   - Jumlah parameter `kali` ternyata 4 karena `self` ikut terhitung, sedangkan
     hitungan manual awal 3; `named_child_count` tidak membedakan `self`.
     Bukti: `output_t3_fungsi.txt`.
3. **Pembuktian:** hasil query dicocokkan dengan hitungan manual pada `contoh.py`.

## Tugas 4 - Grammar DSL filter

Grammar `filter` dibuat untuk bahasa pencarian lanjutan seperti
`status = "open" and (priority > 2 or owner = "budi")`. Yang didukung:
perbandingan (`=`, `!=`, `>`, `<`, `>=`, `<=`), string, angka, boolean,
`and`/`or`/`not`, kurung, `in`, dan `contains`.

**Prioritas operator.** `not` (prec 3) lebih kuat dari `and` (prec.left 2), dan
`and` lebih kuat dari `or` (prec.left 1). Karena itu `a = 1 or b = 2 and c = 3`
dibaca sebagai `a = 1 or (b = 2 and c = 3)`.

**`word: $ => $.identifier`** dipasang supaya kata kunci seperti `and`, `or`, dan
`in` tidak terbaca sebagai identifier.

**Field** diberikan pada child penting (`field`, `operator`, `value`, `left`,
`right`, `operand`) agar pohon tidak bergantung pada urutan. Field `operator`
tidak muncul di pohon tes karena isinya node anonim.

**Tes.** Ada 8 kasus di `test/corpus/dasar.txt`: string, angka, boolean,
prioritas `and`/`or`, kurung, `not`, `in` dengan tiga nilai
(`in_expression`), dan `contains`.

```
  dasar:
      1. ✓ [32mPerbandingan string[0m
      2. ✓ [32mPerbandingan angka[0m
      3. ✓ [32mNilai boolean[0m
      4. ✓ [32mPrioritas and lebih kuat dari or[0m
      5. ✓ [32mKurung mengubah pengelompokan[0m
      6. ✓ [32mOperator not[0m
      7. ✓ [32mOperator in dengan tiga nilai[0m
      8. ✓ [32mOperator contains[0m

Total parses: 8; successful parses: 8; failed parses: 0; success percentage: 100.00%; average speed: 4945 bytes/ms
```

### Kendala dan solusi
- `tree-sitter generate` gagal ketika dijalankan dari root repo karena mencari
  `grammar.js` di folder yang salah. Solusi: menjalankannya dari dalam
  `tree-sitter-filter/`.

### Catatan penggunaan AI
1. **Yang diminta:** menulis `grammar.js` dan kasus uji corpus.
2. **Kesalahan atau kekurangan AI yang ditemukan:** 
    - **`grammar.js` ditulis dengan gaya CommonJS, padahal proyek memakai ES module.**
      AI menulis `module.exports = grammar({ ... })`. Namun `package.json` hasil
      `tree-sitter init` berisi `"type": "module"`, sehingga `tree-sitter generate`
      gagal dengan pesan:
      `ReferenceError: module is not defined in ES module scope`
      dan `Failed to load grammar.js -- node process exited with status 1`.
      - **Bukti:** pesan error di terminal saat menjalankan `tree-sitter generate`
        pertama kali. Perintah `tree-sitter parse` setelahnya hanya menghasilkan
        node `ERROR` karena parser belum berhasil dibuat.
      - **Perbaikan:** mengganti baris pertama menjadi `export default grammar({`.
      - **Verifikasi:** setelah diperbaiki, `tree-sitter generate` berhasil dan
        `tree-sitter test` dapat dijalankan (hasilnya di
        `tree-sitter-filter/hasil_test.txt`).
3. **Pembuktian:** hasil `tree-sitter test` pada `hasil_test.txt`.


## Tugas 5 - Highlight

Highlight untuk DSL filter dibuat lewat `queries/highlights.scm`. Konfigurasi
dilakukan dengan `tree-sitter init-config`, lalu `parser-directories` diisi
folder induk dari `tree-sitter-filter/` (`/mnt/d/plp`), bukan folder grammar
itu sendiri. Di `tree-sitter.json`, `file-types` berisi `filter`.

Query dibuat bertahap: dimulai dari `(string) @string` untuk membuktikan
konfigurasi benar, lalu ditambah kata kunci (`and or not in contains`), operator
perbandingan, angka, boolean, nama field pada `comparison`, `in_expression`,
dan `contains_expression`, serta tanda kurung dan koma.

Karena laporan berformat teks, bukti disajikan dari `tree-sitter query` (capture
yang cocok) pada `contoh.filter`, bukan tangkapan layar warna:

```
contoh.filter
  pattern: 6
    capture: 5 - property, start: (0, 0), end: (0, 6), text: `status`
  pattern: 0
    capture: 0 - keyword, start: (0, 7), end: (0, 9), text: `in`
  pattern: 8
    capture: 6 - punctuation.bracket, start: (0, 10), end: (0, 11), text: `(`
  pattern: 2
    capture: 2 - string, start: (0, 11), end: (0, 17), text: `"open"`
  pattern: 8
    capture: 6 - punctuation.bracket, start: (0, 17), end: (0, 18), text: `,`
  pattern: 2
    capture: 2 - string, start: (0, 19), end: (0, 28), text: `"pending"`
  pattern: 8
    capture: 6 - punctuation.bracket, start: (0, 28), end: (0, 29), text: `)`
  pattern: 0
    capture: 0 - keyword, start: (0, 30), end: (0, 33), text: `and`
  pattern: 8
    capture: 6 - punctuation.bracket, start: (0, 34), end: (0, 35), text: `(`
  pattern: 5
    capture: 5 - property, start: (0, 35), end: (0, 43), text: `priority`
  pattern: 1
    capture: 1 - operator, start: (0, 44), end: (0, 46), text: `>=`
  pattern: 3
    capture: 3 - number, start: (0, 47), end: (0, 48), text: `2`
  pattern: 0
    capture: 0 - keyword, start: (0, 49), end: (0, 51), text: `or`
  pattern: 5
    capture: 5 - property, start: (0, 52), end: (0, 57), text: `owner`
  pattern: 1
    capture: 1 - operator, start: (0, 58), end: (0, 59), text: `=`
  pattern: 2
    capture: 2 - string, start: (0, 60), end: (0, 66), text: `"budi"`
  pattern: 8
    capture: 6 - punctuation.bracket, start: (0, 66), end: (0, 67), text: `)`
  pattern: 0
    capture: 0 - keyword, start: (0, 68), end: (0, 71), text: `and`
  pattern: 0
    capture: 0 - keyword, start: (0, 72), end: (0, 75), text: `not`
  pattern: 5
    capture: 5 - property, start: (0, 76), end: (0, 84), text: `archived`
  pattern: 1
    capture: 1 - operator, start: (0, 85), end: (0, 86), text: `=`
  pattern: 4
    capture: 4 - constant.builtin, start: (0, 87), end: (0, 91), text: `true`
  pattern: 0
    capture: 0 - keyword, start: (0, 92), end: (0, 95), text: `and`
  pattern: 7
    capture: 5 - property, start: (0, 96), end: (0, 101), text: `title`
  pattern: 0
    capture: 0 - keyword, start: (0, 102), end: (0, 110), text: `contains`
  pattern: 2
    capture: 2 - string, start: (0, 111), end: (0, 120), text: `"invoice"`

```

### Kendala dan solusi
tidak ada

### Catatan penggunaan AI
1. **Yang diminta:** menulis `queries/highlights.scm` dan langkah konfigurasi.
2. **Kesalahan atau kekurangan AI yang ditemukan:** tidak ada
3. **Pembuktian:** isi `hasil_highlight.txt` dan hasil `tree-sitter highlight`.


## Tugas 6 - cek.py

`cek.py <folder>` memeriksa semua file `*.py` di sebuah folder dan melaporkan:

1. **Komentar TODO/FIXME**: query `((comment) @c (#match? @c "TODO|FIXME"))`,
   dilaporkan beserta file dan barisnya.
2. **Fungsi lebih dari 30 baris**: query `function_definition`, panjangnya
   dihitung dari `end_point[0] - start_point[0] + 1`. Semua fungsi dihitung,
   termasuk method di dalam kelas dan fungsi bersarang.
3. **File dengan syntax error**: `root_node.has_error`, lalu fungsi rekursif
   mencari node pertama yang `is_error` atau `is_missing` untuk melaporkan
   baris pertama yang bermasalah.

Folder `venv`, `.git`, dan `node_modules` dilewati. Isi file dibaca sebagai
byte dan didekode dengan `errors="replace"` agar file dengan encoding aneh
tidak membuat skrip berhenti.

Hasil pada folder uji buatan sendiri (`uji/`):
```
[PANJANG] uji/panjang.py:1: fungsi fungsi_panjang = 37 baris
[ERROR] uji/rusak.py:1: syntax error (ERROR)
[TODO]  uji/todo.py:1: # TODO: tambahkan validasi input
[TODO]  uji/todo.py:3: # FIXME: belum menangani x negatif
-- selesai: 3 file diperiksa

```

Hasil pada repo nyata "https://github.com/psf/requests", cuplikan:
```
[PANJANG] /home/hana/uji-repo/src/requests/__init__.py:60: fungsi check_compatibility = 37 baris
[TODO]  /home/hana/uji-repo/src/requests/_types.py:60: # TODO: move to collections.abc when Python >= 3.12
[TODO]  /home/hana/uji-repo/src/requests/_types.py:61: # TODO: move to typing when Python >= 3.13
[TODO]  /home/hana/uji-repo/src/requests/adapters.py:715: # TODO: Remove this in 3.0.0: see #2811
[PANJANG] /home/hana/uji-repo/src/requests/adapters.py:85: fungsi _urllib3_request_context = 35 baris
[PANJANG] /home/hana/uji-repo/src/requests/adapters.py:269: fungsi proxy_manager_for = 37 baris
[PANJANG] /home/hana/uji-repo/src/requests/adapters.py:307: fungsi cert_verify = 57 baris
[PANJANG] /home/hana/uji-repo/src/requests/adapters.py:365: fungsi build_response = 37 baris
[PANJANG] /home/hana/uji-repo/src/requests/adapters.py:403: fungsi build_connection_pool_key_attributes = 51 baris
[PANJANG] /home/hana/uji-repo/src/requests/adapters.py:455: fungsi get_connection_with_tls_context = 56 baris
[PANJANG] /home/hana/uji-repo/src/requests/adapters.py:512: fungsi get_connection = 42 baris
[PANJANG] /home/hana/uji-repo/src/requests/adapters.py:565: fungsi request_url = 33 baris
[PANJANG] /home/hana/uji-repo/src/requests/adapters.py:634: fungsi send = 115 baris
[PANJANG] /home/hana/uji-repo/src/requests/api.py:24: fungsi request = 48 baris
[PANJANG] /home/hana/uji-repo/src/requests/auth.py:34: fungsi _basic_auth_str = 42 baris
[PANJANG] /home/hana/uji-repo/src/requests/auth.py:157: fungsi build_digest_header = 110 baris
[PANJANG] /home/hana/uji-repo/src/requests/auth.py:273: fungsi handle_401 = 47 baris
[PANJANG] /home/hana/uji-repo/src/requests/cookies.py:494: fungsi create_cookie = 35 baris
[PANJANG] /home/hana/uji-repo/src/requests/help.py:67: fungsi info = 57 baris
[TODO]  /home/hana/uji-repo/src/requests/hooks.py:29: # TODO: response is the only one
[TODO]  /home/hana/uji-repo/src/requests/models.py:687: # TODO: can be fixed by flipping the conditionals
[TODO]  /home/hana/uji-repo/src/requests/models.py:1016: # TODO: remove cast after iter_lines rewrite
[PANJANG] /home/hana/uji-repo/src/requests/models.py:183: fungsi _encode_files = 69 baris
[PANJANG] /home/hana/uji-repo/src/requests/models.py:323: fungsi __init__ = 33 baris
[PANJANG] /home/hana/uji-repo/src/requests/models.py:483: fungsi prepare_url = 81 baris
[PANJANG] /home/hana/uji-repo/src/requests/models.py:576: fungsi prepare_body = 77 baris
[PANJANG] /home/hana/uji-repo/src/requests/models.py:765: fungsi __init__ = 46 baris
[PANJANG] /home/hana/uji-repo/src/requests/models.py:914: fungsi iter_content = 64 baris
[PANJANG] /home/hana/uji-repo/src/requests/models.py:994: fungsi iter_lines = 39 baris
[PANJANG] /home/hana/uji-repo/src/requests/models.py:1054: fungsi text = 36 baris
[PANJANG] /home/hana/uji-repo/src/requests/models.py:1091: fungsi json = 34 baris
[PANJANG] /home/hana/uji-repo/src/requests/sessions.py:154: fungsi should_strip_auth = 31 baris
[PANJANG] /home/hana/uji-repo/src/requests/sessions.py:186: fungsi resolve_redirects = 122 baris
[PANJANG] /home/hana/uji-repo/src/requests/sessions.py:334: fungsi rebuild_proxies = 35 baris
[PANJANG] /home/hana/uji-repo/src/requests/sessions.py:442: fungsi __init__ = 62 baris
[PANJANG] /home/hana/uji-repo/src/requests/sessions.py:511: fungsi prepare_request = 45 baris
[PANJANG] /home/hana/uji-repo/src/requests/sessions.py:557: fungsi request = 97 baris
[PANJANG] /home/hana/uji-repo/src/requests/sessions.py:752: fungsi send = 78 baris
[PANJANG] /home/hana/uji-repo/src/requests/sessions.py:831: fungsi merge_environment_settings = 38 baris
[PANJANG] /home/hana/uji-repo/src/requests/utils.py:99: fungsi proxy_bypass_registry = 37 baris
[PANJANG] /home/hana/uji-repo/src/requests/utils.py:160: fungsi super_len = 69 baris
[PANJANG] /home/hana/uji-repo/src/requests/utils.py:231: fungsi get_netrc_auth = 50 baris
[PANJANG] /home/hana/uji-repo/src/requests/utils.py:290: fungsi extract_zipped_paths = 36 baris
[PANJANG] /home/hana/uji-repo/src/requests/utils.py:440: fungsi parse_dict_header = 32 baris
[PANJANG] /home/hana/uji-repo/src/requests/utils.py:633: fungsi get_unicode_from_response = 39 baris
[PANJANG] /home/hana/uji-repo/src/requests/utils.py:810: fungsi should_bypass_proxies = 61 baris
[PANJANG] /home/hana/uji-repo/src/requests/utils.py:965: fungsi parse_header_links = 35 baris
[PANJANG] /home/hana/uji-repo/tests/test_lowlevel.py:127: fungsi test_digestauth_401_count_reset_on_redirect = 63 baris
[PANJANG] /home/hana/uji-repo/tests/test_lowlevel.py:192: fungsi test_digestauth_401_only_sent_once = 44 baris
[PANJANG] /home/hana/uji-repo/tests/test_lowlevel.py:238: fungsi test_digestauth_only_on_4xx = 35 baris
[PANJANG] /home/hana/uji-repo/tests/test_lowlevel.py:308: fungsi test_redirect_rfc1808_to_non_ascii_location = 32 baris
[PANJANG] /home/hana/uji-repo/tests/test_lowlevel.py:364: fungsi test_fragment_update_on_redirect = 41 baris
[PANJANG] /home/hana/uji-repo/tests/test_requests.py:450: fungsi test_cookielib_cookiejar_on_redirect = 31 baris
[PANJANG] /home/hana/uji-repo/tests/test_requests.py:683: fungsi test_basicauth_with_netrc = 34 baris
[PANJANG] /home/hana/uji-repo/tests/test_requests.py:841: fungsi test_POSTBIN_SEEKED_OBJECT_WITH_NO_ITER = 40 baris
[PANJANG] /home/hana/uji-repo/tests/test_requests.py:1647: fungsi test_transport_adapter_ordering = 37 baris
[PANJANG] /home/hana/uji-repo/tests/test_requests.py:2286: fungsi test_custom_redirect_mixin = 43 baris
[PANJANG] /home/hana/uji-repo/tests/test_requests.py:2959: fungsi test_different_connection_pool_for_tls_settings_verify_bundle_expired_cert = 32 baris
[PANJANG] /home/hana/uji-repo/tests/test_requests.py:2992: fungsi test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert = 31 baris
[PANJANG] /home/hana/uji-repo/tests/test_requests.py:3024: fungsi test_different_connection_pool_for_mtls_settings = 38 baris
[TODO]  /home/hana/uji-repo/tests/test_testserver.py:97: # TODO: figure out why this sometimes fails when using pytest-xdist.
[PANJANG] /home/hana/uji-repo/tests/test_utils.py:886: fungsi test_should_bypass_proxies_win_registry = 35 baris
[PANJANG] /home/hana/uji-repo/tests/testserver/server.py:139: fungsi __init__ = 31 baris
-- selesai: 37 file diperiksa

```

Pencocokan manual pada 2 file acak:

- `src/requests/hooks.py`: `cek.py` melaporkan 1 komentar TODO di baris 29
  (`# TODO: response is the only one`). Dicek manual dengan `grep`: (cocok / tidak cocok).
- `src/requests/api.py`: `cek.py` melaporkan fungsi `request` di baris 24 dengan
  panjang 48 baris (berakhir di baris 71). Dicek manual dengan `sed`: (cocok / tidak cocok).

### Kendala dan solusi
tidak ada kendala

### Catatan penggunaan AI
1. **Yang diminta:** menulis `cek.py`, file uji, dan `README.md`.
2. **Kesalahan atau kekurangan AI yang ditemukan:** (ISI hanya jika benar-benar
   terjadi, misalnya jenis error yang dilaporkan berbeda dari perkiraan AI,
   atau hasil yang tidak cocok dengan pengecekan manual, lengkap dengan buktinya.)
3. **Pembuktian:** `output_uji.txt`, `output_repo_nyata.txt`, dan pencocokan
   manual pada 2 file acak.