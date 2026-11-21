import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from pathlib import Path
from scipy.stats import pearsonr, linregress

# ==========================================
# 1. CARGAR DATASET
# ==========================================

dataset = pd.read_csv("Cleansed_Treatment_Carbon_Steel_Summary_Fixed.csv")

dataset["SAE Series"] = dataset["SAE Grade"].astype(str).str.zfill(4).str[:2] + "XX"

properties = ["UTS (MPa)", "YS (MPa)", "Hardness (HB)", "Elongation (%)"]

MIN_N = 5

output_dir = Path("graficas_por_serie_y_procesamiento")
output_dir.mkdir(exist_ok=True)

# ==========================================
# 2. CLASIFICACIÓN JERÁRQUICA
# ==========================================

def classify_processing(row):
    mechanical = row["Mechanical Conditions"]
    thermal = row["Heat Treatment"]

    # Primero: combinaciones mecánicas y térmicas específicas
    if mechanical == "Cold drawn" and thermal == "Annealed":
        return "Cold drawn + Annealed"

    # Segundo: condiciones mecánicas
    elif mechanical == "Hot rolled":
        return "Hot rolled"

    elif mechanical == "Cold drawn":
        return "Cold drawn"

    # Tercero: tratamientos térmicos del resto de registros
    elif thermal == "Annealed":
        return "Annealed"

    elif thermal == "Normalized":
        return "Normalized"

    elif thermal == "Quenched and tempered":
        return "Quenched and tempered"

    else:
        return None


dataset["Processing Group"] = dataset.apply(classify_processing, axis=1)

# ==========================================
# 3. VERIFICAR DISTRIBUCIÓN DE LOS GRUPOS
# ==========================================

print("\nDISTRIBUCIÓN JERÁRQUICA DE LOS REGISTROS\n")

group_counts = dataset.groupby(["SAE Series", "Processing Group"], dropna=False).size().reset_index(name="n")

print(group_counts.to_string(index=False))

# Exportar tamaños de muestra
group_counts.to_csv(output_dir / "Distribucion_por_serie_y_procesamiento.csv", index=False)

# ==========================================
# 4. GENERAR GRÁFICAS Y CORRELACIONES
# ==========================================

results = []

series_list = sorted(dataset["SAE Series"].unique())

for sae_series in series_list:

    series_data = dataset[dataset["SAE Series"] == sae_series]

    processing_groups = sorted(series_data["Processing Group"].dropna().unique())

    for processing in processing_groups:

        subset_group = series_data[series_data["Processing Group"] == processing].copy()

        n_group = len(subset_group)

        print(f"\nAnalizando {sae_series} - {processing}: n={n_group}")

        # ==========================================
        # Calcular estadísticas para cada propiedad
        # ==========================================

        property_results = []

        for prop in properties:

            subset = subset_group.dropna(subset=["C (%)", prop])

            x = subset["C (%)"]
            y = subset[prop]

            n = len(subset)

            pearson_r = np.nan
            p_value = np.nan
            slope = np.nan
            intercept = np.nan
            r_squared = np.nan

            if n >= 2 and x.nunique() >= 2:

                regression = linregress(x, y)

                slope = regression.slope
                intercept = regression.intercept
                r_squared = regression.rvalue**2

                if y.nunique() >= 2:
                    pearson = pearsonr(x, y)
                    pearson_r = pearson.statistic
                    p_value = pearson.pvalue

            property_results.append({
                "SAE Series": sae_series,
                "Processing Group": processing,
                "Property": prop,
                "n": n,
                "Pearson r": pearson_r,
                "p-value": p_value,
                "Slope": slope,
                "Intercept": intercept,
                "R²": r_squared
            })

        results.extend(property_results)

        # ==========================================
        # Generar figura si hay suficientes registros
        # ==========================================

        if n_group < MIN_N:
            print(f"Figura omitida: menos de {MIN_N} observaciones.")
            continue

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()

        for ax, prop, result in zip(axes, properties, property_results):

            subset = subset_group.dropna(subset=["C (%)", prop])

            x = subset["C (%)"]
            y = subset[prop]

            n = len(subset)

            ax.scatter(x, y, alpha=0.75, s=45)

            if n >= 2 and x.nunique() >= 2:

                x_line = np.linspace(x.min(), x.max(), 100)
                y_line = result["Intercept"] + result["Slope"] * x_line

                ax.plot(x_line, y_line, linewidth=2)

            if not np.isnan(result["Pearson r"]):
                annotation = (
                    f"n = {n}\n"
                    f"r = {result['Pearson r']:.3f}\n"
                    f"p = {result['p-value']:.3e}\n"
                    f"R² = {result['R²']:.3f}"
                )
            else:
                annotation = f"n = {n}\nPearson no definido"

            ax.text(0.05, 0.95, annotation, transform=ax.transAxes, verticalalignment="top", bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

            ax.set_xlabel("Carbono nominal, C (%)")
            ax.set_ylabel(prop)
            ax.set_title(f"C vs. {prop}")
            ax.grid(alpha=0.25)

        fig.suptitle(f"Serie SAE {sae_series} - {processing}", fontsize=14)

        plt.tight_layout(rect=[0, 0, 1, 0.95])

        # ==========================================
        # Guardar con nombres únicos
        # ==========================================

        safe_processing = re.sub(r"[^A-Za-z0-9_-]", "_", processing)

        filename = f"SAE_{sae_series}_{safe_processing}_4propiedades.png"

        plt.savefig(output_dir / filename, dpi=300, bbox_inches="tight")

        plt.show()
        plt.close(fig)

# ==========================================
# 5. EXPORTAR RESULTADOS ESTADÍSTICOS
# ==========================================

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(["SAE Series", "Processing Group", "Property"])

results_df.to_csv(output_dir / "Pearson_SAE_Procesamiento.csv", index=False)

print("\nRESULTADOS DE PEARSON\n")
print(results_df.to_string(index=False))

# ==========================================
# 6. RESUMEN DE GRUPOS
# ==========================================

print("\nRESUMEN DE OBSERVACIONES POR GRUPO\n")
print(group_counts.to_string(index=False))

print(f"\nArchivos guardados en: {output_dir.resolve()}")
