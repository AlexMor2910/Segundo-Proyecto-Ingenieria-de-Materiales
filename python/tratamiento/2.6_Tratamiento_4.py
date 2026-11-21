import pandas as pd
import numpy as np
from scipy.stats import f_oneway, levene, shapiro
from statsmodels.stats.oneway import anova_oneway
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from pathlib import Path

# ==========================================
# 1. CARGAR DATASET
# ==========================================

dataset = pd.read_csv("Cleansed_Treatment_Carbon_Steel_Summary_Fixed.csv")

properties = ["UTS (MPa)", "YS (MPa)", "Hardness (HB)", "Elongation (%)"]

output_dir = Path("Resultados_ANOVA")
output_dir.mkdir(exist_ok=True)

# ==========================================
# 2. CLASIFICAR LOS REGISTROS
# ==========================================

dataset["Main Series"] = dataset["SAE Grade"].astype(str).str.zfill(4).str[0]

def classify_1xxx(row):
    mechanical = row["Mechanical Conditions"]
    thermal = row["Heat Treatment"]

    if mechanical == "Cold drawn" and thermal == "Annealed":
        return "Cold drawn + Annealed"
    elif mechanical == "Hot rolled":
        return "Hot rolled"
    elif mechanical == "Cold drawn":
        return "Cold drawn"
    else:
        return None

dataset["Group 1XXX"] = dataset.apply(classify_1xxx, axis=1)

dataset["Group Other"] = dataset["Heat Treatment"].replace({
    "Normalized": "Normalized",
    "Annealed": "Annealed",
    "Quenched and tempered": "Quenched and tempered"
})

# ==========================================
# 3. CREAR LOS DOS CONJUNTOS
# ==========================================

data_1xxx = dataset[
    (dataset["Main Series"] == "1") &
    (dataset["Group 1XXX"].notna())
].copy()

data_other = dataset[
    (dataset["Main Series"] != "1") &
    (dataset["Group Other"].isin(["Normalized", "Annealed", "Quenched and tempered"]))
].copy()

# ==========================================
# 4. FUNCIÓN PARA REALIZAR ANOVA
# ==========================================

def perform_anova(data, group_column, properties, analysis_name):

    results = []

    for prop in properties:

        subset = data[[group_column, prop]].dropna()

        groups = {
            name: group[prop].values
            for name, group in subset.groupby(group_column)
        }

        groups = {
            name: values
            for name, values in groups.items()
            if len(values) >= 2
        }

        print(f"\n{'='*60}")
        print(f"{analysis_name} - {prop}")
        print(f"{'='*60}")

        for name, values in groups.items():
            print(f"{name}: n={len(values)}, mean={np.mean(values):.3f}, SD={np.std(values, ddof=1):.3f}")

        if len(groups) < 2:
            print("Datos insuficientes para realizar ANOVA.")
            continue

        group_values = list(groups.values())
        group_labels = list(groups.keys())

        # ANOVA convencional
        anova = f_oneway(*group_values)

        # Homogeneidad de varianzas
        levene_test = levene(*group_values, center="median")

        # Normalidad de los residuos
        residuals = np.concatenate([
            values - np.mean(values)
            for values in group_values
        ])

        shapiro_test = shapiro(residuals)

        # ANOVA de Welch
        welch = anova_oneway(group_values, use_var="unequal")

        # Tamaño de efecto eta cuadrada
        grand_mean = subset[prop].mean()
        ss_between = sum(len(values) * (np.mean(values) - grand_mean)**2 for values in group_values)
        ss_total = sum((value - grand_mean)**2 for value in subset[prop])
        eta_squared = ss_between / ss_total if ss_total > 0 else np.nan

        # Selección del resultado principal
        equal_variances = levene_test.pvalue >= 0.05

        selected_test = "ANOVA convencional" if equal_variances else "ANOVA de Welch"
        selected_statistic = anova.statistic if equal_variances else welch.statistic
        selected_pvalue = anova.pvalue if equal_variances else welch.pvalue

        print(f"\nANOVA convencional: F={anova.statistic:.4f}, p={anova.pvalue:.5f}")
        print(f"Levene: p={levene_test.pvalue:.5f}")
        print(f"Shapiro-Wilk residuos: p={shapiro_test.pvalue:.5f}")
        print(f"ANOVA Welch: F={welch.statistic:.4f}, p={welch.pvalue:.5f}")
        print(f"Eta cuadrada: {eta_squared:.4f}")
        print(f"Prueba seleccionada: {selected_test}")
        print(f"Resultado: {'Diferencias significativas' if selected_pvalue < 0.05 else 'Sin diferencias significativas'}")

        results.append({
            "Analysis": analysis_name,
            "Property": prop,
            "N": len(subset),
            "Groups": len(groups),
            "ANOVA F": anova.statistic,
            "ANOVA p": anova.pvalue,
            "Levene p": levene_test.pvalue,
            "Shapiro residuals p": shapiro_test.pvalue,
            "Welch F": welch.statistic,
            "Welch p": welch.pvalue,
            "Eta squared": eta_squared,
            "Selected test": selected_test,
            "Selected p": selected_pvalue
        })

        # Post hoc Tukey: únicamente si se cumplen los criterios
        if equal_variances and anova.pvalue < 0.05:

            tukey = pairwise_tukeyhsd(
                endog=subset[prop],
                groups=subset[group_column],
                alpha=0.05
            )

            print("\nComparaciones post hoc Tukey:")
            print(tukey)

            with open(output_dir / f"Tukey_{analysis_name}_{prop.replace(' ', '_')}.txt", "w") as file:
                file.write(str(tukey))

        elif not equal_variances and welch.pvalue < 0.05:
            print("\nSe requiere un post hoc compatible con Welch, como Games-Howell.")

    return pd.DataFrame(results)

# ==========================================
# 5. EJECUTAR PRIMER ANOVA: SERIE 1XXX
# ==========================================

results_1xxx = perform_anova(
    data_1xxx,
    "Group 1XXX",
    properties,
    "Serie_1XXX"
)

# ==========================================
# 6. EJECUTAR SEGUNDO ANOVA: RESTO DE SERIES
# ==========================================

results_other = perform_anova(
    data_other,
    "Group Other",
    properties,
    "Otras_Series"
)

# ==========================================
# 7. EXPORTAR RESULTADOS
# ==========================================

results_1xxx.to_csv(output_dir / "ANOVA_Serie_1XXX.csv", index=False)

results_other.to_csv(output_dir / "ANOVA_Otras_Series.csv", index=False)

print("\nRESUMEN ANOVA 1XXX")
print(results_1xxx.to_string(index=False))

print("\nRESUMEN ANOVA OTRAS SERIES")
print(results_other.to_string(index=False))

# ==========================================
# 8. RESUMEN DE TAMAÑOS DE GRUPO
# ==========================================

print("\nTAMAÑOS DE LOS GRUPOS 1XXX")
print(data_1xxx.groupby("Group 1XXX").size())

print("\nTAMAÑOS DE LOS GRUPOS RESTANTES")
print(data_other.groupby("Group Other").size())
