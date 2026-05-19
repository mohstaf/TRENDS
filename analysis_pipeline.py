"""TRENDS analysis pipeline.

This script loads the harmonised weekly dataset, attaches year-specific province
populations, and writes four summary tables: validation_summary.csv,
annual_summary.csv, phase_summary.csv, and top_provinces.csv.

Usage:
    python analysis_pipeline.py --xlsx "TRENDS.xlsx" --outdir output
"""
import argparse
import os
import pandas as pd
import matplotlib as mpl

DISEASES = ["Dengue total", "Chikungunya", "HFMD"]
RATES    = ["Dengue rate per 100,000",
            "Chikungunya rate per 100,000",
            "HFMD rate per 100,000"]
TITLES   = {"Dengue total": "Dengue", "Chikungunya": "Chikungunya", "HFMD": "HFMD"}
PALETTE  = {"Dengue total": "#C8102E", "Chikungunya": "#1B4F8F", "HFMD": "#1F8A4C"}

mpl.rcParams.update({
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "bold",
    "axes.titlesize": 12,
    "axes.titlepad": 12,
    "axes.labelpad": 8,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": ":",
    "grid.linewidth": 0.6,
    "figure.constrained_layout.use": True,
    "figure.titlesize": 13,
    "figure.titleweight": "bold",
})


def load_weekly(xlsx_path, sheet="weekly data"):
    return pd.read_excel(xlsx_path, sheet_name=sheet, header=1,
                         parse_dates=["Week start", "Week end"])


def load_province(xlsx_path, sheet="province data"):
    return pd.read_excel(xlsx_path, sheet_name=sheet, header=1)


def attach_population(weekly, province):
    # melt the per-year population columns into one row per (P-code, Year)
    pop_cols = [c for c in province.columns if c.startswith("Population ")]
    long = (province[["P-code"] + pop_cols]
              .melt(id_vars=["P-code"], var_name="PopYear",
                    value_name="Population"))
    long["Year"] = long["PopYear"].str.replace("Population ", "").astype(int)
    long = long[["P-code", "Year", "Population"]]
    return weekly.merge(long, on=["P-code", "Year"], how="left")


def national_pop_by_year(df):
    # sum the per-province populations to get a national total per year
    return (df[["Year", "P-code", "Population"]].drop_duplicates()
              .groupby("Year")["Population"].sum().reset_index()
              .rename(columns={"Population": "National population"}))


def validation_summary(df):
    rows = []
    if "Country" in df.columns:
        countries = sorted(df["Country"].dropna().unique().tolist())
        rows.append(["Country/Countries", ", ".join(countries)])
    rows += [
        ["Province-week records",   len(df)],
        ["Provinces (distinct)",    df["Province"].nunique()],
        ["Epidemiological weeks",   df[["Year", "Epi week"]].drop_duplicates().shape[0]],
        ["Years covered",           f"{df['Year'].min()} to {df['Year'].max()}"],
        ["Total dengue cases",      int(df["Dengue total"].sum())],
        ["Total chikungunya cases", int(df["Chikungunya"].sum())],
        ["Total HFMD cases",        int(df["HFMD"].sum())],
    ]
    return pd.DataFrame(rows, columns=["Metric", "Value"])


def annual_summary(df):
    cases = df.groupby("Year")[DISEASES].sum().reset_index()
    return cases.merge(national_pop_by_year(df), on="Year")


def phase_summary(df):
    # three pandemic phases: pre-COVID 2016-2019, pandemic 2020-2022, post-acute 2023-2025
    phases = {y: ("Pre-COVID" if y <= 2019 else
                  "Pandemic"  if y <= 2022 else "Post-acute")
              for y in range(2016, 2026)}
    cases = df.groupby("Year")[DISEASES].sum().reset_index()
    nat = cases.merge(national_pop_by_year(df), on="Year")
    nat["phase"] = nat["Year"].map(phases)
    for d in DISEASES:
        nat[f"{d}_rate"] = nat[d] / nat["National population"] * 1e5
    means = nat.groupby("phase")[[f"{d}_rate" for d in DISEASES]].mean().round(1)
    means.columns = DISEASES
    ref = means.loc["Pre-COVID"]
    rows = []
    for ph in ["Pre-COVID", "Pandemic", "Post-acute"]:
        for d in DISEASES:
            rate = float(means.loc[ph, d])
            delta = (rate - ref[d]) / ref[d] * 100
            rows.append({"Disease": d, "Phase": ph,
                         "Mean annual rate per 100,000": rate,
                         "Percent change vs Pre-COVID":
                             "Reference" if ph == "Pre-COVID" else f"{delta:+.1f}%"})
    return pd.DataFrame(rows)


def top_provinces(df, n=10):
    rows = []
    for d in DISEASES:
        pop = df[["Province", "Year", "Population"]].drop_duplicates()
        cases = df.groupby(["Province", "Year"])[d].sum().reset_index()
        g = cases.merge(pop, on=["Province", "Year"])
        g["rate"] = g[d] / g["Population"] * 1e5
        rank = (g.groupby("Province")["rate"]
                  .mean().sort_values(ascending=False).head(n).round(1))
        for r, (prov, rate) in enumerate(rank.items(), start=1):
            rows.append({"Disease": d, "Rank": r, "Province": prov,
                         "Mean annual rate per 100,000": float(rate)})
    return pd.DataFrame(rows)


def main(xlsx_path, out_dir):
    weekly = load_weekly(xlsx_path)
    province = load_province(xlsx_path)
    df = attach_population(weekly, province)
    os.makedirs(out_dir, exist_ok=True)

    validation_summary(df).to_csv(os.path.join(out_dir, "validation_summary.csv"), index=False)
    annual_summary(df).to_csv(    os.path.join(out_dir, "annual_summary.csv"),     index=False)
    phase_summary(df).to_csv(     os.path.join(out_dir, "phase_summary.csv"),      index=False)
    top_provinces(df).to_csv(     os.path.join(out_dir, "top_provinces.csv"),      index=False)
    print(f"wrote 4 summary CSVs to {out_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx",   default="TRENDS.xlsx")
    parser.add_argument("--outdir", default="output")
    args = parser.parse_args()
    main(args.xlsx, args.outdir)