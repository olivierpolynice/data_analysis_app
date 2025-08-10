# app.py
import streamlit as st

st.set_page_config(page_title="Analyse de Données – PME", page_icon="📈", layout="wide")

st.title("📊 Analyse de Données pour Petites Entreprises")
st.markdown("""
Bienvenue ! Cette application vous permet :
- d’**analyser** vos ventes (KPI, graphiques interactifs),
- de **comparer** deux périodes ou deux fichiers,
- d’**exporter** les graphiques en **PNG/PDF**,
- et de retrouver des infos dans **À propos & Contact**.

➡️ Utilisez le menu à gauche pour naviguer :
- **02_Tableau de bord** : analyse classique d’un fichier CSV
- **01_Analyses avancées** : multi-fichiers & comparaison de périodes
""")

st.info("Astuce : préparez vos CSV avec les colonnes `Date`, `Produit`, `Quantité`, `Prix unitaire (€)`, `Total (€)`, `Canal`.")
