# Danganronpa (PSP) – Documentación técnica

Documentación del funcionamiento interno de **Danganronpa: Trigger Happy Havoc** para PSP, en concreto de la versión con la **traducción al español** hecha por aficionados.

El objetivo a largo plazo es que alguien con experiencia pueda hacer una **reimplementación del motor para PS2**, al estilo de ScummVM: un programa nuevo que lea los archivos del juego de la copia de cada usuario.

## ⚠️ Normas del proyecto

- **Este repositorio no contiene ni debe contener archivos del juego**: ni ISO, ni EBOOT.BIN, ni umdimage.dat, ni imágenes, audio, vídeos o textos extraídos, ni proyectos de Ghidra (llevan el ejecutable dentro). El `.gitignore` ya bloquea esos tipos de archivo.
- Solo se comparte **documentación** (formatos, direcciones, estructuras) y **herramientas propias**.
- Cada colaborador trabaja con **su propia copia** del juego.
- La traducción se distribuye como **parche**, nunca como ISO.

## Estado actual

| Parte | Estado |
|---|---|
| Estructura del ISO | ✅ Documentada |
| EBOOT.BIN | ✅ Desencriptado en la versión traducida; se abre en Ghidra |
| Formato de `umdimage.dat` (contenedor principal, 4107 archivos) | ✅ Descifrado |
| Tabla de nombres/posiciones/tamaños en el EBOOT | ✅ Descifrada |
| Formato PAK (contenedores anidados) | ✅ Descifrado |
| Texto del juego (UTF-16, `FF FE`) | ✅ Descifrado |
| Imágenes (formato GIM de Sony) | ✅ Identificado |
| Minijuego de letras ("Epifanía Anagrámica") | 🟡 Datos principales descifrados |
| Formato `LLFS` | ❌ Desconocido |
| Scripts `.lin` | ❌ Sin probar con la versión PSP |
| Código del motor en Ghidra | ❌ Sin empezar |

Todos los detalles, con cada dato marcado como **[CONFIRMADO]**, **[PROBABLE]** o **[PENDIENTE]**, están en [`NOTAS.txt`](NOTAS.txt).
Lo que necesita a alguien con experiencia está en [`PENDIENTE_PARA_EXPERTOS.md`](PENDIENTE_PARA_EXPERTOS.md).

## Herramientas

Requieren Python 3. No contienen datos del juego: se usan con los archivos de tu copia.

### `herramientas/umdimage.py`

Lista y extrae archivos de `umdimage.dat`. Con `--eboot` usa el EBOOT.BIN (desencriptado) para poner nombre y tamaño exacto a cada archivo.

```
python umdimage.py listar  umdimage.dat --eboot EBOOT.BIN
python umdimage.py listar  umdimage.dat --eboot EBOOT.BIN --buscar anagram
python umdimage.py extraer umdimage.dat 23 87 --salida extraido --eboot EBOOT.BIN
```

### `herramientas/anagram.py`

Muestra las 88 palabras del minijuego de letras y todas sus partidas, y comprueba que el número de casillas de cada partida coincide con las letras de la respuesta.

```
python anagram.py umdimage.dat --eboot EBOOT.BIN
```

## Herramientas de terceros usadas

- **Ghidra 11.1.2** + extensión **ghidra-allegrex** (kotcrab), para analizar el EBOOT.BIN.
- **HxD**, editor hexadecimal.
- **UMDGen**, para abrir el ISO.
- [vn-tools/danganronpa-tools](https://github.com/vn-tools/danganronpa-tools) y [drpakmapgen](https://github.com/Visual-Novel-Decompilation-Project/drpakmapgen): pensadas para la versión de PC; pendiente comprobar si sirven para la de PSP.
