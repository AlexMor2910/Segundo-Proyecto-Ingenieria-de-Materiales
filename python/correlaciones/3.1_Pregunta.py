import warnings
import re
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr, t
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

INPUT_FILE = "Cleansed_Treatment_Carbon_Steel_Summary_Fixed.csv"
OUTPUT_DIR = Path("Correlaciones_Propiedades_Mecanicas_1XXX")
TABLES_DIR = OUTPUT_DIR / "Tablas"
PLOTS_DIR = OUTPUT_DIR / "Graficas"

for folder in [OUTPUT_DIR, TABLES_DIR, PLOTS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

ALPHA = 0.05
GRADE = "SAE Grade"
GROUP = "Processing Group"

# Se incluyen las cinco propiedades mecánicas disponibles en el CSV.
PROPERTIES = [
    "UTS (MPa)",
    "YS (MPa)",
    "Hardness (HB)",
    "Elongation (%)",
    "Reduction (%)"
]

PROCESSING_ORDER = ["Hot rolled", "Cold drawn", "Cold drawn + Annealed"]

# ============================================================
# 2. CARGA Y FILTRADO DE LA SERIE SAE 1XXX
# ============================================================

dataset = pd.read_csv(INPUT_FILE)

required_columns = [GRADE, "Mechanical Conditions", "Heat Treatment", "C (%)"] + PROPERTIES
missing_columns = [column for column in required_columns if column not in dataset.columns]
if missing_columns:
    raise ValueError(f"Faltan columnas necesarias en el CSV: {missing_columns}")

dataset[GRADE] = pd.to_numeric(dataset[GRADE], errors="coerce")
dataset["Main Series"] = dataset[GRADE].astype("Int64").astype(str).str.zfill(4).str[0]

def classify_processing(row):
    mechanical = row["Mechanical Conditions"]
    thermal = row["Heat Treatment"]

    if mechanical == "Cold drawn" and thermal == "Annealed":
        return "Cold drawn + Annealed"
    elif mechanical == "Hot rolled":
        return "Hot rolled"
    elif mechanical == "Cold drawn":
        return "Cold drawn"
    return np.nan

dataset[GROUP] = dataset.apply(classify_processing, axis=1)

data = dataset[(dataset["Main Series"] == "1") & dataset[GROUP].notna()].copy()
data[GROUP] = pd.Categorical(data[GROUP], categories=PROCESSING_ORDER, ordered=True)

if data.empty:
    raise ValueError("No se encontraron registros SAE 1XXX clasificados.")

print("=" * 75)
print("CORRELACIÓN ENTRE PROPIEDADES MECÁNICAS - SERIE SAE 1XXX")
print("=" * 75)
print(f"Registros incluidos: {len(data)}")
print(f"Grados SAE distintos: {data[GRADE].nunique()}")
print("\nTamaños de muestra por procesamiento:")
print(data[GROUP].value_counts().reindex(PROCESSING_ORDER).fillna(0).astype(int))

excluded = dataset[(dataset["Main Series"] == "1") & dataset[GROUP].isna()]
print(f"\nRegistros SAE 1XXX excluidos por procesamiento no clasificado: {len(excluded)}")
if not excluded.empty:
    print(excluded[[GRADE, "Mechanical Conditions", "Heat Treatment"]].to_string(index=False))

data.to_csv(OUTPUT_DIR / "Base_Analitica_1XXX.csv", index=False)

# ============================================================
# 3. FUNCIÓN PARA CALCULAR CORRELACIONES POR PARES
# ============================================================

def calculate_pairwise_correlations(frame, properties, group_name):
    rows = []

    for prop1, prop2 in combinations(properties, 2):
        subset = frame[[prop1, prop2]].dropna()
        n = len(subset)

        pearson_r = pearson_p = spearman_rho = spearman_p = np.nan

        if n >= 3 and subset[prop1].nunique() > 1 and subset[prop2].nunique() > 1:
            pearson_result = pearsonr(subset[prop1], subset[prop2])
            spearman_result = spearmanr(subset[prop1], subset[prop2])
            pearson_r = pearson_result.statistic
            pearson_p = pearson_result.pvalue
            spearman_rho = spearman_result.statistic
            spearman_p = spearman_result.pvalue

        rows.append({
            "Processing Group": group_name,
            "Property 1": prop1,
            "Property 2": prop2,
            "n": n,
            "Pearson r": pearson_r,
            "Pearson p": pearson_p,
            "Spearman rho": spearman_rho,
            "Spearman p": spearman_p,
            "Absolute Spearman": abs(spearman_rho) if pd.notna(spearman_rho) else np.nan
        })

    return pd.DataFrame(rows)

# ============================================================
# 4. CORRELACIONES GENERALES Y POR PROCESAMIENTO
# ============================================================

overall_corr = calculate_pairwise_correlations(data, PROPERTIES, "All 1XXX")
group_corr_frames = [overall_corr]

for group in PROCESSING_ORDER:
    subset = data[data[GROUP] == group]
    group_corr_frames.append(calculate_pairwise_correlations(subset, PROPERTIES, group))

correlations = pd.concat(group_corr_frames, ignore_index=True)

# Ajuste BH separado para cada conjunto de comparaciones y método.
correlations["Pearson q BH"] = np.nan
correlations["Spearman q BH"] = np.nan

for group_name, indices in correlations.groupby("Processing Group", observed=False).groups.items():
    idx = list(indices)
    for p_col, q_col in [("Pearson p", "Pearson q BH"), ("Spearman p", "Spearman q BH")]:
        valid_idx = [i for i in idx if pd.notna(correlations.loc[i, p_col])]
        if valid_idx:
            correlations.loc[valid_idx, q_col] = multipletests(correlations.loc[valid_idx, p_col], method="fdr_bh")[1]

correlations["Spearman significant BH"] = correlations["Spearman q BH"] < ALPHA
correlations["Pearson significant BH"] = correlations["Pearson q BH"] < ALPHA

correlations.to_csv(TABLES_DIR / "Correlaciones_Pares_Propiedades.csv", index=False)

print("\nCORRELACIONES GENERALES - ORDENADAS POR |SPEARMAN|")
print(
    overall_corr.sort_values("Absolute Spearman", ascending=False)
    [["Property 1", "Property 2", "n", "Pearson r", "Pearson p", "Spearman rho", "Spearman p"]]
    .to_string(index=False)
)

for group in PROCESSING_ORDER:
    print(f"\nCORRELACIONES - {group}")
    result = correlations[correlations["Processing Group"] == group].sort_values("Absolute Spearman", ascending=False)
    print(result[["Property 1", "Property 2", "n", "Pearson r", "Spearman rho", "Spearman q BH"]].to_string(index=False))

# ============================================================
# 5. MATRICES DE CORRELACIÓN Y MAPAS DE CALOR
# ============================================================

def save_correlation_heatmaps(frame, label):
    numeric = frame[PROPERTIES]
    pearson_matrix = numeric.corr(method="pearson", min_periods=3)
    spearman_matrix = numeric.corr(method="spearman", min_periods=3)

    safe_label = re.sub(r"[^A-Za-z0-9]+", "_", label).strip("_")
    pearson_matrix.to_csv(TABLES_DIR / f"Matriz_Pearson_{safe_label}.csv")
    spearman_matrix.to_csv(TABLES_DIR / f"Matriz_Spearman_{safe_label}.csv")

    for method, matrix in [("Pearson", pearson_matrix), ("Spearman", spearman_matrix)]:
        fig, ax = plt.subplots(figsize=(9, 7))
        sns.heatmap(matrix, annot=True, fmt=".2f", cmap="coolwarm", center=0, vmin=-1, vmax=1, square=True, linewidths=0.5, ax=ax)
        ax.set_title(f"Correlación {method} entre propiedades - {label}")
        plt.xticks(rotation=35, ha="right")
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / f"Heatmap_{method}_{safe_label}.png", dpi=300, bbox_inches="tight")
        plt.close(fig)

