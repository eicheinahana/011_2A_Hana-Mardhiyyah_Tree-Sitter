# Draf Proposal: Pemeriksa Aturan Kode Node.js/Express dengan Tree-sitter

## 1. Judul
Linter aturan internal tim untuk aplikasi web Node.js/Express berbasis tree-sitter.

## 2. Masalah
Tim pengembang web enterprise punya aturan internal yang sering terlewat saat code
review, misalnya larangan `console.log` di kode produksi dan query SQL yang dibentuk
dengan penggabungan string. Reviewer dan developer yang mengalaminya: pemeriksaan
manual lambat dan tidak konsisten antar reviewer.

## 3. Kenapa tidak cukup dengan AI saja
Meminta AI me-review setiap file bersifat probabilistik (hasil bisa berbeda tiap
dijalankan) dan berbiaya per token untuk basis kode besar. Tool berbasis tree-sitter
deterministik, hampir tanpa biaya per pengecekan, dan bisa dijalankan otomatis di CI
pada setiap commit. Regex atas teks mentah akan gagal karena tidak bisa membedakan
`console.log` di kode asli dengan yang ada di komentar atau string.

## 4. Bahasa dan framework target
JavaScript (Express). Grammar: `tree-sitter-javascript` (tersedia di PyPI).

## 5. Contoh kode
Harus terdeteksi:
```js
console.log("debug", user);
db.query("SELECT * FROM users WHERE id = " + req.params.id);
```
Tidak boleh terdeteksi:
```js
// console.log("ini komentar")
const s = "console.log bukan pemanggilan";
logger.info("pesan");
```

## 6. Rancangan query (aturan 1: larangan console.log)
```scheme
(call_expression
  function: (member_expression
    object: (identifier) @obj
    property: (property_identifier) @prop)
  (#eq? @obj "console")
  (#eq? @prop "log"))
```
Aturan 2 (SQL dengan penggabungan string) memakai pola `binary_expression`
dengan operator `+` pada argumen pemanggilan `.query(...)`; akan dirinci setelah
nama node dilihat langsung dengan penjelajah pohon.

## 7. Bentuk output
Laporan terminal (`file:baris: pesan aturan`) dengan kode keluar tidak nol bila ada
temuan, supaya bisa dipakai sebagai langkah di CI.

## 8. Cara evaluasi
Diuji pada satu repo open source Express. Sampel 20 temuan dicek manual untuk
menghitung berapa yang benar (presisi), dan beberapa file dicek manual untuk
melihat temuan yang terlewat.

## 9. Rencana kerja per minggu dan risiko
- Minggu 1: aturan `console.log` dan pengujian pada kode contoh.
- Minggu 2: aturan SQL penggabungan string.
- Minggu 3: pengujian pada repo nyata dan pengecekan manual.
- Minggu 4: keluaran untuk CI dan perapian.
- Minggu 5: laporan dan demo.

Risiko: banyak gaya penulisan query (template literal, variabel perantara) yang
sulit ditangkap; skop dibatasi pada pola penggabungan langsung.