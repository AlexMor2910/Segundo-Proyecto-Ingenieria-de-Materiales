# Proyecto 2 — Documento de continuidad para el punto 4

> **Estado:** documento de continuidad actualizado con la transcripción íntegra del Word `Resumen Proyecto 2 hacia punto 3.docx`, incorporado al final como Anexo A. **Pendiente:** recibir y cotejar el dataset original, el dataset limpiado y los scripts Python que el usuario vuelva a facilitar para la implementación web. El Word es la fuente textual principal para la explicación y las conclusiones; su contenido original se conserva sin correcciones silenciosas.

## 1. Objetivo del siguiente chat

**El punto 2 y el punto 3 están concluidos.** El siguiente paso es el **punto 4: desarrollar y presentar un producto final** para el proyecto *Análisis y visualización de propiedades mecánicas de aceros al carbono*, a partir del conjunto de datos *Steel – Property and Composition (Carbon Steel)*.

El producto será **una página web estática, responsiva e interactiva**, programada con **HTML, CSS y JavaScript vainilla (sin frameworks)** en **WebStorm**, con apoyo de **Codex**, y publicada mediante **GitHub Pages**. Evitar dependencias que requieran un servidor backend o secretos; pueden considerarse bibliotecas de gráficas frontend si son justificables, pero mantener la lógica propia en JS vainilla y preferir dependencias fáciles de alojar estáticamente.

**Identidad visual exigida:** blancos y azules; diseño limpio, legible, técnico y consistente. Garantizar contraste, soporte móvil, navegación por teclado y etiquetas accesibles.

## 2. Orden obligatorio de la página

1. **Portada / introducción:** nombre del proyecto, objetivo y navegación.
2. **Resultados del punto 2** con **gráficas interactivas y filtros**. Los **estadísticos pertinentes deben aparecer dentro o junto a cada gráfica**, y actualizarse con los filtros. Priorizar una historia clara en vez de saturar de gráficos.
3. **Explicación del proceso de exploración, limpieza y organización del dataset**, situada **después** de los resultados del punto 2 (no antes). Presentar decisiones, razonamiento y limitaciones; usar el Word y scripts para preservar precisión.
4. **Punto 3: respuesta interactiva** a la pregunta de correlaciones entre propiedades mecánicas de aceros SAE 1XXX; hacer la interacción especialmente rica y didáctica.
5. **Tablas complementarias dinámicas**, al final del contenido analítico (antes de referencias), con filtros, búsqueda, ordenamiento y posibilidad de descargar CSV si resulta conveniente.
6. **Referencias bibliográficas en formato APA**, al final de la página. **No es necesario incluir citas dentro del texto**; no inventar autores, ediciones, fechas ni DOI. El Word ya incluye tres referencias bibliográficas en formato no estandarizado; verificar sus datos antes de convertirlas al estilo APA.

Esta secuencia es un requisito explícito del usuario. El proceso de limpieza **no debe aparecer antes** de los resultados del punto 2.

## 3. Punto 2: trabajo previamente concluido y contenido a trasladar

De acuerdo con `Contexto_Proyecto2_Punto3.md` y los scripts aportados:

- Se analizó la relación entre porcentaje nominal de carbono y **UTS (MPa), YS (MPa), Hardness (HB) y Elongation (%)**, mediante Pearson y regresiones, separando series SAE y condiciones de procesamiento cuando resultó adecuado.
- Se compararon procesos **Hot rolled**, **Cold drawn** y **Cold drawn + Annealed** para la serie principal 1XXX; para otras series se compararon los tratamientos **Annealed**, **Normalized** y **Quenched and tempered**.
- Se realizaron pruebas ANOVA convencional o de Welch según características de los grupos, pruebas post hoc (Tukey/Games–Howell) y boxplots; la documentación de resultados detallados se encuentra en `Contexto_Proyecto2_Punto3.md`, y los scripts `2.1_Tratamiento.py` a `2.7_Tratamiento_4.py`.
- La web debe evitar insinuar causalidad solo por encontrar asociación estadística; respetar los tamaños muestrales, unidades y condiciones específicas.

### Comportamientos de filtros propuestos para el punto 2

- Selección de **serie SAE** (principal y, cuando sea útil, familia de dos dígitos), **propiedad mecánica**, **tipo de procesamiento**, y eventualmente **intervalo de carbono**.
- Mostrar **n**, coeficiente de Pearson **r** y su p-valor cuando se puedan calcular, ecuación de regresión/R² cuando proceda; indicar **“no definible”** si no hay variación suficiente.
- Para gráficos de comparación de grupos, mostrar **media/mediana/dispersión**, tamaño de muestra, prueba estadística apropiada y resultados post hoc solo si corresponden exactamente al subconjunto examinado.
- **Crítico:** no reutilizar p-valores ANOVA o post hoc obtenidos para el conjunto completo al aplicar filtros que cambian los datos. Recalcular estadísticas compatibles o mostrar claramente que son cifras del análisis original, no del filtro activo. Implementar con cuidado las pruebas estadísticas en JS o precalcular un catálogo verificado de combinaciones con su alcance explícito; no improvisar p-valores.
- Tooltip con grado SAE, valor, unidad y condición; leyenda que permita ocultar/mostrar grupos; botón para restablecer filtros.

## 4. Explicación del dataset y limpieza (sección posterior al punto 2)

Según la documentación de continuidad, el archivo final `Cleansed_Treatment_Carbon_Steel_Summary_Fixed.csv` contiene **190 registros y 13 columnas**. La limpieza previa:

