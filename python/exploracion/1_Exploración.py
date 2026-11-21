import pandas as pd

dataset = pd.read_csv("Steel- Property and Composition (Carbon Steel).csv")

# Análisis preliminar
print(f"Dataset size: {dataset.shape[0]} x {dataset.shape[1]}")

for column in dataset.columns:
    print(f"\nColumn: {column}")
    print(f"Data type: {dataset[column].dtype}")

    if pd.api.types.is_numeric_dtype(dataset[column]):
        print(f"Range: [{dataset[column].min()}, {dataset[column].max()}]")
    else:
        print(f"Unique values: {dataset[column].dropna().unique().tolist()}")

    missing = dataset[column].isna().sum()
    total = len(dataset[column])
    print(f"Missing values: {missing}/{total} ({missing / total:.2%})")

# Primera limpiada
cleansed_dataset = dataset.copy()
cleansed_dataset["SAE Grade"] = cleansed_dataset["SAE Grade"].str.replace(r"\D", "", regex=True).astype(int)
cleansed_dataset["Reduction (%)"] = cleansed_dataset["Reduction (%)"].str.replace(",", ".", regex=False).astype(float)
cleansed_dataset["Hardness (HB)"] = cleansed_dataset["Hardness (HB)"].str.extract(r"(\d+)", expand=False).astype(int)
cleansed_dataset["Mn Avg (%)"] = (cleansed_dataset["Mn (Min)"] + cleansed_dataset["Mn (Max)"]) /2
columns_to_drop = ["UTS (Ksi)", "YS (ksi)", "P (Min)", "S (Min)", "C (Min)", "C (Max)", "Mn (Min)", "Mn (Max)", "Si (Min)", "Si (Max)", "Ni (Min)", "Ni (Max)", "Cr (Min)", "Cr (Max)", "Mo (Min)", "Mo (Max)", "Ti (Min)", "Ti (Max)"]
cleansed_dataset = cleansed_dataset.drop(columns=columns_to_drop)
cleansed_dataset["C (%)"] = cleansed_dataset["SAE Grade"].astype(str).str[-2:].astype(int) / 100
cleansed_dataset = cleansed_dataset.reset_index(drop=True)
print(f"Percentage kept: {round(cleansed_dataset.shape[0]/dataset.shape[0],4)}")
cleansed_dataset.info()
cleansed_dataset.to_csv("Cleansed_Carbon_Steel.csv", index=False)
