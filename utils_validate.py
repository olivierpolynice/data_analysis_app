# utils_validate.py
import pandas as pd

REQUIRED = ["Date", "Produit", "Quantité", "Prix unitaire (€)", "Total (€)", "Canal"]

def clean_and_validate(df: pd.DataFrame):
    """
    - Vérifie colonnes requises
    - Convertit les types
    - Filtre lignes invalides (NaN)
    - Signale valeurs négatives
    """
    issues = []
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        issues.append(f"Colonnes manquantes : {', '.join(missing)}")
        return df, issues

    # Types
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for c in ["Quantité", "Prix unitaire (€)", "Total (€)"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Lignes invalides (NaN)
    key_cols = ["Date", "Quantité", "Prix unitaire (€)", "Total (€)"]
    bad = df[df[key_cols].isna().any(axis=1)]
    if len(bad) > 0:
        issues.append(f"{len(bad)} lignes invalides supprimées (dates/nombres manquants).")
        df = df.drop(bad.index)

    # Valeurs négatives
    neg = df[(df["Quantité"] < 0) | (df["Prix unitaire (€)"] < 0) | (df["Total (€)"] < 0)]
    if len(neg) > 0:
        issues.append(f"{len(neg)} lignes avec valeurs négatives détectées (à vérifier).")

    return df, issues
