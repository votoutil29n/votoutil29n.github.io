# Voto útil 29-N

**¿Dónde aporta más tu voto a la izquierda?** Herramienta para ver, provincia por provincia, cuántos escaños aporta tu voto al bloque de izquierdas en las elecciones generales del 29 de noviembre de 2026, y si otra opción aportaría más.

Web: https://votoutil29n.github.io/

Eliges provincia y a quién piensas votar. La herramienta te muestra:

- cuánto aporta tu voto a la izquierda, comparado con las demás listas de izquierda de tu provincia;
- qué votar si priorizas a tu partido y qué votar si priorizas a la izquierda en conjunto;
- qué pasó con tu voto en 2023, con los resultados oficiales.

No es una recomendación de voto. El método, los supuestos y los límites están en [METODO.md](METODO.md).

## Estructura

| Ruta | Contenido |
|---|---|
| `index.html` | La herramienta (página única, sin servidor). Se genera; no se edita a mano. |
| `metodo.html`, `METODO.md` | Metodología, resumen por provincia, límites y fuentes. Se generan. |
| `web/` | Plantilla de la herramienta, textos de la metodología y configuración (`config.json`). |
| `modelo/` | Código en Python: proyección, simulaciones, impacto en 2023, clasificación y construcción de la web. |
| `datos/` | Resultados de 2023, encuestas de octubre de 2026 y salidas de las simulaciones. |

## Reconstruir la web

Requiere Python 3 con numpy, pandas y markdown.

```
python3 modelo/impacto2023.py .
python3 modelo/clasificar.py .
python3 modelo/construir_web.py .
python3 modelo/construir_metodo.py .
```

## Actualizar con nuevas encuestas

1. Añade las encuestas nuevas a `datos/encuestas_oct2026.csv` y calcula la media.
2. Lanza la simulación principal con los nuevos objetivos, por ejemplo:
   `python3 modelo/model.py . 250000 0.05 main '{"PP":31.5,"PSOE":27.0,"VOX":19.0,"ALT_TARGET":10.0}'`
3. Repite cada escenario de `modelo/escenarios.txt` con los mismos objetivos.
4. Reconstruye la web con los cuatro comandos de arriba.
5. Actualiza la fecha de los datos en `web/plantilla.html` y `web/metodo_cabecera.md`.

## Veda de encuestas

La ley electoral (LOREG, art. 69.7) prohíbe publicar y difundir sondeos en los cinco días anteriores a la votación: del 24 al 28 de noviembre de 2026. Desde el 24 de noviembre la página oculta sus cálculos y muestra un aviso hasta el cierre de los colegios. Los datos siguen en el código de la página, así que lo prudente es desactivar GitHub Pages esos días y no promocionarla. Esto no es asesoramiento jurídico.

## Licencias

- Código (`modelo/`, `web/`): MIT.
- Textos y datos (`METODO.md`, `datos/`): CC BY-SA 4.0. Los resultados de 2023 y la tabla de encuestas proceden de Wikipedia (CC BY-SA 4.0), que cita al Ministerio del Interior y a cada encuestadora.

## Créditos y errores

Proyecto independiente, sin relación con ningún partido. Hecho con ayuda de inteligencia artificial (Claude, de Anthropic). Si encuentras un error, [abre una incidencia](https://github.com/votoutil29n/votoutil29n.github.io/issues).
