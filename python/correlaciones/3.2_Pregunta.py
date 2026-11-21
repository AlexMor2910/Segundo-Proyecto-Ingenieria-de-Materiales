import re
from pathlib import Path
from itertools import combinations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr

# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

INPUT_FILE = "Cleansed_Treatment_Carbon_Steel_Summary_Fixed.csv"
OUTPUT_DIR = Path("Graficas_Correlaciones_Propiedades_1XXX")
OUTPUT_DIR.mkdir(exist_ok=True)

GRADE = "SAE Grade"
GROUP = "Processing Group"
PROPERTIES = ["UTS (MPa)", "YS (MPa)", "Hardness (HB)", "Elongation (%)", "Reduction (%)"]
PROCESSING_ORDER = ["Hot rolled", "Cold drawn", "Cold drawn + Annealed"]

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 300, "axes.titlesize": 12, "axes.labelsize": 10})

# ============================================================
# 2. CARGA Y PREPARACIÓN DE DATOS
# ============================================================

dataset = pd.read_csv(INPUT_FILE)

required = [GRADE, "Mechanical Conditions", "Heat Treatment"] + PROPERTIES
missing = [column for column in required if column not in dataset.columns]
if missing:
    raise ValueError(f"Faltan columnas en el CSV: {missing}")

dataset[GRADE] = pd.to_numeric(dataset[GRADE], errors="coerce")
dataset["Main Series"] = dataset[GRADE].astype("Int64").astype(str).str.zfill(4).str[0]

def classify_processing(row):
    mechanical = row["Mechanical Conditions"]
    thermal = row["Heat Treatment"]
    if mechanical == "Cold drawn" and thermal == "Annealed":
        return "Cold drawn + Annealed"
    if mechanical == "Hot rolled":
        return "Hot rolled"
    if mechanical == "Cold drawn":
        return "Cold drawn"
    return np.nan

dataset[GROUP] = dataset.apply(classify_processing, axis=1)
data = dataset[(dataset["Main Series"] == "1") & dataset[GROUP].notna()].copy()
data[GROUP] = pd.Categorical(data[GROUP], categories=PROCESSING_ORDER, ordered=True)

if data.empty:
    raise ValueError("No hay registros SAE 1XXX en los grupos de procesamiento definidos.")

print(f"Registros incluidos: {len(data)}")
print(f"Grados SAE distintos: {data[GRADE].nunique()}")
print(f"Las gráficas se guardarán en: {OUTPUT_DIR.resolve()}")

# ============================================================
# 3. MAPAS DE CALOR: PEARSON Y SPEARMAN
# ============================================================

def plot_correlation_heatmap(frame, method, title, filename):
    matrix = frame[PROPERTIES].corr(method=method, min_periods=3)
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(matrix, annot=True, fmt=".2f", cmap="coolwarm", center=0, vmin=-1, vmax=1, square=True, linewidths=0.7, cbar_kws={"label": "Coeficiente de correlación"}, ax=ax)
    ax.set_title(title, pad=14, weight="bold")
    ax.tick_params(axis="x", rotation=35)
    ax.tick_params(axis="y", rotation=0)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, bbox_inches="tight")
    plt.close(fig)

plot_correlation_heatmap(data, "pearson", "Correlación de Pearson entre propiedades mecánicas - SAE 1XXX", "01_Heatmap_Pearson_General.png")
plot_correlation_heatmap(data, "spearman", "Correlación de Spearman entre propiedades mecánicas - SAE 1XXX", "02_Heatmap_Spearman_General.png")

for group in PROCESSING_ORDER:
    subset = data[data[GROUP] == group]
    if len(subset) >= 3:
        safe_group = re.sub(r"[^A-Za-z0-9]+", "_", group).strip("_")
        plot_correlation_heatmap(subset, "spearman", f"Correlación de Spearman - {group}", f"Heatmap_Spearman_{safe_group}.png")

# ============================================================
# 4. DIAGRAMAS DE DISPERSIÓN DE LAS RELACIONES PRINCIPALES
# ============================================================

MAIN_PAIRS = [
    ("UTS (MPa)", "Hardness (HB)", "UTS vs. dureza Brinell"),
    ("YS (MPa)", "Elongation (%)", "Esfuerzo de cedencia vs. elongación"),
    ("UTS (MPa)", "YS (MPa)", "UTS vs. esfuerzo de cedencia"),
    ("Elongation (%)", "Reduction (%)", "Elongación vs. reducción de área")
]

for x_var, y_var, title in MAIN_PAIRS:
    plot_data = data[[x_var, y_var, GROUP]].dropna()
    rho, p_value = spearmanr(plot_data[x_var], plot_data[y_var])

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.scatterplot(data=plot_data, x=x_var, y=y_var, hue=GROUP, hue_order=PROCESSING_ORDER, s=65, alpha=0.8, ax=ax)

    # Línea descriptiva por grupo; no representa un modelo causal.
    for group in PROCESSING_ORDER:
        subset = plot_data[plot_data[GROUP] == group]
        if len(subset) >= 3 and subset[x_var].nunique() >= 2:
            sns.regplot(data=subset, x=x_var, y=y_var, scatter=False, ci=None, truncate=True, line_kws={"linewidth": 1.8}, ax=ax)

    ax.set_title(f"{title}\nSpearman ρ = {rho:.3f} | p = {p_value:.3e}", weight="bold")
    ax.legend(title="Procesamiento")
    ax.grid(alpha=0.25)
    plt.tight_layout()
    safe_name = re.sub(r"[^A-Za-z0-9]+", "_", f"{x_var}_vs_{y_var}").strip("_")
    fig.savefig(OUTPUT_DIR / f"Scatter_{safe_name}.png", bbox_inches="tight")
    plt.close(fig)