save_correlation_heatmaps(data, "Todos_los_1XXX")

for group in PROCESSING_ORDER:
    group_data = data[data[GROUP] == group]
    save_correlation_heatmaps(group_data, group)

# ============================================================
# 6. CORRELACIÓN PARCIAL CONTROLANDO CARBONO Y PROCESAMIENTO
# ============================================================
# Para cada propiedad se ajusta un modelo contra C (%) y las categorías
# de procesamiento. Después se correlacionan los residuos de cada par.
# Esto estima la asociación restante una vez retiradas esas covariables.
#
# La prueba t usa los grados de libertad de una correlación parcial:
# df = n - k - 2, donde k es el rango de las covariables sin contar
# el intercepto. Es una aproximación bajo los supuestos del modelo.

partial_rows = []
partial_data = data[[GRADE, "C (%)", GROUP] + PROPERTIES].dropna().copy()
partial_data[GROUP] = partial_data[GROUP].astype(str)

controls = pd.get_dummies(partial_data[[GROUP]], drop_first=True, dtype=float)
controls.insert(0, "C (%)", partial_data["C (%)"].astype(float))
X = sm.add_constant(controls, has_constant="add")
rank_x = np.linalg.matrix_rank(X.to_numpy())
k_controls = rank_x - 1

residuals = {}
for prop in PROPERTIES:
    y = pd.to_numeric(partial_data[prop], errors="coerce")
    fit = sm.OLS(y, X).fit()
    residuals[prop] = fit.resid

for prop1, prop2 in combinations(PROPERTIES, 2):
    r1 = residuals[prop1]
    r2 = residuals[prop2]
    valid = r1.notna() & r2.notna()
    n = int(valid.sum())
    partial_r = partial_p = np.nan

    if n > k_controls + 2 and r1[valid].nunique() > 1 and r2[valid].nunique() > 1:
        partial_r = pearsonr(r1[valid], r2[valid]).statistic
        dfree = n - k_controls - 2
        t_stat = partial_r * np.sqrt(dfree / max(1e-15, 1 - partial_r**2))
        partial_p = 2 * t.sf(abs(t_stat), dfree)

    partial_rows.append({
        "Property 1": prop1,
        "Property 2": prop2,
        "n": n,
        "Controls": "C (%) + Processing Group",
        "Partial correlation": partial_r,
        "p-value": partial_p
    })

