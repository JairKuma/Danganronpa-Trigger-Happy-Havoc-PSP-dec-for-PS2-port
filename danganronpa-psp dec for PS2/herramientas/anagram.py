#!/usr/bin/env python3
"""
anagram.py - Muestra las palabras y las partidas del minijuego de letras
("Epifanía Anagrámica") de Danganronpa (PSP, traducción al español).

Este script NO contiene datos del juego. Lee el umdimage.dat de tu copia.

Qué lee (ver NOTAS.txt):
  - Archivo 23 de umdimage.dat (23_anagram.pak): las 88 palabras, en
    UTF-16 con letras de ancho completo. Van en parejas: respuesta / señuelos.
  - Archivos anagram_XX.dat (48 a 93 en esta versión): una partida cada uno.
      c1 = 180 (¿tiempo?), c2 = nº de casillas, c3 = 2000 (¿?),
      c4 / c5 = pareja de palabras, c6 en adelante = sin descifrar.

Uso:
  python anagram.py umdimage.dat                    # archivos 48-93 por defecto
  python anagram.py umdimage.dat --eboot EBOOT.BIN  # usa los nombres del EBOOT
"""
import argparse
import struct
import unicodedata

from umdimage import Eboot, huecos, leer_cabecera

ARCHIVO_PALABRAS = 23
PARTIDAS_POR_DEFECTO = range(48, 94)


def leer_pak_textos(datos):
    """Lee un PAK de textos: { nº ; posiciones } + textos UTF-16 con FF FE."""
    n = struct.unpack_from("<I", datos, 0)[0]
    pos = list(struct.unpack_from("<%dI" % n, datos, 4)) + [len(datos)]
    textos = []
    for i in range(n):
        t = datos[pos[i]:pos[i + 1]].decode("utf-16le", errors="replace")
        textos.append(t.lstrip("\ufeff").split("\x00")[0])
    return textos


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("umdimage")
    ap.add_argument("--eboot", help="EBOOT.BIN desencriptado (para los nombres)")
    a = ap.parse_args()

    posiciones, total = leer_cabecera(a.umdimage)
    tam_hueco = huecos(posiciones, total)
    nombres = {}
    if a.eboot:
        nombres = Eboot(a.eboot).tabla_de_nombres(posiciones, tam_hueco)

    with open(a.umdimage, "rb") as f:
        def leer(i):
            size = nombres.get(i, (None, tam_hueco[i]))[1]
            f.seek(posiciones[i])
            return f.read(size)

        brutas = leer_pak_textos(leer(ARCHIVO_PALABRAS))
        palabras = [unicodedata.normalize("NFKC", w) for w in brutas]

        print("=== PALABRAS (archivo %d) ===" % ARCHIVO_PALABRAS)
        for i in range(0, len(palabras) - 1, 2):
            print("  %2d/%2d  %-17s | %s" % (i, i + 1, palabras[i], palabras[i + 1]))

        if nombres:
            partidas = sorted(i for i, (n, _) in nombres.items()
                              if n.startswith("anagram_") and n.endswith(".dat"))
        else:
            partidas = list(PARTIDAS_POR_DEFECTO)

        print("\n=== PARTIDAS ===")
        errores = 0
        for i in partidas:
            datos = leer(i)
            nombre = nombres.get(i, ("archivo %d" % i,))[0]
            if len(datos) < 10:
                print("  %-16s  (solo %d bytes: %s)" % (nombre, len(datos), datos.hex(" ")))
                continue
            v = struct.unpack_from("<%dH" % (len(datos) // 2), datos)
            casillas, resp = v[1], v[3]
            palabra = palabras[resp] if resp < len(palabras) else "?"
            ok = "OK" if len(palabra) == casillas else "¡¡NO CUADRA!!"
            if ok != "OK":
                errores += 1
            cola = list(v[5:])
            while cola and cola[-1] == 0:
                cola.pop()
            print("  %-16s  t=%3d casillas=%2d  %2d/%2d  %-16s %-13s cola=%s"
                  % (nombre, v[0], casillas, v[3], v[4], palabra, ok, cola))
        print("\nPartidas con el nº de casillas mal: %d" % errores)


if __name__ == "__main__":
    main()
