# utils_io.py
import pandas as pd

# Canonicalisation des noms de colonnes fréquents
CANON = {
    "date": "Date", "jour": "Date",
    "produit": "Produit", "article": "Produit", "product": "Produit",
    "quantite": "Quantité", "quantité": "Quantité", "qty": "Quantité", "qté": "Quantité",
    "prix": "Prix unitaire (€)", "prix_unitaire": "Prix unitaire (€)", "unit_price": "Prix unitaire (€)",
    "total": "Total (€)", "montant": "Total (€)", "revenue": "Total (€)", "chiffre d'affaires": "Total (€)",
    "canal": "Canal", "channel": "Canal", "source": "Canal",
}

def _canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    lower = {c: str(c).strip().lower() for c in df.columns}
    df.rename(columns={old: CANON.get(lower[old], old) for old in df.columns}, inplace=True)
    return df

def read_table(file) -> pd.DataFrame:
    """Lit CSV ou Excel, puis harmonise les noms de colonnes."""
    name = getattr(file, "name", "").lower()
    if name.endswith(".xlsx") or name.endswith(".xls"):
        df = pd.read_excel(file)
    else:
        df = pd.read_csv(file)
    return _canonicalize_columns(df)
