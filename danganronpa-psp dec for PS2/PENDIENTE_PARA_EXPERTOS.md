# Pendiente para personas con experiencia

Lo que sigue necesita ingeniería inversa del código (Ghidra) o depuración en vivo (depurador de PPSSPP). Todo lo que ya sabemos está en `NOTAS.txt`.

## Preparación

- **Dirección base.** Ghidra carga el EBOOT.BIN en `0x0`; en PPSSPP se carga normalmente en `0x08804000`. Hay que ajustarlo para que las direcciones coincidan al depurar.
- **Tablas sin reconocer.** Ghidra no ha marcado como punteros muchas entradas de la tabla de archivos (por ejemplo la de `13_skilldesc.pak`, en `0xfc0e0`), así que faltan referencias (XREF). Definir la tabla como un array de estructuras `{ char *nombre; u32 posicion; u32 tamano; }` debería hacer aparecer las referencias al código que la usa.

## Formatos

- **`LLFS`**: aparece al principio de varios sub-archivos de `bin_anagram.pak`, junto a imágenes GIM. Probablemente indica cómo se colocan los gráficos en pantalla (aparece el valor 480, el ancho de la pantalla del PSP).
- **Scripts `.lin`**: probar `lin_compiler` (danganronpa-tools) con los de la versión PSP.
- **`umdimage2.dat`** (213 MB): sin investigar. Ninguna de las posiciones buscadas hasta ahora estaba en él.
- **`voice.pak`** y **`bgm.pak`**: sin investigar.

## Minijuego de letras ("Epifanía Anagrámica")

Ya se sabe qué palabras usa cada partida y su número de casillas (ver `NOTAS.txt` y `herramientas/anagram.py`). Falta:

- **La "cola" de cada `anagram_XX.dat`** (a partir del campo 6): pares que suben con la dificultad (0/1, 1/2, 2/3, 3/4), otros números (por ejemplo 24, 7, 6, 31) y una serie de 0/1 en las partidas de la historia.
- **Los campos 1 y 3**: 180 y 2000 casi siempre (`anagram_52.dat` tiene 300). ¿Tiempo? ¿Puntuación?
- **La tabla de configuración** (sub-archivo 12 de `bin_anagram.pak`, 51 entradas de 14 números): qué significa cada columna y si la cola de los `.dat` apunta a ella.
- **`anagram_52.dat`** (capítulo 5): usa la palabra en inglés FISTFIGHT con valores distintos al resto. ¿Sale en el juego sin traducir o es una partida especial?
- **Las 33 partidas `anagram_200`–`232`** y `anagram_101`: ¿en qué modo de juego se usan?
- **El código del minijuego**: localizarlo en Ghidra y comprobar si la traducción lo modificó (el EBOOT tiene fecha de 2016, posterior al juego).

## Port a PS2

Librerías de Sony que usa el juego y que habría que sustituir (lista completa en `NOTAS.txt`, sección 5): gráficos (`sceGe_user`), pantalla, controles, audio (ATRAC3plus), vídeo (PMF), archivos y guardado. Resolución: 480×272 en PSP frente a 640×448 en PS2.