- Normalizó grados SAE y formatos numéricos (reducción de área, dureza Brinell, unidades MPa).
- Calculó **Mn Avg (%)** como promedio de límites mínimo y máximo; conservó **P (Max)** y **S(Max)**, eliminando límites mínimos poco completos.
- Definió **C (%)** a partir de los dos últimos dígitos del grado SAE (aproximación nominal), y descartó variables redundantes o insuficientemente documentadas.
- Identificó tratamientos térmicos, temperatura en K y condiciones mecánicas desde texto libre, normalizando descripciones y errores tipográficos.
- Corrigió anomalías de escala en P/S mediante la regla de limpieza documentada y registros con YS mayor que UTS intercambiados.
- Conservó los 190 registros originales.

**El Word fue incorporado íntegramente en el Anexo A. Verificar las implementaciones y resultados contra el dataset y los scripts antes de publicar.** Explicar las limitaciones derivadas de utilizar composiciones nominales, máximos reportados, agrupación de tratamientos y ausencia de datos metalográficos. No presentar valores inferidos como mediciones experimentales.

## 5. Punto 3: pregunta y resultados concluidos

**Pregunta definitiva del punto 3:**

> Entre las propiedades mecánicas, para la serie SAE 1XXX, ¿cuáles se correlacionan más entre sí? ¿Y por qué?

Se analizaron **138 observaciones** correspondientes a **65 grados SAE distintos**, distribuidas en:

| Procesamiento | n |
|---|---:|
| Hot rolled | 65 |
| Cold drawn | 52 |
| Cold drawn + Annealed | 21 |

**Dos registros SAE 1340** con condiciones térmicas Normalized y Annealed quedaron fuera de los tres grupos de procesamiento definidos. Dejar esta regla transparente.

### Hallazgos clave del punto 3

| Pareja | Spearman ρ general |
|---|---:|
| UTS — Hardness | +0.9914 |
| YS — Elongation | -0.9136 |
| Hardness — Elongation | -0.8514 |
| UTS — Elongation | -0.8491 |
| UTS — YS | +0.7742 |
| Hardness — Reduction | -0.7628 |
| YS — Hardness | +0.7589 |
| UTS — Reduction | -0.7522 |
| Elongation — Reduction | +0.6617 |
| YS — Reduction | -0.6103 |

- **UTS–Hardness:** Pearson **0.9946**, Spearman **0.9914**; correlación parcial de Pearson, controlando carbono y procesamiento: **0.9751**.
- **YS–Elongation:** Pearson **−0.8904**, Spearman **−0.9136**; correlación parcial: **−0.5353**.
- **UTS–YS:** Spearman **0.7742**, correlación parcial: **0.9100**.
- **Hot rolled:** YS–Hardness Spearman **0.9986**; UTS–YS **0.9964**.
- **Cold drawn:** UTS–YS Spearman **0.9967**.
- **Cold drawn + Annealed:** UTS–Hardness Spearman **0.7945**, mientras YS–Hardness es aproximadamente **0.3691** y no fue significativa tras la corrección BH.

Interpretación metalúrgica documentada: UTS, YS y dureza comparten mecanismos de resistencia a la deformación plástica; en aceros al carbono la proporción ferrita/perlita, la presencia de cementita, el refinamiento de microestructura y el endurecimiento por deformación pueden contribuir. El aumento de resistencia frecuentemente se relaciona con pérdida de elongación/ductilidad; el estirado en frío eleva densidad de dislocaciones y dificulta su movimiento. El recocido puede provocar recuperación/recristalización según condiciones, aunque **no está demostrado directamente** en los registros. Elongación y reducción de área caracterizan aspectos distintos de ductilidad.

**Advertencias científicas:** estas son asociaciones observacionales, no pruebas de causalidad; el contenido de carbono y el procesamiento explican parte de las asociaciones; hay grados repetidos y no independencia perfecta de observaciones; faltan micrografías; revisar si alguna propiedad fue estimada en vez de medida, ya que algunas correlaciones son excepcionalmente altas.

### Interactividad prioritaria del punto 3

- **Matriz de correlaciones dinámica**, con alternancia Pearson / Spearman, selección de procesamiento (todos, Hot rolled, Cold drawn, Cold drawn + Annealed) y visualización del coeficiente dentro de cada celda. Las celdas deben abrir una comparación detallada del par.
- **Explorador de pares de propiedades:** seleccionar eje X, eje Y y procesamiento, visualizar puntos con tooltip (grado SAE, valores y unidades), coeficientes r/ρ, n y, cuando corresponda, p/q **calculados para los datos activos**; resaltar correlaciones positivas y negativas.
- **Ranking dinámico** de pares por fuerza absoluta de correlación, con posibilidad de ver solo asociaciones positivas/negativas y elegir grupo.
- **Comparación entre procesamientos** para un par elegido, con coeficientes y n por grupo y explicación que cambia según la selección.
- **Modo explicativo de metalurgia:** tarjetas breves y diagramas accesibles que expliquen dislocaciones, resistencia/dureza, ductilidad y cómo cambia el procesamiento; separar el dato observado del mecanismo hipotético. Nunca afirmar que los datos contienen evidencias metalográficas.
- **Correlación parcial**: vista comparativa «sin controlar» vs «controlando C y procesamiento». No cambiar interpretaciones de p-valor sin verificar supuestos. Estas correlaciones parciales fueron calculadas por residualización lineal, no son Spearman parcial.
- Mostrar avisos cuando no se puede calcular una correlación (n insuficiente o variable constante) y evitar gráficos engañosos.

## 6. Tablas complementarias dinámicas

Ubicar **al final de la página, antes de referencias**. Proponer pestañas para: registros de aceros filtrables; estadísticas descriptivas por grupo; correlaciones generales/por procesamiento; resultados ANOVA/post hoc del punto 2 (identificando alcance); y coeficientes parciales del punto 3. Incluir encabezados con unidades, búsqueda, orden ascendente/descendente, paginación, filtros sincronizados con gráficas cuando aplique, exportación CSV y estados de carga/vacíos.

## 7. Arquitectura técnica de la página (propuesta)