partial_corr = pd.DataFrame(partial_rows)
valid = partial_corr["p-value"].notna()
partial_corr["p BH"] = np.nan
if valid.any():
    partial_corr.loc[valid, "p BH"] = multipletests(partial_corr.loc[valid, "p-value"], method="fdr_bh")[1]
partial_corr["Significant BH"] = partial_corr["p BH"] < ALPHA
partial_corr["Absolute partial correlation"] = partial_corr["Partial correlation"].abs()
partial_corr.to_csv(TABLES_DIR / "Correlaciones_Parciales_Control_C_y_Procesamiento.csv", index=False)

print("\nCORRELACIONES PARCIALES CONTROLANDO C (%) Y PROCESAMIENTO")
print(partial_corr.sort_values("Absolute partial correlation", ascending=False).to_string(index=False))

# ============================================================
# 7. GRÁFICAS DE DISPERSIÓN PARA LOS PARES MÁS CORRELACIONADOS
# ============================================================

top_pairs = overall_corr.dropna(subset=["Spearman rho"]).sort_values("Absolute Spearman", ascending=False).head(5)

for _, row in top_pairs.iterrows():
    prop1, prop2 = row["Property 1"], row["Property 2"]
    plot_data = data[[prop1, prop2, GROUP]].dropna()

    fig, ax = plt.subplots(figsize=(8, 6))
    for group in PROCESSING_ORDER:
        subset = plot_data[plot_data[GROUP] == group]
        if subset.empty:
            continue
        ax.scatter(subset[prop1], subset[prop2], alpha=0.7, s=45, label=f"{group} (n={len(subset)})")

    ax.set_xlabel(prop1)
    ax.set_ylabel(prop2)
    ax.set_title(f"{prop1} vs. {prop2} - SAE 1XXX\nSpearman ρ = {row['Spearman rho']:.3f}")
    ax.grid(alpha=0.25)
    ax.legend(title="Procesamiento")
    plt.tight_layout()

    safe_name = re.sub(r"[^A-Za-z0-9]+", "_", f"{prop1}_vs_{prop2}").strip("_")
    plt.savefig(PLOTS_DIR / f"Scatter_{safe_name}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

# ============================================================
# 8. RESUMEN DESCRIPTIVO DE PROPIEDADES
# ============================================================

descriptive = data[PROPERTIES].describe().T
descriptive.to_csv(TABLES_DIR / "Estadisticos_Descriptivos_Propiedades.csv")

# ============================================================
# 9. EXPORTAR RANKING DE CORRELACIONES
# ============================================================

ranking = overall_corr.dropna(subset=["Spearman rho"]).copy()
ranking = ranking.sort_values("Absolute Spearman", ascending=False)
ranking.insert(0, "Rank", range(1, len(ranking) + 1))
ranking.to_csv(TABLES_DIR / "Ranking_Correlaciones_Generales.csv", index=False)

partial_ranking = partial_corr.dropna(subset=["Partial correlation"]).sort_values("Absolute partial correlation", ascending=False)
partial_ranking.insert(0, "Rank", range(1, len(partial_ranking) + 1))
partial_ranking.to_csv(TABLES_DIR / "Ranking_Correlaciones_Parciales.csv", index=False)

# ============================================================
# 10. CONCLUSIONES AUTOMÁTICAS DESCRIPTIVAS
# ============================================================

print("\n" + "=" * 75)
print("RESUMEN AUTOMÁTICO")
print("=" * 75)

if not ranking.empty:
    strongest = ranking.iloc[0]
    print(f"Par con mayor |Spearman| en el conjunto: {strongest['Property 1']} y {strongest['Property 2']}")
    print(f"Spearman rho = {strongest['Spearman rho']:.4f}; p = {strongest['Spearman p']:.4g}")

if not partial_ranking.empty:
    strongest_partial = partial_ranking.iloc[0]
    print("\nPar con mayor asociación parcial controlando carbono y procesamiento:")
    print(f"{strongest_partial['Property 1']} y {strongest_partial['Property 2']}")
    print(f"Correlación parcial = {strongest_partial['Partial correlation']:.4f}; p ajustada BH = {strongest_partial['p BH']:.4g}")

print("\nNOTAS METODOLÓGICAS:")
print("- Pearson mide asociación lineal y es sensible a valores extremos.")
print("- Spearman mide asociación monotónica basada en rangos y es menos sensible a extremos.")
print("- Las correlaciones generales pueden estar influidas por diferencias entre tratamientos.")
print("- Las correlaciones por procesamiento permiten comprobar si la asociación se mantiene dentro de cada grupo.")
print("- La correlación parcial controla C (%) y procesamiento, pero no controla todos los factores metalúrgicos ni el grado SAE.")
print("- Las correlaciones no demuestran causalidad.")
print("- Una asociación entre propiedades puede deberse a mecanismos metalúrgicos compartidos, al procesamiento o a variables omitidas.")
print(f"\nResultados guardados en: {OUTPUT_DIR.resolve()}")
