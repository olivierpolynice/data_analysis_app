import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ✅ Configuration de la page
st.set_page_config(page_title="Analyse", layout="wide")
st.title("📈 Analyse des Données d’Entreprise")

# ✅ Chargement du fichier CSV
try:
    df = pd.read_csv("donnees_entreprise.csv")
    st.success("✅ Données chargées avec succès depuis 'donnees_entreprise.csv'")
except FileNotFoundError:
    st.error("❌ Le fichier 'donnees_entreprise.csv' est introuvable.")
    st.stop()

# ✅ Conversion de la colonne Date
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

# --- 🔍 FILTRES DYNAMIQUES ---
st.sidebar.header("🎛️ Filtres")

# 1. Filtre par date
if "Date" in df.columns:
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    date_range = st.sidebar.date_input("📅 Plage de dates", [min_date, max_date], min_value=min_date, max_value=max_date)
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

# 2. Filtre par produit
if "Produit" in df.columns:
    produits = df["Produit"].dropna().unique().tolist()
    selected_produits = st.sidebar.multiselect("🧃 Produits", options=produits, default=produits)
    df = df[df["Produit"].isin(selected_produits)]

# 3. Filtre par canal
if "Canal" in df.columns:
    canaux = df["Canal"].dropna().unique().tolist()
    selected_canaux = st.sidebar.multiselect("🌐 Canal de vente", options=canaux, default=canaux)
    df = df[df["Canal"].isin(selected_canaux)]

st.markdown("---")

# ✅ KPI
st.subheader("📌 Indicateurs Clés")
col1, col2, col3 = st.columns(3)
col1.metric("💰 Total des ventes", f"{df['Total (€)'].sum():,.2f} €")
col2.metric("🛒 Nombre de ventes", f"{len(df)}")
col3.metric("📊 Panier moyen", f"{df['Total (€)'].mean():,.2f} €")

st.markdown("---")

# ✅ Graphique : Top produits
st.subheader("📦 Ventes totales par produit")
if "Produit" in df.columns and "Total (€)" in df.columns:
    top_produits = df.groupby("Produit")["Total (€)"].sum().sort_values(ascending=False)
    st.bar_chart(top_produits)
else:
    st.warning("Colonnes 'Produit' et 'Total (€)' nécessaires.")

st.markdown("---")

# ✅ Courbe : Évolution des ventes
st.subheader("📈 Évolution des ventes dans le temps")
if "Date" in df.columns and "Total (€)" in df.columns:
    df_by_date = df.groupby("Date")["Total (€)"].sum().reset_index().sort_values("Date")
    st.line_chart(df_by_date.set_index("Date"))
else:
    st.warning("Colonnes 'Date' et 'Total (€)' nécessaires.")

st.markdown("---")

# ✅ Camembert : Répartition par canal
st.subheader("🧩 Répartition par canal")
if "Canal" in df.columns and "Total (€)" in df.columns:
    df_canaux = df.groupby("Canal")["Total (€)"].sum()
    fig, ax = plt.subplots()
    ax.pie(df_canaux, labels=df_canaux.index, autopct='%1.1f%%', startangle=90)
    ax.axis("equal")
    st.pyplot(fig)
else:
    st.warning("Colonnes 'Canal' et 'Total (€)' nécessaires.")

st.markdown("---")

# ✅ Tableau des données
st.subheader("📄 Aperçu des données")
st.dataframe(df.head())

st.markdown("---")

# ✅ Statistiques générales
st.subheader("📊 Statistiques générales")
st.write(df.describe())

st.markdown("---")

# ✅ Histogramme interactif
st.subheader("📈 Distribution d'une colonne numérique")
num_cols = df.select_dtypes(include='number').columns.tolist()
if num_cols:
    col = st.selectbox("📌 Choisissez une colonne :", num_cols)
    try:
        fig, ax = plt.subplots()
        df[col].hist(bins=15, ax=ax)
        ax.set_title(f"Distribution de {col}")
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Erreur dans l'affichage de l'histogramme : {e}")
else:
    st.info("Aucune colonne numérique à afficher.")
