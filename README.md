# Análisis y visualización de propiedades mecánicas de aceros al carbono

Sitio académico para explorar composición, procesamiento y propiedades mecánicas del conjunto **Steel – Property and Composition (Carbon Steel)**. Utiliza HTML5, CSS3, SVG y módulos JavaScript sin servidor de aplicaciones, dependencias de frontend ni compilación.

## Uso

Abre la carpeta en WebStorm y utiliza **Open in Browser** sobre `index.html`, o ejecuta `python -m http.server 8000` desde la raíz y visita `http://localhost:8000/`. Se necesita HTTP porque los navegadores restringen `fetch()` cuando la página se abre mediante `file://`.

La página incluye relaciones entre carbono nominal y propiedades, comparaciones por procesamiento y un explorador de correlaciones SAE 1XXX. Los controles de las gráficas recalculan sus estadísticas descriptivas. Las tablas complementarias permiten buscar por grado, filtrar, ordenar, paginar y exportar CSV UTF-8; sus filtros son independientes de los de las gráficas. Las exportaciones de registros conservan el texto numérico original del CSV.

La comparación por procesamiento incluye medias con intervalos descriptivos de confianza del 95 % y las pruebas ANOVA y post hoc verificadas para las poblaciones originales. Los selectores de la comparación actualizan ambas vistas. La superposición de intervalos individuales no es una prueba de diferencias entre pares.

## Archivos principales

- `data/steels.csv`: base depurada; no se modifica.
- `data/statistical-results.json`: resultados inferenciales reproducidos para las poblaciones originales fijas.
- `js/stats.js`: estadísticas descriptivas, correlaciones y residualización.
- `js/charts-point2.js`, `js/charts-processing.js`, `js/charts-point3.js`: visualizaciones.
- `js/tables.js`, `js/inference.js`: tablas y lectura de resultados verificados.
- `js/charts-anova.js`, `data/mean-ci.json`: visualización e intervalos descriptivos de medias.
- `verification/reproduce.py`, `verification/requirements.txt`: flujo aislado de reproducción Python.
- `verification/mean_ci.py`: cálculo reproducible de los intervalos descriptivos.
- `verification/results/`: salida estructurada y registros de ejecución de los scripts originales.

## Reproducción estadística

Solo la verificación Python necesita instalar dependencias; el sitio no las necesita. Con Python 3.13, desde la raíz:

```powershell
python -m venv .venv-verification
.\.venv-verification\Scripts\python.exe -m pip install -r verification/requirements.txt
.\.venv-verification\Scripts\python.exe verification/reproduce.py
.\.venv-verification\Scripts\python.exe verification/mean_ci.py
```

En macOS/Linux usa `.venv-verification/bin/python` en lugar de la ruta de Windows. El script copia `data/steels.csv` a un directorio temporal con el nombre esperado y ejecuta allí, sin editarlos, `2.6_Tratamiento_4.py` y `2.7_Tratamiento_4.py`. Guarda los registros y resultados bajo `verification/results/`, con versiones y SHA-256 de entrada. Verifica las diferencias y los resultados antes de copiar manualmente el JSON a `data/statistical-results.json`. El sitio comprueba el SHA-256 del CSV antes de mostrar inferencias: requiere un contexto seguro como HTTPS o `localhost` y `crypto.subtle`; si no está disponible, las omite.

Los ANOVA y post hoc se refieren exclusivamente a las dos poblaciones y agrupaciones originales, no a filtros arbitrarios. El selector de propiedad y población carga el resultado fijo correspondiente. Las estadísticas descriptivas y correlaciones sí se calculan a partir de los datos activos. Un valor post hoc que la biblioteca devuelve como cero se indica como inferior a la precisión numérica, no como probabilidad exactamente cero. Pearson parcial utiliza casos completos en las cinco propiedades, carbono y procesamiento.

Los intervalos añadidos son `media ± t(0,975; n − 1) × s / √n`, con desviación estándar muestral `s` y cuantiles de SciPy. Utilizan los registros no faltantes de cada grupo original y son cálculos descriptivos adicionales, no intervalos de comparación múltiple. Su interpretación requiere considerar independencia y normalidad aproximada de las medias; los grados repetidos y el diseño observacional limitan esas condiciones. El generador comprueba el SHA-256 y las medias y tamaños de los grupos verificados; la interfaz solo los muestra cuando coinciden con esos resultados.

Para las comprobaciones automatizadas, ejecuta `node verification/check-website.mjs`, `node verification/check-table-dom.mjs`, `node verification/check-ranking-dom.mjs` y `node verification/check-mean-ci.mjs` si dispones de Node.js. Node no es necesario para utilizar ni publicar el sitio.

## GitHub Pages

Sube los archivos del sitio y la carpeta `data/`. En **Settings → Pages**, selecciona la publicación desde la rama y carpeta raíz que contienen `index.html`. Las rutas son relativas y no se necesita compilación.

## Limitaciones

Los datos son observacionales; carbono es nominal y no se dispone de micrografías. Los grupos pueden diferir en composición y hay grados repetidos. Las correlaciones no demuestran causalidad. El informe original aporta referencias bibliográficas incompletas y discrepa de los catálogos consultados en la fecha y editorial de Shackelford; la edición exacta utilizada requiere confirmación. Las pruebas visuales y de teclado deben completarse en los navegadores y tamaños de pantalla de destino antes de publicar.