# ============================================================
# 5. COMPARACIÓN DE CORRELACIONES ENTRE PROCESAMIENTOS
# ============================================================

pairs_to_compare = [
    ("UTS (MPa)", "Hardness (HB)"),
    ("YS (MPa)", "Elongation (%)"),
    ("UTS (MPa)", "YS (MPa)"),
    ("Elongation (%)", "Reduction (%)")
]

comparison_rows = []
for x_var, y_var in pairs_to_compare:
    for group in PROCESSING_ORDER:
        subset = data[data[GROUP] == group][[x_var, y_var]].dropna()
        rho = spearmanr(subset[x_var], subset[y_var]).statistic if len(subset) >= 3 else np.nan
        comparison_rows.append({"Pair": f"{x_var} vs. {y_var}", "Processing": group, "Spearman rho": rho, "n": len(subset)})

comparison = pd.DataFrame(comparison_rows)
comparison.to_csv(OUTPUT_DIR / "Correlaciones_Comparadas_por_Procesamiento.csv", index=False)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=comparison, x="Pair", y="Spearman rho", hue="Processing", hue_order=PROCESSING_ORDER, ax=ax)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_ylim(-1.05, 1.05)
ax.set_ylabel("Correlación de Spearman (ρ)")
ax.set_xlabel("Par de propiedades")
ax.set_title("Comparación de correlaciones según procesamiento", weight="bold")
ax.tick_params(axis="x", rotation=20)
ax.legend(title="Procesamiento")
plt.tight_layout()
fig.savefig(OUTPUT_DIR / "Comparacion_Correlaciones_Procesamiento.png", bbox_inches="tight")
plt.close(fig)

# ============================================================
# 6. RANKING GENERAL DE LAS CORRELACIONES
# ============================================================

ranking_rows = []
for prop1, prop2 in combinations(PROPERTIES, 2):
    subset = data[[prop1, prop2]].dropna()
    if len(subset) >= 3 and subset[prop1].nunique() > 1 and subset[prop2].nunique() > 1:
        rho, p_value = spearmanr(subset[prop1], subset[prop2])
        ranking_rows.append({"Pair": f"{prop1} vs. {prop2}", "Spearman rho": rho, "Absolute rho": abs(rho), "p-value": p_value, "n": len(subset)})

ranking = pd.DataFrame(ranking_rows).sort_values("Absolute rho", ascending=True)
ranking.to_csv(OUTPUT_DIR / "Ranking_Correlaciones_Spearman.csv", index=False)

fig, ax = plt.subplots(figsize=(10, 7))
bar_colors = ["#C44E52" if value < 0 else "#4C72B0" for value in ranking["Spearman rho"]]
ax.barh(ranking["Pair"], ranking["Spearman rho"], color=bar_colors)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_xlim(-1.05, 1.05)
ax.set_xlabel("Correlación de Spearman (ρ)")
ax.set_title("Ranking de correlaciones entre propiedades mecánicas - SAE 1XXX", weight="bold")
ax.grid(axis="x", alpha=0.25)
plt.tight_layout()
fig.savefig(OUTPUT_DIR / "Ranking_Correlaciones_Spearman.png", bbox_inches="tight")
plt.close(fig)

# ============================================================
# 7. DISTRIBUCIONES DE LAS PROPIEDADES POR PROCESAMIENTO
# ============================================================

for prop in PROPERTIES:
    plot_data = data[[GROUP, prop]].dropna()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=plot_data, x=GROUP, y=prop, order=PROCESSING_ORDER, showfliers=False, ax=ax)
    sns.stripplot(data=plot_data, x=GROUP, y=prop, order=PROCESSING_ORDER, color="black", alpha=0.35, size=3.5, jitter=0.18, ax=ax)
    ax.set_title(f"Distribución de {prop} por procesamiento", weight="bold")
    ax.set_xlabel("Condición de procesamiento")
    ax.set_ylabel(prop)
    ax.tick_params(axis="x", rotation=15)
    plt.tight_layout()
    safe_prop = re.sub(r"[^A-Za-z0-9]+", "_", prop).strip("_")
    fig.savefig(OUTPUT_DIR / f"Distribucion_{safe_prop}.png", bbox_inches="tight")
    plt.close(fig)

# ============================================================
# 8. EXPORTAR MATRICES DE CORRELACIÓN
# ============================================================

data[PROPERTIES].corr(method="pearson").to_csv(OUTPUT_DIR / "Matriz_Pearson_General.csv")
data[PROPERTIES].corr(method="spearman").to_csv(OUTPUT_DIR / "Matriz_Spearman_General.csv")

print("\n" + "=" * 75)
print("GRÁFICAS GENERADAS CORRECTAMENTE")
print("=" * 75)
for file in sorted(OUTPUT_DIR.glob("*.png")):
    print(file.name)
print(f"\nTotal de gráficas: {len(list(OUTPUT_DIR.glob('*.png')))}")
print(f"Directorio: {OUTPUT_DIR.resolve()}")