```text
proyecto-aceros/
├── index.html
├── css/
│   └── styles.css
├── js/
│   ├── main.js
│   ├── data.js
│   ├── filters.js
│   ├── charts-point2.js
│   ├── charts-point3.js
│   ├── stats.js
│   └── tables.js
├── data/
│   ├── steels.csv
│   └── statistical-results.json       # solo resultados verificados / alcance explícito
├── assets/
├── README.md
└── .gitignore
```

- Utilizar módulos JS ES (`type="module"`) y `fetch` con rutas **relativas** compatibles con una página de proyecto en GitHub Pages (`./data/steels.csv`), sin depender de rutas absolutas `/data/...`.
- Para gráficos, elegir con cuidado entre SVG/Canvas implementados en JS y una biblioteca JS client-side ligera; el requisito es **JavaScript vainilla**, no necesariamente ausencia de toda biblioteca de visualización. Acordar esta distinción antes de iniciar código de producción.
- Cargar CSV/JSON localmente desde el repositorio. Verificar que todas las transformaciones estadísticas reproduzcan los análisis en Python y que cada filtro actualice los valores que muestra.
- Evitar publicar ficheros innecesarios, credenciales o rutas locales de Windows. La aplicación funcionará sin backend, builds obligatorios ni servicios de pago.
- Preparar README que describa instalación, ejecución local mediante servidor estático (por ejemplo el preview/servidor de WebStorm), pruebas, y publicación GitHub Pages desde rama `main`/directorio raíz o GitHub Actions según configuración.
- Diseñar interfaz **blanco/azul**, jerarquía tipográfica clara, tablas accesibles, contraste adecuado, gráficos con paleta apta para distinguir series (no depender únicamente del color).

## 8. Secuencia de trabajo solicitada para el siguiente chat

1. **Usar el Word ya incorporado en el Anexo A:** respetar la redacción original de explicaciones y conclusiones, adaptándola a secciones web solo cuando el usuario lo indique. Revisar las referencias del documento antes de normalizarlas a APA; algunos datos bibliográficos son incompletos.
2. Confirmar inventario de datos/resultados utilizables; si no existe algún CSV de resultados del punto 2, regenerarlo desde los scripts originales o reconstruirlo cuidadosamente.
3. Diseñar un esquema de datos (CSV/JSON) y un mapa de secciones, filtros y estadísticas por visualización. Definir qué cálculos pueden actualizarse en navegador y cuáles deben ser precomputados con alcance fijo.
4. Desarrollar la web progresivamente para uso con WebStorm/Codex, iniciando por estructura, estilos y lectura de datos, luego punto 2, limpieza, punto 3 y tablas.
5. Verificar resultados, interactividad, accesibilidad, móvil, tiempos de carga y funcionamiento con rutas de GitHub Pages.
6. Preparar instrucciones concretas para subir el repositorio y activar GitHub Pages; la publicación requiere acción/credenciales del usuario y no debe afirmarse que ocurrió sin verificación.

## 9. Archivos existentes y continuidad

- `Contexto_Proyecto2_Punto3.md`: instrucciones originales del proyecto, redacción y resultados del punto 2.
- `Cleansed_Treatment_Carbon_Steel_Summary_Fixed.csv`: base depurada de 190 × 13.
- Scripts de limpieza/exploración `1_Exploración.py`, `1.1_Exploración.py`, `1.2_Exploración.py`, `1.3_Exploración.py`, y `2.1_Tratamiento.py` a `2.7_Tratamiento_4.py`.
- `Correlacion_Propiedades_Mecanicas_1XXX.py`: análisis del punto 3.
- `Correlaciones_Propiedades_Mecanicas_1XXX_Resultados.zip`: tablas y gráficos del punto 3.
- `Graficas_Correlaciones_Propiedades_1XXX.py` y `Graficas_Correlaciones_Propiedades_1XXX.zip`: scripts y visualizaciones del punto 3.
- **Documento Word recibido e incorporado íntegramente:** `Resumen Proyecto 2 hacia punto 3.docx` (transcripción en Anexo A).
- **Dataset original: pendiente de recibir para documentar y contrastar la limpieza.**
- **Todos los scripts Python que el usuario adjunte: usar como referencia de implementación de cada transformación y cálculo en JavaScript, con pruebas de equivalencia Python–JS.**

## 10. Instrucciones importantes para el asistente del próximo chat

- El usuario **da por terminados los puntos 2 y 3**; no reiniciar su análisis estadístico sin una razón o petición explícita. El trabajo nuevo es producir la web del punto 4.
- Priorizar exactitud estadística y metalúrgica sobre la cantidad de interacciones. Nunca mostrar p-valores/ANOVA que no correspondan a la selección visible.
- Mantener siempre el orden **punto 2 → limpieza del dataset → punto 3 → tablas complementarias → referencias APA**.
- Respetar requisitos técnicos: **WebStorm, Codex, JS vainilla, GitHub Pages, blanco/azul**.
- **Usar el Word del usuario ya incorporado en Anexo A como referencia textual principal.** Este archivo es continuidad operativa para iniciar el punto 4; integrar cualquier archivo nuevo sin perder lo ya documentado.
- El Word contiene tres referencias (Askeland, Callister y Shackelford) con datos bibliográficos parciales; conservarlas como fuentes suministradas y **verificar metadatos antes de mostrar referencias APA normalizadas**. No inventar editoriales, años, edición o DOI.

## 11. Reglas de entrega y uso de Codex en WebStorm

- Construir el proyecto en etapas pequeñas y verificables, entregando archivos completos y prompts de trabajo precisos para Codex cuando se soliciten. Mantener nombres de campos y convenciones del dataset, salvo que exista un mapeo explícito.
- Antes de traducir una fórmula de Python a JavaScript, identificar el script fuente, definición matemática, tratamiento de `NaN`, grados de libertad, redondeo, y el conjunto de registros utilizado. Documentar diferencias entre las bibliotecas Python y las rutinas JS.
- El sitio debe funcionar directamente como página estática en GitHub Pages. Cualquier estadístico que no sea factible de recalcular correctamente en el navegador deberá cargarse de resultados precalculados y etiquetarse como resultado del conjunto fijo, no del filtro interactivo.
- En el próximo chat, usar el Word transcrito en el Anexo A y cotejar las estadísticas y transformaciones con los CSV y scripts que se adjunten. No tratar la transcripción como sustituto de los datos para cálculos.


