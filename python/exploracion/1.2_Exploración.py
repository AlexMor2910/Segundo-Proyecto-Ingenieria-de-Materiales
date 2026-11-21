import pandas as pd
import re

dataset = pd.read_csv("Cleansed_Carbon_Steel.csv")


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
        heat_treatment = "Quenched and tempered"
    temperatures = re.findall(r"(\d+(?:\.\d+)?)\s*°C", condition, flags=re.IGNORECASE)

    if temperatures and heat_treatment:
        temperature = round(float(temperatures[0]) + 273.15, 2)

    characteristics = []
    if "hot rolled" in condition:
        characteristics.append("Hot rolled")
    if "cold drawn" in condition:
        characteristics.append("Cold drawn")
    if characteristics:
        other_conditions = ", ".join(characteristics)

    return pd.Series([heat_treatment, temperature, other_conditions])


dataset[["Heat Treatment", "Temperature (K)", "Mechanical Conditions"]] = dataset["Conditions"].apply(separate_conditions)
dataset = dataset.drop(columns=["Conditions"])
dataset.to_csv("Cleansed_Treatment_Carbon_Steel_Summary.csv", index=False)
