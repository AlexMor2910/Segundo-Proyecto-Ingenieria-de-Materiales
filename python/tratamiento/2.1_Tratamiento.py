import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr, linregress

dataset = pd.read_csv("Cleansed_Treatment_Carbon_Steel_Summary_Fixed.csv")
carbon = "C (%)"
properties = ["UTS (MPa)", "YS (MPa)", "Hardness (HB)", "Elongation (%)"]

results = []

for prop in properties:
    x = dataset[carbon]
    y = dataset[prop]

    pearson = pearsonr(x, y)
    spearman = spearmanr(x, y)
    regression = linregress(x, y)

    results.append({
        "Property": prop,
        "n": len(dataset[[carbon, prop]].dropna()),
        "Pearson r": pearson.statistic,
        "Pearson p": pearson.pvalue,
        "Pearson CI 95%": pearson.confidence_interval(),
        "Spearman rho": spearman.statistic,
        "Spearman p": spearman.pvalue,
        "Slope": regression.slope,
        "Intercept": regression.intercept,
        "R2": regression.rvalue**2
    })

results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

for prop in properties:
    x = dataset[carbon]
    y = dataset[prop]
    regression = linregress(x, y)

    plt.figure(figsize=(8, 5))
    plt.scatter(x, y, alpha=0.65)
    plt.plot(x, regression.intercept + regression.slope*x)
    plt.xlabel("Carbono nominal C (%)")
    plt.ylabel(prop)
    plt.title(f"Carbono vs. {prop}")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.show()