---

# Anexo A — Transcripción íntegra del documento Word recibido

**Documento de origen:** `Resumen Proyecto 2 hacia punto 3.docx` (18 páginas). Se conserva el texto de sus párrafos en orden, incluidos sus saltos de línea y las referencias tal como aparecen. La transcripción no corrige errores bibliográficos ni modifica conclusiones.

Instrucciones:

PROYECTO 2. Análisis y visualización de propiedades mecánicas de aceros al carbono
Steel – Property and Composition (Carbon Steel)
En este proyecto trabajarán con una base de datos que relaciona la composición química, las condiciones de procesamiento y las propiedades mecánicas de diferentes aceros al carbono.

El objetivo será investigar cómo estas variables se relacionan con el comportamiento mecánico de los materiales, pero esta vez tendrán un reto adicional:
Ya tienen una serie de preguntas de investigación que deberán responder. Sin embargo, tendrán libertad para decidir cómo desarrollar su análisis, qué herramientas utilizar y, especialmente, cómo presentar la información.
No quiero que piensen que el resultado necesariamente tiene que ser un documento con muchas gráficas. Pueden desarrollar una página web, una aplicación, un dashboard interactivo, un visualizador de propiedades o cualquier otra propuesta que les permita explorar y explicar los resultados.´

También pueden realizar una presentación convencional si consideran que es la mejor manera de comunicar sus hallazgos.
¿Qué tienen que hacer?
1. Comprender y preparar los datos
Antes de comenzar, deberán explorar la base de datos, identificar las variables disponibles y comprender qué representan físicamente.
Tendrán que organizar los registros, clasificar las condiciones de procesamiento, revisar la calidad de los datos y realizar las transformaciones necesarias para analizarlos.
Recuerden que no basta con pedirle a la inteligencia artificial que limpie los datos: deben entender qué está haciendo, por qué lo está haciendo y cómo sus decisiones pueden afectar los resultados.
2. Responder las preguntas de investigación

Analicen la relación entre el %C y propiedades como UTS, YS, dureza y elongación.

Comparen las condiciones de procesamiento, identifiquen diferencias y expliquen los resultados a partir de los conceptos de microestructura y propiedades que revisamos en clase.

Exploren los registros correspondientes a recocido y normalizado, identifiquen tendencias y consideren las limitaciones de los datos.

Utilicen el análisis estadístico propuesto (ANOVA), cuando los datos y sus características lo permitan, e interpreten los resultados y sus limitaciones.

Deben justificar sus decisiones, interpretar los resultados desde el punto de vista de la ingeniería de materiales y reconocer cuándo los datos no permiten establecer una conclusión clara.
3. Proponer algo propio
Además de responder las preguntas anteriores, cada equipo deberá proponer que considere interesante.
Puede tratarse de una nueva pregunta de investigación, una forma diferente de comparar los aceros, una herramienta para explorar sus propiedades o alguna funcionalidad que haga más útil su proyecto.
No tiene que ser algo complejo. Lo importante es que puedan explicar


4. Desarrollar y presentar su producto final
Esta es la parte en la que quiero que experimenten un poco más.
Pueden utilizar Python, R, HTML, herramientas de visualización, inteligencia artificial u otras tecnologías que les permitan desarrollar su propuesta.
Me gustaría que aprovecharan esta libertad para ir más allá de las gráficas tradicionales: pueden incorporar filtros interactivos, comparaciones entre materiales, visualizaciones dinámicas, explicaciones integradas o cualquier recurso que facilite comprender los resultados.

Piensen que están desarrollando algo que podría ser utilizado por otros estudiantes, ingenieros o personas interesadas en los materiales.

No olviden que . Las gráficas deben ser correctas, representar adecuadamente los datos y ayudar a interpretar los resultados.

Pero recuerden que . Deben comprender lo que presentan y ser capaces de explicarlo.
Este proyecto también es una oportunidad para explorar habilidades que quizá no sabían que tenían: programación, diseño, visualización, investigación, comunicación o desarrollo de herramientas digitales.

Explicación y conclusiones hasta el momento:

Antes de realizar el análisis estadístico, se llevó a cabo una etapa de exploración, depuración y reorganización de la base de datos con el objetivo de obtener variables consistentes y comparables desde el punto de vista físico.

En primer lugar, se realizó una exploración general del conjunto de datos. Se identificaron el número de registros y variables, los tipos de datos de cada columna, sus rangos de valores y la cantidad de datos faltantes. Esta revisión permitió detectar tanto variables redundantes como columnas con una cobertura insuficiente para el análisis posterior. El procedimiento también sirvió para identificar variables almacenadas en formatos inconsistentes, errores aparentes de captura y diferencias en la forma de describir las condiciones de procesamiento.

Para simplificar la información composicional, se revisaron inicialmente las concentraciones mínima y máxima de carbono. Debido a que el contenido nominal de carbono puede obtenerse aproximadamente de los dos últimos dígitos de la clasificación SAE, divididos entre 100, se comparó este valor con el promedio de los límites mínimo y máximo disponibles. Las diferencias encontradas fueron pequeñas, por lo que se decidió utilizar como variable de carbono el valor derivado de la clasificación SAE. Esta decisión también permitió disponer de un valor de carbono para registros en los que faltaba el límite mínimo de composición. En consecuencia, las columnas originales de carbono mínimo y máximo fueron eliminadas. Para el manganeso se siguió un criterio distinto: se calculó el promedio entre sus concentraciones mínima y máxima y se conservó este valor como una variable representativa de composición. Estas transformaciones están implementadas explícitamente en el primer script de limpieza.

