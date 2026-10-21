#!/usr/bin/env python3
"""
umdimage.py - Lista y extrae archivos de umdimage.dat (Danganronpa, PSP).

Este script NO contiene datos del juego. Cada persona lo usa con los
archivos de su propia copia.

Formato de umdimage.dat (ver NOTAS.txt):
  - 4 bytes: número de archivos (N)
  - N x 4 bytes: posición de cada archivo
  - los archivos, cada uno alineado a 16 bytes. No tienen nombre.

Los nombres y tamaños exactos están en el EBOOT.BIN (desencriptado), en
entradas de 12 bytes: { puntero al nombre ; posición ; tamaño }.

Uso:
  python umdimage.py listar  umdimage.dat [--eboot EBOOT.BIN] [--buscar texto]
  python umdimage.py extraer umdimage.dat 23 48 293 --salida carpeta [--eboot EBOOT.BIN]
  python umdimage.py extraer umdimage.dat --todo --salida carpeta --eboot EBOOT.BIN
"""
import argparse
import os
import struct
import sys


def leer_cabecera(ruta):
    """Devuelve la lista de posiciones y el tamaño total del contenedor."""
    with open(ruta, "rb") as f:
        n = struct.unpack("<I", f.read(4))[0]
        posiciones = list(struct.unpack("<%dI" % n, f.read(4 * n)))
    return posiciones, os.path.getsize(ruta)


def huecos(posiciones, tam_total):
    """Espacio que ocupa cada archivo dentro del contenedor (incluye relleno)."""
    res = []
    for i, p in enumerate(posiciones):
        fin = posiciones[i + 1] if i + 1 < len(posiciones) else tam_total
        res.append(fin - p)
    return res


class Eboot:
    """Lee un EBOOT.BIN desencriptado (ELF) para sacar nombres de archivo."""

    def __init__(self, ruta):
        with open(ruta, "rb") as f:
            self.datos = f.read()
        d = self.datos
        if d[:4] != b"\x7fELF":
            raise ValueError("El EBOOT no empieza por ELF: está cifrado o no es un EBOOT.")
        phoff = struct.unpack_from("<I", d, 0x1C)[0]
        phentsize = struct.unpack_from("<H", d, 0x2A)[0]
        phnum = struct.unpack_from("<H", d, 0x2C)[0]
        self.segmentos = []  # (dirección virtual, posición en archivo, tamaño)
        for i in range(phnum):
            p_type, p_offset, p_vaddr, _p_paddr, p_filesz = struct.unpack_from(
                "<5I", d, phoff + i * phentsize)
            if p_type == 1 and p_filesz:
                self.segmentos.append((p_vaddr, p_offset, p_filesz))

    def a_posicion(self, vaddr):
        for va, off, tam in self.segmentos:
            if va <= vaddr < va + tam:
                return off + (vaddr - va)
        return None

    def cadena(self, vaddr, maximo=64):
        off = self.a_posicion(vaddr)
        if off is None:
            return None
        fin = self.datos.find(b"\x00", off, off + maximo)
        if fin <= off:
            return None
        bruto = self.datos[off:fin]
        if not all(0x20 < b < 0x7F for b in bruto):
            return None
        texto = bruto.decode("ascii")
        return texto if "." in texto else None

    def tabla_de_nombres(self, posiciones, tam_hueco):
        """Busca entradas {nombre, posición, tamaño} que encajen con el contenedor.

        Devuelve un diccionario: número de archivo -> (nombre, tamaño exacto).
        """
        indice = {p: i for i, p in enumerate(posiciones)}
        res = {}
        for va, off, tam in self.segmentos:
            fin = off + tam - 12
            for pos_arch in range(off, fin, 4):
                ptr, pos, size = struct.unpack_from("<3I", self.datos, pos_arch)
                i = indice.get(pos)
                if i is None or size == 0 or size > tam_hueco[i]:
                    continue
                nombre = self.cadena(ptr)
                if nombre:
                    res[i] = (nombre, size)
        return res


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="orden", required=True)

    l = sub.add_parser("listar", help="Lista los archivos del contenedor")
    l.add_argument("umdimage")
    l.add_argument("--eboot", help="EBOOT.BIN desencriptado, para ver los nombres")
    l.add_argument("--buscar", help="Mostrar solo los nombres que contengan este texto")

    e = sub.add_parser("extraer", help="Extrae archivos por número")
    e.add_argument("umdimage")
    e.add_argument("numeros", nargs="*", type=int)
    e.add_argument("--todo", action="store_true", help="Extraer todos")
    e.add_argument("--salida", required=True, help="Carpeta de salida")
    e.add_argument("--eboot", help="EBOOT.BIN desencriptado, para nombres y tamaños exactos")

    a = ap.parse_args()
    posiciones, total = leer_cabecera(a.umdimage)
    tam_hueco = huecos(posiciones, total)
    nombres = {}
    if a.eboot:
        nombres = Eboot(a.eboot).tabla_de_nombres(posiciones, tam_hueco)
        print("Nombres encontrados en el EBOOT: %d de %d archivos"
              % (len(nombres), len(posiciones)), file=sys.stderr)

    if a.orden == "listar":
        print("%6s  %-10s  %-10s  %s" % ("Nº", "posición", "tamaño", "nombre"))
        for i, p in enumerate(posiciones):
            nombre, size = nombres.get(i, ("", tam_hueco[i]))
            if a.buscar and a.buscar.lower() not in nombre.lower():
                continue
            print("%6d  0x%08X  0x%08X  %s" % (i, p, size, nombre))
        return

    numeros = range(len(posiciones)) if a.todo else a.numeros
    if not numeros:
        sys.exit("Indica números de archivo o usa --todo.")
    os.makedirs(a.salida, exist_ok=True)
    with open(a.umdimage, "rb") as f:
        for i in numeros:
            nombre, size = nombres.get(i, ("%04d.bin" % i, tam_hueco[i]))
            f.seek(posiciones[i])
            datos = f.read(size)
            destino = os.path.join(a.salida, "%04d_%s" % (i, nombre) if i in nombres else nombre)
            with open(destino, "wb") as g:
                g.write(datos)
            print("Extraído %d -> %s (%d bytes)" % (i, destino, len(datos)))


if __name__ == "__main__":
    main()
