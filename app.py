import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

# ✅ Configuration de la page
st.set_page_config(page_title="Analyse TPE", layout="wide")

# ✅ Titre
st.title("📈 Analyse de Données pour Petites Entreprises")

# ✅ Intro + bouton pour télécharger un exemple
st.markdown("**💡 Vous n'avez pas encore de fichier ?** Téléchargez un exemple pour tester l'application :")

with open("donnees_exemple.csv", "rb") as f:
    st.download_button(
        label="📥 Télécharger un exemple de fichier",
        data=f,
        file_name="donnees_exemple.csv",
        mime="text/csv"
    )

st.markdown("---")

# ✅ Upload de fichier CSV
uploaded_file = st.file_uploader("📁 Importer un fichier CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Données chargées avec succès")

    # ✅ Filtres
    st.subheader("📌 Filtres")
    produits = st.multiselect("🧃 Filtrer par produit :", options=df["Produit"].unique() if "Produit" in df.columns else [])
    canal = st.multiselect("🌐 Filtrer par canal :", options=df["Canal"].unique() if "Canal" in df.columns else [])

    if produits:
        df = df[df["Produit"].isin(produits)]
    if canal:
        df = df[df["Canal"].isin(canal)]

    st.markdown("---")

    # ✅ Aperçu
    st.subheader("📄 Aperçu des données")
    st.dataframe(df.head())

    st.markdown("---")

    # ✅ KPI
    st.subheader("📌 Indicateurs Clés")
    col1, col2, col3 = st.columns(3)
    try:
        col1.metric("💰 Total des ventes", f"{df['Total (€)'].sum():.2f} €")
        col2.metric("🛒 Nb de transactions", f"{len(df)}")
        col3.metric("📊 Panier moyen", f"{df['Total (€)'].mean():.2f} €")
    except:
        st.warning("⚠️ Les colonnes nécessaires pour les KPI n'existent pas ou sont mal nommées.")

    st.markdown("---")

    # ✅ Statistiques générales
    st.subheader("📊 Statistiques générales")
    st.write(df.describe())

    st.markdown("---")

    # ✅ Histogramme interactif
    num_cols = df.select_dtypes(include='number').columns.tolist()
    if num_cols:
        st.subheader("📈 Distribution d'une colonne numérique")
        col = st.selectbox("Choisissez une colonne :", num_cols)
        fig, ax = plt.subplots()
        df[col].hist(bins=20, ax=ax)
        ax.set_title(f"Distribution de {col}")
        st.pyplot(fig)

    st.markdown("---")

    # ✅ Ventes par produit
    if "Produit" in df.columns and "Total (€)" in df.columns:
        st.subheader("📦 Ventes totales par produit")
        df_grouped = df.groupby("Produit")["Total (€)"].sum().sort_values(ascending=False)
        st.bar_chart(df_grouped)

    st.markdown("---")

    # ✅ Export des données filtrées
    st.subheader("📤 Exporter les résultats filtrés")
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Télécharger les données filtrées",
        data=csv_buffer.getvalue(),
        file_name="donnees_filtrees.csv",
        mime="text/csv"
    )

else:
    st.info("📁 Veuillez importer un fichier CSV pour commencer.")
