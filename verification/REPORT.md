# Verificación de los resultados inferenciales

La ejecución del 21 de noviembre de 2026 usó Python 3.13.6, NumPy 2.5.5, pandas 3.1.1, SciPy 1.18.1, statsmodels 0.15.0 y Matplotlib 3.11.2. El SHA-256 del CSV está en `results/statistical-results.json`. Los scripts originales se ejecutaron sin modificaciones con una copia temporal del CSV; sus registros están junto al JSON.

Las poblaciones reproducidas tienen 65, 52 y 21 registros en los grupos 1XXX, y 19, 19 y 12 en los tres grupos de las demás series. Las ocho pruebas principales coinciden con los valores históricos redondeados del informe:

| Población | Propiedad | Prueba seleccionada | F reproducido | p reproducido |
| --- | --- | --- | ---: | ---: |
| 1XXX | UTS | Welch | 32.6894 | 2.4346e−11 |
| 1XXX | YS | Welch | 183.8626 | 7.6033e−32 |
| 1XXX | Dureza | Welch | 30.7737 | 8.9430e−11 |
| 1XXX | Elongación | Welch | 79.8991 | 4.2637e−20 |
| Otras | UTS | Convencional | 35.7694 | 3.6189e−10 |
| Otras | YS | Welch | 115.5819 | 1.9828e−13 |
| Otras | Dureza | Convencional | 39.6459 | 8.1654e−11 |
| Otras | Elongación | Convencional | 13.2307 | 2.7663e−5 |

El archivo estructurado incluye Levene, ambas variantes de ANOVA, grados de libertad, tamaños de efecto, medias y varianzas por grupo, nueve comparaciones Tukey y quince Games–Howell, con intervalos y probabilidades ajustadas. Las decisiones post hoc coinciden con el patrón descrito en el informe. Algunos valores Games–Howell se redondean a cero en `studentized_range.sf`; la interfaz no los presenta como probabilidades exactamente cero.

No se encontraron discrepancias en las ocho pruebas principales a la precisión histórica. El propio informe contiene una diferencia de alcance entre la descripción preliminar del grupo estirado y recocido y el resumen posterior de medias de ANOVA; se conserva esa distinción. La coincidencia con el informe no elimina las limitaciones observacionales ni la sensibilidad de algunas pruebas de Levene a valores cercanos a 0.05. Los intervalos y diferencias de medias usan la orientación original de cada biblioteca: Tukey calcula segundo menos primero y Games–Howell primero menos segundo.

## Intervalos individuales de medias añadidos para visualización

`mean_ci.py` calcula, para cada grupo y propiedad de las poblaciones fijas, `media ± t(0,975; n − 1) · s / √n`, con `s` muestral y el cuantil de SciPy 1.18.1. Antes de guardar `data/mean-ci.json`, comprueba el SHA-256 del CSV, el tamaño y la media de cada grupo contra los resultados verificados. Por ejemplo, UTS en 1XXX laminado en caliente tiene n = 65, media = 538.8462 MPa e intervalo [502.2609, 575.4314] MPa. Estos intervalos descriptivos no estaban en los resultados originales: no sustituyen los intervalos simultáneos de las diferencias ni establecen por sí solos la significancia de pares. La independencia y la aproximación de normalidad deben interpretarse con cautela ante grados repetidos y grupos observacionales.
