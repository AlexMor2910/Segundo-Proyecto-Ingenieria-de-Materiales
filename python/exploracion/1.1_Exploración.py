import pandas as pd
import re

dataset = pd.read_csv("Cleansed_Carbon_Steel.csv")

# Análisis preliminar
print(f"Dataset size: {dataset.shape[0]} x {dataset.shape[1]}")
for column in dataset.columns:
    print(f"\nColumn: {column}")
    print(f"Data type: {dataset[column].dtype}")

    if pd.api.types.is_numeric_dtype(dataset[column]):
        print(f"Range: [{dataset[column].min()}, {dataset[column].max()}]")
    else:
        print(f"Unique values: {dataset[column].dropna().unique().tolist()}")


def separate_conditions(condition):
    condition = str(condition).lower().strip()
    condition = condition.replace("\n", " ")
    condition = condition.replace("cold orawn", "cold drawn")
    condition = condition.replace("hot rotted", "hot rolled")
    condition = condition.replace("oi i quenched", "oil quenched")

    heat_treatment = None
    temperature = None
    other_conditions = None

    if "normalized" in condition:
        heat_treatment = "Normalized"
    elif "annealed" in condition:
        heat_treatment = "Annealed"
    elif "quenched" in condition:
        heat_treatment = "Quenched"

    temperatures = re.findall(r"(\d+(?:\.\d+)?)\s*°C", condition, flags=re.IGNORECASE)
    temperatures = [float(t) + 273.15 for t in temperatures]

    if temperatures and heat_treatment:
        temperature = temperatures[0]

    characteristics = []
    if "hot rolled" in condition:
        characteristics.append("Hot rolled")
    if "cold drawn" in condition:
        characteristics.append("Cold drawn")
    if "spheroidized" in condition:
        characteristics.append("Spheroidized")
    if "water quenched" in condition:
        characteristics.append("Water quenched")
    if "oil quenched" in condition:
        characteristics.append("Oil quenched")
    if "tempered" in condition:
        if len(temperatures) > 1:
            characteristics.append(f"Tempered at {temperatures[1]:.2f} K")
        else:
            characteristics.append("Tempered")
    if characteristics:
        other_conditions = ", ".join(characteristics)

    return pd.Series([heat_treatment, temperature, other_conditions])


dataset[["Heat Treatment", "Temperature (K)", "Other Conditions"]] = dataset["Conditions"].apply(separate_conditions)
dataset = dataset.drop(columns=["Conditions"])
dataset.to_csv("Cleansed_Treatment_Carbon_Steel.csv", index=False)
