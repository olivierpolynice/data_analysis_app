# pages/99_À propos & Contact.py
import streamlit as st

st.set_page_config(page_title="À propos & Contact", page_icon="ℹ️", layout="centered")

st.title("ℹ️ À propos")

st.markdown("""
**Projet :** *Analyse de Données pour Petites Entreprises*  
**Auteur :** **Olivier Polynice**

**Objectif :** aider les TPE/PME à piloter leurs ventes via un outil simple :  
CSV → **KPIs** clairs → **visualisations interactives** → **exports**.

**Technologies :** Streamlit • Pandas • Plotly
""")

st.divider()
st.subheader("📬 Me contacter")
st.markdown("""
- 🌐 **Portfolio** : [olivierpolynice.netlify.app](https://olivierpolynice.netlify.app/)
- 🧑‍💻 **GitHub** : [github.com/olivierpolynice](https://github.com/olivierpolynice)
- ✉️ **Email** : [olivierpolynice5@gmail.com](mailto:olivierpolynice5@gmail.com)
- 💼 **LinkedIn** : [linkedin.com/in/olivier-polynice](https://www.linkedin.com/in/olivier-polynice/)
""")
st.divider()
st.caption("Merci d’avoir testé l’application ! N’hésitez pas à me contacter pour une démo.")
