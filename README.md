# Análisis y visualización de propiedades mecánicas de aceros al carbono

Sitio académico para explorar las relaciones entre composición química, procesamiento y propiedades mecánicas de aceros al carbono a partir del conjunto **Steel – Property and Composition (Carbon Steel)**.

## Tecnologías y estructura

HTML5, CSS3 y JavaScript con módulos ES. El sitio estático no requiere dependencias, instalación de Node.js ni compilación. Los archivos preexistentes del proyecto inicial con Vite se conservan, pero no son necesarios para ejecutar el sitio.

```text
index.html          Página principal
css/styles.css      Diseño y adaptación a pantallas
js/data.js          Carga, análisis CSV y acceso a datos
js/main.js          Inicialización, navegación y vista previa
data/steels.csv     Conjunto de datos de entrada
assets/             Recursos gráficos futuros
```

El archivo requerido es `data/steels.csv`. Se conservan los nombres originales de sus columnas y los valores faltantes; el sitio no modifica el archivo. Los indicadores se calculan al cargarlo. La vista previa muestra hasta diez registros.

## Ejecutar en WebStorm

Abre la carpeta del proyecto en WebStorm y abre `index.html` en el navegador mediante el servidor integrado (por ejemplo, con **Open in Browser**). Alternativamente, desde la raíz ejecuta `python -m http.server 8000` y visita `http://localhost:8000/`. Se requiere HTTP porque el navegador aplica restricciones de seguridad a `fetch()` cuando se abre la página directamente con `file://`.

## Publicar en GitHub Pages

Sube los archivos del sitio y `data/steels.csv` al repositorio. En GitHub, abre **Settings → Pages**, selecciona la publicación desde una rama y elige la rama y la carpeta raíz que contienen `index.html`. Guarda la configuración y espera a que GitHub publique el sitio. Las rutas relativas permiten servirlo desde la subruta del repositorio. No es necesario un paso de compilación.

## Estado y próximas fases

La fase 1 incluye estructura y diseño adaptable, navegación, carga del CSV, indicadores y vista previa. Los paneles de visualización son marcadores informativos; todavía no contienen análisis estadísticos ni resultados. En fases posteriores se podrán añadir gráficos interactivos, filtros, tablas con búsqueda y ordenación, resultados verificados de ANOVA y correlaciones, documentación de limpieza y referencias APA verificadas.
