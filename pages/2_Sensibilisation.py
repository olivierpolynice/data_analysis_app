import streamlit as st

st.set_page_config(page_title="Sensibilisation", layout="wide")

st.title("🧠 Sensibilisation à l'Analyse de Données")
st.markdown("## Pourquoi les données sont-elles importantes pour les TPE ?")

st.write("""
Les données sont une mine d’or pour toute entreprise, même les plus petites. Bien utilisées, elles permettent de :
- Comprendre le comportement des clients
- Améliorer les performances commerciales
- Prendre des décisions stratégiques basées sur des faits
- Identifier les produits qui fonctionnent et ceux à revoir
- Optimiser les canaux de vente

> 📊 **Un bon tableau de bord = une meilleure décision.**
""")

# ✅ Image illustrative (optionnelle)
st.image("assets/info.png", use_column_width=True)

st.markdown("---")

# ✅ BONNES PRATIQUES
st.subheader("✅ Bonnes pratiques pour débuter avec la donnée")
st.markdown("""
- **Centraliser** toutes les ventes et contacts dans un seul fichier (CSV, Excel)
- **Mettre à jour régulièrement** les informations (dates, montants, produits)
- **Éviter les doublons** et les fautes de frappe dans les noms de produits
- **Analyser au moins 1 fois par mois** les chiffres clés (CA, top produits, canaux)

""")

# ✅ Quiz interactif
st.markdown("## 🧪 Petit Quiz pour tester vos connaissances")
question = st.radio("Pourquoi l’analyse de données est-elle utile ?", [
    "Pour compliquer la gestion",
    "Pour prendre des décisions basées sur des faits",
    "Parce que c’est tendance"
])

if st.button("💡 Vérifier ma réponse"):
    if question == "Pour prendre des décisions basées sur des faits":
        st.success("✅ Bonne réponse ! C’est la base de la data.")
    else:
        st.error("❌ Mauvaise réponse. L’analyse sert avant tout à prendre de meilleures décisions.")