También se normalizó el formato de algunas propiedades mecánicas. La reducción de área contenía valores con coma decimal, por lo que éstos se transformaron a formato numérico empleando punto decimal. En la columna de dureza se extrajo el valor numérico correspondiente a la dureza Brinell, eliminando caracteres asociados con formatos inconsistentes. De igual manera, se descartaron las columnas de esfuerzo último y esfuerzo de cedencia expresadas en ksi, ya que la base contenía las mismas propiedades en MPa y mantener ambas unidades habría introducido información redundante.

Las variables correspondientes a concentraciones mínimas y máximas de silicio, níquel, cromo, molibdeno y titanio, así como los valores mínimos de fósforo y azufre, presentaban una cantidad considerable de datos faltantes o resultaban insuficientes para desarrollar comparaciones estadísticas consistentes. Por esta razón se eliminaron de la base empleada para el análisis. Se conservaron, en cambio, los valores máximos de fósforo y azufre, cuya cobertura era adecuada. La presencia de plomo en únicamente dos grados fue considerada demasiado poco representativa para incluirla como una variable independiente dentro del análisis estadístico general.

Posteriormente se reorganizaron las condiciones de procesamiento, que originalmente se encontraban almacenadas como descripciones de texto libre. Se corrigieron algunos errores tipográficos recurrentes y se identificaron de forma programática el tratamiento térmico, la temperatura de tratamiento y las condiciones de procesamiento mecánico. Los tratamientos se clasificaron en tres categorías principales: recocido, normalizado y temple seguido de revenido. Las temperaturas especificadas originalmente en grados Celsius fueron convertidas a Kelvin. Por separado, se identificaron las condiciones de laminado en caliente y estirado en frío.

Durante esta reorganización se observó que algunas categorías más específicas aportaban muy pocos registros para permitir una comparación estadística independiente. Por ejemplo, el recocido esferoidizado fue agrupado dentro de la categoría general de recocido. Asimismo, las descripciones de temple y revenido se condensaron en una sola categoría denominada “Quenched and tempered”. La finalidad de esta simplificación fue evitar grupos excesivamente pequeños y obtener categorías de procesamiento suficientemente homogéneas para las comparaciones posteriores.

Finalmente, se efectuó una última revisión de consistencia física. Se detectaron valores de fósforo y azufre que eran varios órdenes de magnitud mayores que los demás registros, lo que indicaba un problema de escala; los valores superiores a 5 fueron divididos entre 1000 para llevarlos al mismo orden de magnitud que el resto de las concentraciones. También se buscaron registros en los que el esfuerzo de cedencia fuera mayor que el esfuerzo último. En los casos encontrados, ambos valores se encontraban intercambiados, por lo que se corrigió su posición. Estas dos operaciones constituyeron la última etapa de modificación de los datos.

Después de estas transformaciones, la base final contiene 190 registros y 13 variables: grado SAE, esfuerzo último, esfuerzo de cedencia, elongación, reducción de área, dureza Brinell, contenido máximo de fósforo y azufre, contenido promedio de manganeso, contenido nominal de carbono, tratamiento térmico, temperatura del tratamiento térmico y condición de procesamiento mecánico. No se eliminaron registros durante la limpieza, por lo que se conservó la totalidad de las observaciones originales.

De manera preliminar, se abordó la primera pregunta de investigación, correspondiente a la relación entre el porcentaje de carbono y cuatro propiedades mecánicas de los aceros: esfuerzo de cedencia (YS), esfuerzo último a la tracción (UTS), dureza Brinell y porcentaje de elongación. Para ello, se calcularon los coeficientes de correlación de Pearson y se elaboraron los diagramas de dispersión correspondientes, acompañados de sus respectivas líneas de regresión lineal.

Sin embargo, durante el análisis inicial se observó que, para determinadas concentraciones de carbono, existían múltiples registros con valores iguales o muy similares en las propiedades mecánicas. Se consideró que este comportamiento podría estar relacionado con la inclusión de aceros sometidos a diferentes condiciones de procesamiento térmico y mecánico, las cuales pueden modificar considerablemente sus propiedades aun cuando presenten una composición química nominal similar. Esta variabilidad dificultaba identificar una tendencia general y podía reducir los coeficientes de correlación obtenidos al considerar la totalidad de las observaciones.

Con el propósito de reducir esta variabilidad sin generar subdivisiones excesivamente pequeñas, se decidió realizar una primera clasificación de los registros de acuerdo con su serie SAE. Esta separación permitió distinguir familias de aceros con características de composición y aleación diferentes. Como resultado, los coeficientes de correlación aumentaron considerablemente en varias de las series, lo que sugirió que parte de la dispersión observada en el análisis global estaba relacionada con las diferencias entre familias de materiales.

Durante esta etapa se identificó que las series 13XX, 31XX, 44XX, 46XX, 48XX, 61XX, 87XX, 92XX y 93XX presentaban un único valor de carbono nominal en los registros disponibles. Esto se debe a que las observaciones de dichas series corresponden a variaciones en las condiciones de procesamiento de materiales con una misma composición nominal. En consecuencia, al no existir variabilidad en la concentración de carbono, no fue posible calcular coeficientes de correlación de Pearson entre esta variable y las propiedades mecánicas. Por esta razón, dichas series no permiten estudiar estadísticamente la relación entre ambas variables mediante este procedimiento.

Posteriormente, se elaboraron gráficas independientes para cada serie SAE, agrupando las cuatro propiedades mecánicas en una misma figura. Aunque esta representación facilitó la identificación de tendencias, se observó que algunos conjuntos de datos presentaban dos o más agrupaciones diferenciadas. Estas agrupaciones parecían corresponder a distintas condiciones de procesamiento térmico y mecánico, lo que reforzó la hipótesis de que dichos factores contribuían a la dispersión de los resultados.

