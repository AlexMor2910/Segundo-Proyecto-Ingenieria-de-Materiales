import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, linregress
from pathlib import Path

# =========================
# 1. Cargar dataset
# =========================
dataset = pd.read_csv("Cleansed_Treatment_Carbon_Steel_Summary_Fixed.csv")

# =========================
# 2. Crear columna de serie SAE
# =========================
dataset["SAE Series"] = dataset["SAE Grade"].astype(str).str.zfill(4).str[:2] + "XX"

# =========================
# 3. Definir propiedades a analizar
# =========================
properties = ["UTS (MPa)", "YS (MPa)", "Hardness (HB)", "Elongation (%)"]

# =========================
# 4. Crear carpeta de salida
# =========================
output_dir = Path("graficas_por_serie")
output_dir.mkdir(exist_ok=True)

# =========================
# 5. Obtener series disponibles
# =========================
series_list = sorted(dataset["SAE Series"].dropna().unique())

# =========================
# 6. Tabla para guardar resultados
# =========================
results = []

# =========================
# 7. Generar una figura por serie
# =========================
for sae_series in series_list:
    subset_series = dataset[dataset["SAE Series"] == sae_series].copy()

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    for ax, prop in zip(axes, properties):
        subset = subset_series.dropna(subset=["C (%)", prop])

        x = subset["C (%)"]
        y = subset[prop]
        n = len(subset)

        ax.scatter(x, y, alpha=0.75)

        if n >= 2 and x.nunique() >= 2 and y.nunique() >= 2:
            pearson = pearsonr(x, y)
            regression = linregress(x, y)

            x_line = np.linspace(x.min(), x.max(), 100)
            y_line = regression.intercept + regression.slope * x_line
            ax.plot(x_line, y_line, linewidth=2)

            text_box = f"n = {n}\nr = {pearson.statistic:.3f}\np = {pearson.pvalue:.3e}\nR² = {regression.rvalue**2:.3f}"
            ax.text(0.05, 0.95, text_box, transform=ax.transAxes, verticalalignment="top", bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

            results.append({
                "SAE Series": sae_series,
                "Property": prop,
                "n": n,
                "Pearson r": pearson.statistic,
                "p-value": pearson.pvalue,
                "Slope": regression.slope,
                "Intercept": regression.intercept,
                "R²": regression.rvalue**2
            })
        else:
            ax.text(0.05, 0.95, f"n = {n}\nCorrelación no definida", transform=ax.transAxes, verticalalignment="top", bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

            results.append({
                "SAE Series": sae_series,
                "Property": prop,
                "n": n,
                "Pearson r": np.nan,
                "p-value": np.nan,
                "Slope": np.nan,
                "Intercept": np.nan,
                "R²": np.nan
            })

        ax.set_xlabel("Carbono nominal, C (%)")
        ax.set_ylabel(prop)
        ax.set_title(f"{sae_series}: C vs. {prop}")
        ax.grid(alpha=0.25)

    fig.suptitle(f"Relación entre carbono y propiedades mecánicas - Serie {sae_series}", fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.97])

    file_name = output_dir / f"{sae_series}_4propiedades.png"
    plt.savefig(file_name, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close(fig)

# =========================
# 8. Guardar tabla de resultados
# =========================
results_df = pd.DataFrame(results)
results_df = results_df.sort_values(["SAE Series", "Property"])
results_df.to_csv(output_dir / "Pearson_por_serie_y_propiedad.csv", index=False)

print(results_df.to_string(index=False))