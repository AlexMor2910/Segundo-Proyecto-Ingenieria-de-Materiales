
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import studentized_range
from pathlib import Path
from itertools import combinations

# ==========================================
# 1. CARGAR DATASET Y CONFIGURACIÓN
# ==========================================

dataset = pd.read_csv("Cleansed_Treatment_Carbon_Steel_Summary_Fixed.csv")

properties = ["UTS (MPa)", "YS (MPa)", "Hardness (HB)", "Elongation (%)"]

output_dir = Path("Resultados_ANOVA")
games_dir = output_dir / "Games_Howell"
boxplot_dir = output_dir / "Boxplots"

games_dir.mkdir(parents=True, exist_ok=True)
boxplot_dir.mkdir(parents=True, exist_ok=True)

alpha = 0.05

# ==========================================
# 2. CLASIFICACIÓN DE LOS REGISTROS
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
    return None

dataset["Group 1XXX"] = dataset.apply(classify_1xxx, axis=1)

dataset["Group Other"] = dataset["Heat Treatment"].where(
    dataset["Heat Treatment"].isin(["Annealed", "Normalized", "Quenched and tempered"])
)

data_1xxx = dataset[(dataset["Main Series"] == "1") & dataset["Group 1XXX"].notna()].copy()

data_other = dataset[(dataset["Main Series"] != "1") & dataset["Group Other"].notna()].copy()

# ==========================================
# 3. FUNCIÓN GAMES-HOWELL
# ==========================================

def games_howell(data, group_column, property_name, alpha=0.05):

    groups = {
        name: group[property_name].dropna().values
        for name, group in data.groupby(group_column)
    }

    groups = {
        name: values
        for name, values in groups.items()
        if len(values) >= 2
    }

    k = len(groups)
    results = []

    for group1, group2 in combinations(groups.keys(), 2):

        x1 = groups[group1]
        x2 = groups[group2]

        n1, n2 = len(x1), len(x2)
        mean1, mean2 = np.mean(x1), np.mean(x2)
        var1, var2 = np.var(x1, ddof=1), np.var(x2, ddof=1)

        difference = mean1 - mean2

        # Error estándar
        se = np.sqrt(var1/n1 + var2/n2)

        if se == 0:
            continue

        # Estadístico t de Welch
        t_stat = abs(difference) / se

        # Grados de libertad de Welch-Satterthwaite
        df = (var1/n1 + var2/n2)**2 / (
            (var1/n1)**2/(n1-1) +
            (var2/n2)**2/(n2-1)
        )

        # Estadístico q de Games-Howell
        q_stat = t_stat * np.sqrt(2)

        # Valor p ajustado para comparaciones múltiples
        p_value = studentized_range.sf(q_stat, k, df)

        # Intervalo de confianza simultáneo
        q_critical = studentized_range.ppf(1-alpha, k, df)
        margin = q_critical * se / np.sqrt(2)

        lower = difference - margin
        upper = difference + margin

        results.append({
            "Property": property_name,
            "Group 1": group1,
            "Group 2": group2,
            "n1": n1,
            "n2": n2,
            "Mean 1": mean1,
            "Mean 2": mean2,
            "Mean Difference": difference,
            "t statistic": t_stat,
            "Degrees of Freedom": df,
            "q statistic": q_stat,
            "p-adjusted": p_value,
            "CI Lower": lower,
            "CI Upper": upper,
            "Significant": p_value < alpha
        })

    return pd.DataFrame(results)

# ==========================================
# 4. GAMES-HOWELL: SERIE 1XXX
# ==========================================

results_1xxx = []

for prop in properties:

    result = games_howell(data_1xxx, "Group 1XXX", prop, alpha)

    if not result.empty:
        results_1xxx.append(result)

        print(f"\nGAMES-HOWELL - SERIE 1XXX - {prop}")
        print(result.to_string(index=False))

if results_1xxx:
    games_1xxx_df = pd.concat(results_1xxx, ignore_index=True)
    games_1xxx_df.to_csv(games_dir / "Games_Howell_1XXX.csv", index=False)

# ==========================================
# 5. GAMES-HOWELL: RESTO DE SERIES
# ==========================================

result_other = games_howell(data_other, "Group Other", "YS (MPa)", alpha)

print("\nGAMES-HOWELL - OTRAS SERIES - YS")
print(result_other.to_string(index=False))

result_other.to_csv(games_dir / "Games_Howell_Otras_Series_YS.csv", index=False)

# ==========================================
# 6. CONFIGURACIÓN DE BOXPLOTS
# ==========================================

group_configs = [
    (data_1xxx, "Group 1XXX", "Serie 1XXX", ["Hot rolled", "Cold drawn", "Cold drawn + Annealed"], "BOX_1XXX"),
    (data_other, "Group Other", "Otras series", ["Annealed", "Normalized", "Quenched and tempered"], "BOX_Otras_Series")
]

colors = ["#4C78A8", "#F58518", "#54A24B"]

# ==========================================
# 7. GENERAR BOXPLOTS
# ==========================================

for data, group_column, analysis_name, group_order, filename_prefix in group_configs:

    for prop in properties:

        plot_data = [
            data.loc[data[group_column] == group, prop].dropna().values
            for group in group_order
        ]

        valid_groups = [
            (group, values)
            for group, values in zip(group_order, plot_data)
            if len(values) > 0
        ]

        labels = [group for group, values in valid_groups]
        values = [values for group, values in valid_groups]

        fig, ax = plt.subplots(figsize=(9, 6))

        bp = ax.boxplot(
            values,
            tick_labels=labels,
            patch_artist=True,
            showmeans=True,
            meanline=False,
            showfliers=True
        )

        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.65)

        # Mostrar observaciones individuales con jitter
        rng = np.random.default_rng(42)

        for i, group_values in enumerate(values, start=1):
            jitter = rng.uniform(-0.08, 0.08, size=len(group_values))
            ax.scatter(i + jitter, group_values, alpha=0.45, s=22, color="black")

        ax.set_title(f"{analysis_name}: {prop}", fontsize=14)
        ax.set_xlabel("Condición de procesamiento")
        ax.set_ylabel(prop)
        ax.grid(axis="y", alpha=0.25)

        plt.xticks(rotation=15, ha="right")
        plt.tight_layout()

        safe_property = prop.replace(" ", "_").replace("(", "").replace(")", "").replace("%", "pct")

        plt.savefig(boxplot_dir / f"{filename_prefix}_{safe_property}.png", dpi=300, bbox_inches="tight")
        plt.show()
        plt.close(fig)

# ==========================================
# 8. EXPORTAR RESUMEN DESCRIPTIVO
# ==========================================

summary_results = []

for data, group_column, analysis_name, group_order, filename_prefix in group_configs:

    for prop in properties:

        for group in group_order:

            values = data.loc[data[group_column] == group, prop].dropna()

            if len(values) == 0:
                continue

            summary_results.append({
                "Analysis": analysis_name,
                "Property": prop,
                "Group": group,
                "n": len(values),
                "Mean": values.mean(),
                "Median": values.median(),
                "SD": values.std(),
                "Q1": values.quantile(0.25),
                "Q3": values.quantile(0.75),
                "Minimum": values.min(),
                "Maximum": values.max()
            })

summary_df = pd.DataFrame(summary_results)

summary_df.to_csv(output_dir / "Resumen_Descriptivo_ANOVA.csv", index=False)

print("\nRESUMEN DESCRIPTIVO")
print(summary_df.to_string(index=False))

print("\nANÁLISIS COMPLETADO")
print(f"Resultados guardados en: {output_dir.resolve()}")