Por lo anterior, se realizó una última subdivisión de los registros, considerando tanto la serie SAE como las condiciones de procesamiento identificadas. Para evitar interpretaciones basadas en grupos con muy pocas observaciones, se estableció como criterio exploratorio considerar únicamente aquellos subconjuntos con más de cinco registros.

Después de esta clasificación, se obtuvieron coeficientes de correlación de Pearson superiores a 0.85 en la mayoría de las combinaciones analizadas. En términos generales, se identificó una asociación positiva entre el contenido de carbono y el esfuerzo último, el esfuerzo de cedencia y la dureza, mientras que la elongación presentó una asociación negativa. Por lo tanto, dentro de las familias y condiciones de procesamiento examinadas, los aceros con mayor contenido nominal de carbono tendieron a presentar mayor resistencia mecánica y dureza, pero menor capacidad de deformación antes de la fractura.

Este comportamiento puede explicarse mediante la influencia del carbono sobre la microestructura del acero. En condiciones de equilibrio o enfriamiento suficientemente lento, un incremento en el contenido de carbono de los aceros hipoeutectoides favorece una mayor proporción de perlita en relación con la ferrita. La perlita está constituida por láminas alternadas de ferrita y cementita, siendo esta última una fase considerablemente más dura y resistente a la deformación plástica. Por consiguiente, el incremento de su proporción suele elevar la resistencia mecánica y la dureza del material, aunque también reduce su ductilidad.

Los resultados muestran tendencias interesantes en las propiedades mecánicas dependiendo de las condiciones de procesamiento. Para las series 1XXX, se observó que el estirado en frío (Cold drawn) incrementó el esfuerzo último a la tracción, el esfuerzo de cedencia y la dureza en comparación con el rolado en caliente (Hot rolled), pero produjo una disminución en el porcentaje de elongación. Por su parte, los registros correspondientes a aceros estirados en frío y posteriormente identificados como recocidos (Annealed + Cold drawn) presentaron, en términos generales, un comportamiento intermedio entre ambas condiciones.

Para las demás series, al comparar los tratamientos térmicos, se observó que los aceros templados y revenidos (Quenched and tempered) presentaron los mayores valores de esfuerzo último, esfuerzo de cedencia y dureza, seguidos por los aceros normalizados (Normalized) y recocidos (Annealed). En cuanto al porcentaje de elongación, se identificó la tendencia contraria: los aceros recocidos presentaron los valores más elevados, seguidos por los normalizados, mientras que los templados y revenidos mostraron los menores valores.

Estas diferencias pueden explicarse a partir de los cambios microestructurales producidos por cada condición de procesamiento. En primer lugar, el estirado en frío provoca un mecanismo conocido como endurecimiento por deformación, mediante el cual aumenta la densidad de dislocaciones en el material. La interacción y acumulación de estas dislocaciones dificultan el movimiento de otras durante la deformación plástica, incrementando el esfuerzo necesario para continuar deformando el acero. Como consecuencia, aumentan el esfuerzo de cedencia, el esfuerzo último y la dureza, mientras que disminuye su capacidad de deformación plástica, reflejada en una menor elongación. En contraste, el rolado en caliente se realiza a temperaturas suficientemente elevadas para favorecer la recuperación y la recristalización, reduciendo los efectos del endurecimiento por deformación. Por esta razón, generalmente se obtienen menores valores de resistencia y dureza, pero una mayor capacidad de deformación.

En cuanto a los tratamientos térmicos, las diferencias se relacionan principalmente con las transformaciones de fase y la microestructura resultante. Durante el recocido, el calentamiento y el enfriamiento lento favorecen la formación de una microestructura relativamente blanda y dúctil, generalmente constituida por ferrita y perlita en los aceros al carbono hipoeutectoides. La recuperación de la estructura y la reducción de las tensiones internas contribuyen a disminuir la resistencia mecánica y la dureza, pero favorecen la ductilidad. Por otra parte, la normalización utiliza un enfriamiento al aire, generalmente más rápido que el del recocido, lo que puede producir una microestructura más fina, con menor tamaño de grano y una distribución más fina de los constituyentes perlíticos. Esto suele incrementar la resistencia y la dureza respecto al material recocido, aunque puede reducir ligeramente su elongación.

Finalmente, en los aceros templados y revenidos, el enfriamiento rápido posterior a la austenización favorece la formación de martensita, una microestructura caracterizada por su elevada dureza y resistencia, pero también por su fragilidad y limitada ductilidad cuando se encuentra sin revenir. El revenido posterior permite reducir parte de las tensiones internas y la fragilidad generadas durante el temple, mejorando la tenacidad y la ductilidad, aunque generalmente disminuye parcialmente la dureza y la resistencia. A pesar de ello, los valores de estas propiedades suelen permanecer por encima de los correspondientes a los aceros recocidos y normalizados, dependiendo de la temperatura y duración del revenido.

Consideraciones y limitaciones del análisis

Es importante señalar que estas tendencias representan el comportamiento observado en los registros disponibles y no necesariamente se cumplen para todos los grados SAE. Las diferencias de composición química, contenido de carbono, elementos de aleación y condiciones específicas de procesamiento también influyen en las propiedades mecánicas. Asimismo, el número de observaciones disponible para algunas combinaciones de serie y tratamiento es reducido, lo que limita la posibilidad de establecer comparaciones estadísticas concluyentes.

Adicionalmente, no se cuenta con observaciones metalográficas que permitan confirmar directamente las microestructuras descritas. Por lo tanto, las explicaciones anteriores corresponden a los mecanismos metalúrgicos esperados para cada proceso y no a fases o estructuras identificadas experimentalmente en los registros analizados.

### Análisis de varianza de las condiciones de procesamiento

