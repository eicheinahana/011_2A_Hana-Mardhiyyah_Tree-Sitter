import os
from pathlib import Path


def tambah(a, b):
    return a + b


def sapa(nama):
    print("halo", nama)
    return nama


class Hitung:
    def kali(self, a, b, c):
        return a * b * c


print(tambah(1, 2))
