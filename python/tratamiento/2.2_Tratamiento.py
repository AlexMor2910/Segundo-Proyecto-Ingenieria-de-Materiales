import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, linregress

# Cargar dataset definitivo
dataset = pd.read_csv("Cleansed_Treatment_Carbon_Steel_Summary_Fixed.csv")

# Identificar las series SAE (primeros dos dígitos)
dataset["SAE Series"] = dataset["SAE Grade"].astype(str).str.zfill(4).str[:2] + "xx"

# Propiedades que se analizarán
properties = ["UTS (MPa)", "YS (MPa)", "Hardness (HB)", "Elongation (%)"]

# Identificar todas las series disponibles
series = sorted(dataset["SAE Series"].unique())

# Generar colores consistentes para todas las gráficas
colors = plt.cm.tab20(np.linspace(0, 1, len(series)))
color_map = dict(zip(series, colors))

# Almacenar resultados estadísticos
correlation_results = []

# Generar una gráfica por propiedad
for prop in properties:

    fig, ax = plt.subplots(figsize=(11, 7))

    for sae_series in series:

        subset = dataset[dataset["SAE Series"] == sae_series].dropna(subset=["C (%)", prop])

        x = subset["C (%)"]
        y = subset[prop]
        n = len(subset)

        # Graficar observaciones
        ax.scatter(x, y, color=color_map[sae_series], alpha=0.75, s=45, label=sae_series)

        # Calcular Pearson y regresión cuando sea matemáticamente posible
        if n >= 2 and x.nunique() >= 2 and y.nunique() >= 2:

            pearson = pearsonr(x, y)
            regression = linregress(x, y)

            correlation_results.append({
                "SAE Series": sae_series,
                "Property": prop,
                "n": n,
                "Pearson r": pearson.statistic,
                "p-value": pearson.pvalue,
                "Slope": regression.slope,
                "Intercept": regression.intercept,
                "R²": regression.rvalue**2
            })

            # Dibujar regresión lineal de la serie
            x_line = np.linspace(x.min(), x.max(), 100)
            y_line = regression.intercept + regression.slope * x_line

            ax.plot(x_line, y_line, color=color_map[sae_series], linewidth=2)

        else:

            correlation_results.append({
                "SAE Series": sae_series,
                "Property": prop,
                "n": n,
                "Pearson r": np.nan,
                "p-value": np.nan,
                "Slope": np.nan,
                "Intercept": np.nan,
                "R²": np.nan
            })

    ax.set_xlabel("Carbono nominal C (%)", fontsize=12)
    ax.set_ylabel(prop, fontsize=12)
    ax.set_title(f"Carbono vs. {prop} por serie SAE", fontsize=14)

    ax.grid(alpha=0.25)
    ax.legend(title="Serie SAE", bbox_to_anchor=(1.02, 1), loc="upper left")

    plt.tight_layout()
    plt.savefig(f"Carbon_{prop.replace(' ', '_').replace('(', '').replace(')', '').replace('%', 'pct')}.png", dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

# Crear tabla de resultados
results_df = pd.DataFrame(correlation_results)

# Ordenar resultados
results_df = results_df.sort_values(["Property", "SAE Series"])

# Mostrar resultados
print("\nCORRELACIONES DE PEARSON POR SERIE SAE\n")
print(results_df.to_string(index=False))

# Exportar resultados
results_df.to_csv("Pearson_by_SAE_Series.csv", index=False)

# Mostrar únicamente correlaciones estadísticamente significativas
print("\nCORRELACIONES CON p < 0.05\n")
print(results_df[results_df["p-value"] < 0.05].to_string(index=False))