Con el propósito de determinar si las diferencias observadas entre las condiciones de procesamiento corresponden a variaciones estadísticamente significativas en las propiedades mecánicas, se realizaron análisis de varianza (ANOVA). Se establecieron dos conjuntos de análisis: el primero correspondiente a los aceros de la serie SAE 1XXX, clasificados según sus condiciones de procesamiento mecánico (Hot rolled, Cold drawn y Cold drawn + Annealed); y el segundo correspondiente al resto de las series, clasificadas según su tratamiento térmico (Annealed, Normalized y Quenched and tempered).

Para cada conjunto se realizaron cuatro pruebas independientes, utilizando como variables dependientes la resistencia última a la tracción (UTS), el esfuerzo de cedencia (YS), la dureza Brinell y el porcentaje de elongación.

En el caso de los aceros 1XXX, se identificaron diferencias estadísticamente significativas entre las condiciones de procesamiento para las cuatro propiedades mecánicas. Debido a que las pruebas de Levene indicaron desigualdad de varianzas en todos los casos, se utilizaron los resultados del ANOVA de Welch. Se obtuvieron valores de significancia inferiores a 0.05 para UTS (F = 32.69; p = 2.43 × 10⁻¹¹), YS (F = 183.86; p = 7.60 × 10⁻³²), dureza (F = 30.77; p = 8.94 × 10⁻¹¹) y elongación (F = 79.90; p = 4.26 × 10⁻²⁰).

En cuanto a los valores promedio, el grupo Cold drawn + Annealed presentó los mayores valores de UTS, YS y dureza, mientras que Hot rolled presentó el mayor porcentaje de elongación. El tamaño de efecto, calculado mediante eta cuadrada, mostró que las diferencias entre grupos fueron particularmente importantes para YS (η² = 0.560) y elongación (η² = 0.333), mientras que para UTS (η² = 0.095) y dureza (η² = 0.082) fueron menores. Estos resultados indican que las condiciones de procesamiento están asociadas con diferencias en las propiedades mecánicas, aunque todavía se requieren comparaciones post hoc para identificar qué pares de grupos presentan diferencias significativas.

Para el segundo conjunto, correspondiente a las series SAE distintas de 1XXX, también se encontraron diferencias estadísticamente significativas entre los tratamientos térmicos en las cuatro propiedades. Para UTS, dureza y elongación se utilizó ANOVA convencional, mientras que para YS se utilizó ANOVA de Welch debido a la falta de homogeneidad de varianzas. Los resultados fueron significativos para UTS (F = 35.77; p = 3.62 × 10⁻¹⁰), YS (F = 115.58; p = 1.98 × 10⁻¹³), dureza (F = 39.65; p = 8.17 × 10⁻¹¹) y elongación (F = 13.23; p = 2.77 × 10⁻⁵).

Los valores promedio mostraron una tendencia progresiva en la que los aceros templados y revenidos presentaron los mayores valores de resistencia última, esfuerzo de cedencia y dureza, seguidos por los normalizados y los recocidos. Para la elongación se observó el comportamiento contrario, siendo mayor en los aceros recocidos, seguida de los normalizados y finalmente los templados y revenidos.

Las comparaciones post hoc mediante Tukey confirmaron diferencias significativas entre los tres tratamientos para UTS, dureza y elongación. En el caso del esfuerzo de cedencia, debido a que se utilizó ANOVA de Welch, se requiere una prueba post hoc compatible con varianzas desiguales para determinar qué tratamientos presentan diferencias entre sí.

Los tamaños de efecto obtenidos para este segundo conjunto fueron considerablemente elevados: 0.604 para UTS, 0.798 para YS, 0.628 para dureza y 0.360 para elongación. Esto indica que las diferencias entre los grupos de tratamiento representan una proporción importante de la variabilidad observada en las propiedades mecánicas.

En términos metalúrgicos, estas tendencias son consistentes con los cambios microestructurales esperados para cada proceso. El recocido favorece una microestructura relativamente blanda y dúctil, mientras que la normalización suele producir una estructura más fina que incrementa la resistencia y la dureza. Por su parte, el temple seguido de revenido permite obtener una microestructura de mayor resistencia mecánica, generalmente acompañada de una menor elongación. De manera similar, el estirado en frío produce endurecimiento por deformación, aumentando la resistencia y reduciendo la ductilidad.

Finalmente, deben considerarse las limitaciones de los datos. En particular, el segundo conjunto reúne diferentes familias SAE, cuyas composiciones y elementos de aleación pueden influir en las propiedades mecánicas independientemente del tratamiento térmico. Asimismo, algunas pruebas presentaron desviaciones de los supuestos estadísticos y no se dispone de observaciones metalográficas para verificar directamente las microestructuras descritas. Por consiguiente, los resultados permiten identificar diferencias estadísticas entre los grupos estudiados, pero no establecer por sí solos relaciones causales entre los tratamientos y las propiedades mecánicas.

### Comparaciones post hoc y análisis de las distribuciones

Debido a que el análisis de varianza permite identificar diferencias entre las medias de los grupos, pero no determina específicamente cuáles presentan diferencias entre sí, se realizaron comparaciones post hoc mediante las pruebas de Games-Howell y Tukey, según las características de los datos.

Para los aceros de la serie 1XXX se utilizó la prueba de Games-Howell, debido a la falta de homogeneidad de varianzas identificada mediante la prueba de Levene. En el caso de UTS, se encontraron diferencias significativas entre Cold drawn + Annealed y los otros dos grupos, mientras que no se identificaron diferencias significativas entre Hot rolled y Cold drawn. Se observó el mismo comportamiento para la dureza Brinell. Por otra parte, para el esfuerzo de cedencia y la elongación se encontraron diferencias estadísticamente significativas entre las tres condiciones de procesamiento.

