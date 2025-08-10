# pages/02_Tableau de bord.py
import streamlit as st
import pandas as pd
import plotly.express as px

from utils_io import read_table
from utils_validate import clean_and_validate
from utils_forecast import forecast_baseline
from utils_export import fig_to_png, fig_to_pdf, export_zip

st.set_page_config(page_title="Tableau de bord", page_icon="📊", layout="wide")

def example_df():
    return pd.DataFrame({
        "Date": pd.to_datetime(
            ["2024-06-01","2024-06-03","2024-06-05","2024-06-07","2024-06-10",
             "2024-06-12","2024-06-15","2024-06-18","2024-06-21","2024-06-25"]),
        "Produit": ["Produit A","Produit B","Produit A","Produit C","Produit B",
                    "Produit A","Produit B","Produit C","Produit A","Produit B"],
        "Quantité": [2,1,3,5,2,4,6,2,1,3],
        "Prix unitaire (€)": [15,40,15,8,40,15,40,20,15,40],
        "Canal": ["Magasin","Site Web","Magasin","Marché","Site Web",
                  "Magasin","Site Web","Marché","Site Web","Site Web"]
    }).assign(**{"Total (€)": lambda d: d["Quantité"] * d["Prix unitaire (€)"]})

def compute_kpis(df):
    total = df["Total (€)"].sum() if "Total (€)" in df else 0
    n = len(df)
    panier = (total / n) if n else 0
    return total, n, panier

st.header("📊 Tableau de bord")

left, right = st.columns([1, 1], gap="large")
with left:
    st.subheader("Importer des données")
    uploaded = st.file_uploader("CSV/Excel (.csv, .xlsx)", type=["csv","xlsx","xls"])
    if uploaded:
        df_raw = read_table(uploaded)
    else:
        st.info("Aucun fichier chargé — utilisation d’un **jeu d’exemple**.")
        df_raw = example_df()
    df, issues = clean_and_validate(df_raw)
    for msg in issues:
        st.warning(msg)

with right:
    st.subheader("Filtres")
    date_range = None
    if "Date" in df.columns and not df.empty:
        dmin, dmax = df["Date"].min(), df["Date"].max()
        date_range = st.date_input("Période", value=(dmin, dmax))
    produits = st.multiselect("Produit", sorted(df["Produit"].dropna().unique()) if "Produit" in df else [])
    canaux = st.multiselect("Canal", sorted(df["Canal"].dropna().unique()) if "Canal" in df else [])

# Appliquer filtres
df_f = df.copy()
if date_range and "Date" in df_f.columns and not df_f.empty:
    s, e = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    df_f = df_f[(df_f["Date"] >= s) & (df_f["Date"] <= e)]
if produits and "Produit" in df_f.columns:
    df_f = df_f[df_f["Produit"].isin(produits)]
if canaux and "Canal" in df_f.columns:
    df_f = df_f[df_f["Canal"].isin(canaux)]

st.markdown("### 🗂️ Aperçu")
st.dataframe(df_f.head(200), use_container_width=True)

st.markdown("### 📌 Indicateurs clés")
k1, k2, k3 = st.columns(3)
total, n, panier = compute_kpis(df_f)
k1.metric("💰 Total des ventes", f"{total:,.2f} €".replace(",", " "))
k2.metric("🧾 Nb de transactions", f"{n}")
k3.metric("🛒 Panier moyen", f"{panier:,.2f} €".replace(",", " "))

st.markdown("### 📈 Visualisations")
figs = {}

if {"Produit","Total (€)"}.issubset(df_f.columns) and not df_f.empty:
    by_prod = df_f.groupby("Produit", as_index=False)["Total (€)"].sum().sort_values("Total (€)", ascending=False)
    fig1 = px.bar(by_prod, x="Produit", y="Total (€)", title="Ventes par produit")
    st.plotly_chart(fig1, use_container_width=True)
    figs["ventes_par_produit"] = fig1

if {"Canal","Total (€)"}.issubset(df_f.columns) and not df_f.empty and df_f["Canal"].nunique() > 0:
    by_ch = df_f.groupby("Canal", as_index=False)["Total (€)"].sum()
    fig2 = px.pie(by_ch, names="Canal", values="Total (€)", title="Répartition par canal", hole=0.3)
    st.plotly_chart(fig2, use_container_width=True)
    figs["ventes_par_canal"] = fig2

if {"Date","Total (€)"}.issubset(df_f.columns) and not df_f.empty:
    by_date = df_f.groupby("Date", as_index=False)["Total (€)"].sum()
    fig3 = px.line(by_date, x="Date", y="Total (€)", markers=True, title="Évolution des ventes (historique)")
    st.plotly_chart(fig3, use_container_width=True)
    figs["evolution_ventes"] = fig3

    # Prévision baseline
    daily, fc = forecast_baseline(df_f)
    if daily is not None and fc is not None:
        hist = daily.rename(columns={"Total (€)": "Ventes (€)"})
        fig4 = px.line(hist, x="Date", y="Ventes (€)", markers=True, title="Évolution & Prévision (baseline)")
        fig4.add_scatter(x=fc["Date"], y=fc["Prévision (€)"], mode="lines", name="Prévision (baseline)")
        st.plotly_chart(fig4, use_container_width=True)
        figs["evolution_prevision"] = fig4

st.markdown("### ⤵️ Exports")
# Export PNG/PDF pour le dernier graphe affiché (si tu veux des boutons par graphe, dupliques ces lignes)
if figs:
    last_name, last_fig = list(figs.items())[-1]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("⬇️ PNG du graphe courant", data=fig_to_png(last_fig), file_name=f"{last_name}.png", mime="image/png", use_container_width=True)
    with c2:
        st.download_button("⬇️ PDF du graphe courant", data=fig_to_pdf(last_fig), file_name=f"{last_name}.pdf", mime="application/pdf", use_container_width=True)

# ZIP complet (CSV filtré + tous les graphs + KPIs)
kpis_dict = {
    "Total ventes": f"{total:,.2f} €".replace(",", " "),
    "Nb transactions": n,
    "Panier moyen": f"{panier:,.2f} €".replace(",", " ")
}
zip_buf = export_zip(figs, df_f, kpis_dict)
st.download_button("🗂️ Télécharger le rapport (ZIP complet)", data=zip_buf.getvalue(),
                   file_name="rapport_analyse.zip", mime="application/zip", use_container_width=True)
