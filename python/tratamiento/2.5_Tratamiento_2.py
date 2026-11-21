import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, linregress
from pathlib import Path
import re

# ==========================================
# 1. Cargar dataset
# ==========================================
dataset = pd.read_csv("Cleansed_Treatment_Carbon_Steel_Summary_Fixed.csv")

# ==========================================
# 2. Crear serie principal (primer dígito)
# ==========================================
dataset["Main Series"] = dataset["SAE Grade"].astype(str).str.zfill(4).str[0] + "XXX"

# ==========================================
# 3. Clasificación mutuamente excluyente del tratamiento
# ==========================================
def classify_treatment(row):
    mechanical = row["Mechanical Conditions"]
    thermal = row["Heat Treatment"]

    if mechanical == "Cold drawn" and thermal == "Annealed":
        return "Annealed + Cold drawn"
    elif mechanical == "Hot rolled":
        return "Hot rolled"
    elif mechanical == "Cold drawn":
        return "Cold drawn"
    elif thermal == "Normalized":
        return "Normalized"
    elif thermal == "Annealed":
        return "Annealed"
    elif thermal == "Quenched and tempered":
        return "Quenched"
    else:
        return "Unspecified"

dataset["Treatment Group"] = dataset.apply(classify_treatment, axis=1)

# ==========================================
# 4. Configuración general
# ==========================================
properties = ["UTS (MPa)", "YS (MPa)", "Hardness (HB)", "Elongation (%)"]

treatment_order = ["Hot rolled", "Cold drawn", "Annealed + Cold drawn", "Normalized", "Annealed", "Quenched"]

# Colores fijos para facilitar comparación entre figuras
color_map = {
    "Hot rolled": "tab:blue",
    "Cold drawn": "tab:orange",
    "Annealed + Cold drawn": "tab:green",
    "Normalized": "tab:red",
    "Annealed": "tab:purple",
    "Quenched": "tab:brown",
    "Unspecified": "tab:gray"
}

output_dir = Path("graficas_series_principales_por_tratamiento")
output_dir.mkdir(exist_ok=True)

results = []

# ==========================================
# 5. Revisar series principales disponibles
# ==========================================
main_series_list = sorted(dataset["Main Series"].dropna().unique())

# ==========================================
# 6. Generar una figura por serie principal
# ==========================================
for main_series in main_series_list:
    subset_series = dataset[dataset["Main Series"] == main_series].copy()

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    axes = axes.flatten()

    for ax, prop in zip(axes, properties):
        legend_handles = []
        legend_labels = []

        for treatment in treatment_order:
            subset = subset_series[subset_series["Treatment Group"] == treatment].dropna(subset=["C (%)", prop])

            if subset.empty:
                continue

            x = subset["C (%)"]
            y = subset[prop]
            n = len(subset)

            scatter = ax.scatter(x, y, alpha=0.75, s=45, color=color_map[treatment], label=treatment)

            legend_handles.append(scatter)
            legend_labels.append(treatment)

            pearson_r = np.nan
            p_value = np.nan
            slope = np.nan
            intercept = np.nan
            r_squared = np.nan

            # Dibujar regresión lineal por tratamiento si es posible
            if n >= 2 and x.nunique() >= 2 and y.nunique() >= 2:
                pearson = pearsonr(x, y)
                regression = linregress(x, y)

                pearson_r = pearson.statistic
                p_value = pearson.pvalue
                slope = regression.slope
                intercept = regression.intercept
                r_squared = regression.rvalue**2

                x_line = np.linspace(x.min(), x.max(), 100)
                y_line = intercept + slope * x_line
                ax.plot(x_line, y_line, color=color_map[treatment], linewidth=2, alpha=0.9)

            results.append({
                "Main Series": main_series,
                "Treatment Group": treatment,
                "Property": prop,
                "n": n,
                "Pearson r": pearson_r,
                "p-value": p_value,
                "Slope": slope,
                "Intercept": intercept,
                "R²": r_squared
            })

        ax.set_xlabel("Carbono nominal, C (%)")
        ax.set_ylabel(prop)
        ax.set_title(f"{main_series}: C vs. {prop}")
        ax.grid(alpha=0.25)

    # Leyenda única para toda la figura
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        unique = dict(zip(labels, handles))
        fig.legend(unique.values(), unique.keys(), loc="upper center", ncol=3, frameon=True, bbox_to_anchor=(0.5, 0.98))

    fig.suptitle(f"Relación entre carbono y propiedades mecánicas - Serie {main_series}", fontsize=15)
    plt.tight_layout(rect=[0, 0, 1, 0.93])

    filename = output_dir / f"MAIN_{main_series}_tratamientos.png"
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close(fig)

# ==========================================
# 7. Exportar tabla de resultados
# ==========================================
results_df = pd.DataFrame(results)
results_df = results_df.sort_values(["Main Series", "Property", "Treatment Group"])
results_df.to_csv(output_dir / "Pearson_por_serie_principal_y_tratamiento.csv", index=False)

print(results_df.to_string(index=False))

# ==========================================
# 8. Resumen de tamaños de muestra
# ==========================================
summary_counts = dataset.groupby(["Main Series", "Treatment Group"]).size().reset_index(name="n")
summary_counts = summary_counts.sort_values(["Main Series", "Treatment Group"])
summary_counts.to_csv(output_dir / "Conteo_por_serie_principal_y_tratamiento.csv", index=False)

print("\nConteo por serie principal y tratamiento:\n")
print(summary_counts.to_string(index=False))