En particular, Cold drawn + Annealed presentó los mayores valores promedio de UTS, YS y dureza, mientras que Hot rolled presentó la mayor elongación. Estos resultados indican que las diferencias entre las condiciones de procesamiento no afectan de manera uniforme todas las propiedades mecánicas.

Para las demás series SAE, las comparaciones mediante Games-Howell para el esfuerzo de cedencia mostraron diferencias significativas entre los tres tratamientos térmicos. El grupo Quenched and tempered presentó el mayor valor promedio, seguido por Normalized y Annealed. Las comparaciones previamente realizadas mediante Tukey para UTS, dureza y elongación también identificaron diferencias significativas entre todos los pares de tratamientos.

Adicionalmente, se analizaron las distribuciones mediante diagramas de caja y bigotes, complementados con los valores individuales y los estadísticos descriptivos de cada grupo. En los aceros 1XXX se observó una considerable superposición entre las distribuciones de Hot rolled y Cold drawn para UTS y dureza, lo cual coincide con la ausencia de diferencias significativas identificada mediante Games-Howell. En cambio, para YS y elongación se observó una separación más marcada entre las condiciones de procesamiento.

En las demás series, los diagramas mostraron una tendencia más definida: los valores de UTS, YS y dureza aumentaron progresivamente desde los aceros recocidos hasta los templados y revenidos, mientras que la elongación presentó una tendencia inversa. Asimismo, se identificaron diferencias en la dispersión de los datos, particularmente en los grupos normalizados, que presentaron mayor variabilidad en algunas propiedades.

En conjunto, las comparaciones post hoc y el análisis de las distribuciones respaldan las diferencias identificadas mediante ANOVA. Los resultados son consistentes con los mecanismos de endurecimiento por deformación y las transformaciones microestructurales asociadas a los tratamientos térmicos. No obstante, las diferencias de composición química entre los grados SAE y las limitaciones de los registros disponibles deben considerarse al interpretar los resultados.

Pregunta: Entre las propiedades mecánicas, para la serie 1XXX, ¿cuáles se correlacionan más entre sí? ¿Y por qué?

## Conclusiones

A partir del análisis de correlación de las propiedades mecánicas de los aceros SAE 1XXX, se identificaron asociaciones estadísticamente significativas entre el esfuerzo último a la tracción (UTS), el esfuerzo de cedencia (YS), la dureza Brinell, la elongación y la reducción de área. La correlación más elevada se encontró entre UTS y dureza, con coeficientes de Pearson de 0.9946 y Spearman de 0.9914. Esta relación puede explicarse porque ambas propiedades dependen de la resistencia del material a la deformación plástica. En los aceros al carbono, el incremento de la proporción de perlita respecto a la ferrita, así como el endurecimiento por deformación, dificultan el movimiento de las dislocaciones, aumentando simultáneamente la resistencia y la dureza. Además, esta asociación permaneció elevada después de controlar el contenido de carbono y las condiciones de procesamiento, con una correlación parcial de 0.9751.

Por otra parte, se encontró una correlación negativa importante entre YS y elongación, con un coeficiente de Spearman de -0.9136. Este comportamiento refleja la relación inversa que generalmente existe entre resistencia mecánica y ductilidad. Durante el estirado en frío, por ejemplo, aumenta la densidad de dislocaciones, dificultando la deformación plástica posterior y elevando el esfuerzo de cedencia, pero reduciendo la elongación. Sin embargo, al controlar el carbono y el procesamiento, la correlación disminuyó hasta -0.5353, lo que indica que parte de la relación inicial está asociada con las diferencias de composición y procesamiento. De manera similar, la dureza y UTS presentaron correlaciones negativas con la elongación de -0.8514 y -0.8491, respectivamente.

En cuanto a UTS y YS, se obtuvo una correlación positiva de Spearman de 0.7742, que aumentó hasta 0.9100 al controlar el carbono y el procesamiento. Aunque ambas propiedades representan la resistencia mecánica, corresponden a etapas distintas de la deformación: YS caracteriza el inicio de la deformación plástica, mientras que UTS representa el esfuerzo máximo alcanzado durante la tracción. Su diferencia depende, entre otros factores, de la capacidad de endurecimiento por deformación del material, lo que explica que no presenten una correspondencia perfecta.

Al separar los registros según el procesamiento, se observaron correlaciones particularmente elevadas entre las propiedades de resistencia. En los aceros laminados en caliente (*Hot rolled*), YS y dureza presentaron una correlación de Spearman de 0.9986, mientras que en los estirados en frío (*Cold drawn*) destacó la relación entre UTS y YS, con 0.9967. Estas asociaciones son consistentes con la influencia conjunta de la composición y los mecanismos de endurecimiento. En contraste, el grupo *Cold drawn + Annealed* presentó correlaciones menores, posiblemente relacionadas con los procesos de recuperación y recristalización asociados al recocido, que modifican la estructura de dislocaciones y las propiedades mecánicas. No obstante, las diferencias de composición y el menor número de registros también pueden contribuir a este comportamiento.

Finalmente, los resultados muestran que las propiedades mecánicas de los aceros SAE 1XXX están estrechamente relacionadas, especialmente aquellas vinculadas con la resistencia a la deformación plástica. Asimismo, se identificó una tendencia inversa entre resistencia y ductilidad, consistente con los mecanismos de endurecimiento de los aceros al carbono. Sin embargo, estas correlaciones representan asociaciones estadísticas y no demuestran causalidad, ya que las diferencias de composición, microestructura y procesamiento pueden influir simultáneamente en las propiedades estudiadas.

Referencias:

ASKELAND, R. D.

The Science and Engineering of Materials

6th edition

USA, 2011

ST.

CALLISTER, D. W.

Materials Science and Engineering: an Introduction

2010

New York, U.S.A., 2010

John Wiley

SHACKELFORD, F. J.

Introduction to Materials Science for Engineers Todos

7th edition

New Jersey, U.S.A. 2008

Macmillan
