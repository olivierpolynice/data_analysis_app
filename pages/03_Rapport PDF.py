# pages/03_Rapport PDF.py
import io
import datetime as dt
import pandas as pd
import plotly.express as px
import streamlit as st

from utils_io import read_table
from utils_validate import clean_and_validate

# PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Rapport PDF", page_icon="🧾", layout="wide")
st.header("🧾 Rapport PDF – KPI & Graphiques")

def compute_kpis(df):
    total = df["Total (€)"].sum() if "Total (€)" in df else 0
    n = len(df)
    panier = (total / n) if n else 0
    return total, n, panier

# ---------- UI: import + filtres
left, right = st.columns([1,1], gap="large")
with left:
    st.subheader("Importer un fichier")
    uploaded = st.file_uploader("CSV/Excel (.csv, .xlsx)", type=["csv","xlsx","xls"])
    if uploaded:
        df_raw = read_table(uploaded)
    else:
        st.stop()

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

if df_f.empty:
    st.warning("Aucune donnée après filtrage.")
    st.stop()

st.markdown("### Aperçu")
st.dataframe(df_f.head(50), use_container_width=True)

# ---------- KPI
total, n, panier = compute_kpis(df_f)
st.markdown("### Indicateurs clés")
c1, c2, c3 = st.columns(3)
c1.metric("💰 Total des ventes", f"{total:,.2f} €".replace(",", " "))
c2.metric("🧾 Nb de transactions", f"{n}")
c3.metric("🛒 Panier moyen", f"{panier:,.2f} €".replace(",", " "))

# ---------- Graphiques Plotly (on garde les objets pour le PDF)
figs = []

if {"Produit","Total (€)"}.issubset(df_f.columns):
    by_prod = df_f.groupby("Produit", as_index=False)["Total (€)"].sum().sort_values("Total (€)", ascending=False)
    fig_prod = px.bar(by_prod, x="Produit", y="Total (€)", title="Ventes par produit")
    st.plotly_chart(fig_prod, use_container_width=True)
    figs.append(("ventes_par_produit", fig_prod))

if {"Canal","Total (€)"}.issubset(df_f.columns) and df_f["Canal"].nunique() > 0:
    by_ch = df_f.groupby("Canal", as_index=False)["Total (€)"].sum()
    fig_ch = px.pie(by_ch, names="Canal", values="Total (€)", title="Répartition par canal", hole=0.3)
    st.plotly_chart(fig_ch, use_container_width=True)
    figs.append(("ventes_par_canal", fig_ch))

if {"Date","Total (€)"}.issubset(df_f.columns):
    by_date = df_f.groupby("Date", as_index=False)["Total (€)"].sum()
    fig_dt = px.line(by_date, x="Date", y="Total (€)", markers=True, title="Évolution des ventes")
    st.plotly_chart(fig_dt, use_container_width=True)
    figs.append(("evolution_ventes", fig_dt))

st.markdown("### Générer le PDF")

def build_pdf(buffer: io.BytesIO, kpis, figs_png, meta):
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.2*cm)
    styles = getSampleStyleSheet()
    H1, H2, P = styles["Title"], styles["Heading2"], styles["BodyText"]

    story = []
    title = Paragraph("Rapport d’Analyse des Ventes", H1)
    story += [title, Spacer(1, 0.3*cm)]
    story += [Paragraph(f"Projet : Analyse de Données pour Petites Entreprises", P)]
    story += [Paragraph(f"Date : {meta['date']}", P)]
    story += [Paragraph(f"Période filtrée : {meta['periode']}", P)]
    if meta["produits"]:
        story += [Paragraph(f"Produits : {', '.join(meta['produits'])}", P)]
    if meta["canaux"]:
        story += [Paragraph(f"Canaux : {', '.join(meta['canaux'])}", P)]
    story += [Spacer(1, 0.5*cm)]

    story += [Paragraph("Indicateurs clés", H2)]
    t = Table([
        ["Total des ventes", "Nb de transactions", "Panier moyen"],
        [kpis["total"], kpis["nb"], kpis["panier"]],
    ])
    t.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.3, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,0), 6),
    ]))
    story += [t, Spacer(1, 0.6*cm)]

    for name, png in figs_png:
        story += [Paragraph(name.replace("_", " ").title(), H2), Spacer(1, 0.2*cm)]
        story += [Image(io.BytesIO(png), width=16*cm, height=9*cm), Spacer(1, 0.6*cm)]

    doc.build(story)
    buffer.seek(0)
    return buffer

# Convertir les figures en PNG (kaleido requis)
figs_png = []
for name, fig in figs:
    png = fig.to_image(format="png", scale=2)  # si erreur -> installer/maj 'kaleido'
    figs_png.append((name, png))

# Meta & KPI formatés
periode_txt = "-"
if date_range:
    periode_txt = f"{pd.to_datetime(date_range[0]).date()} → {pd.to_datetime(date_range[1]).date()}"
kpis_fmt = {
    "total": f"{total:,.2f} €".replace(",", " "),
    "nb": f"{n}",
    "panier": f"{panier:,.2f} €".replace(",", " "),
}
meta = {
    "date": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
    "periode": periode_txt,
    "produits": [str(x) for x in produits] if produits else [],
    "canaux": [str(x) for x in canaux] if canaux else [],
}

pdf_buf = io.BytesIO()
pdf_file = build_pdf(pdf_buf, kpis_fmt, figs_png, meta)

st.download_button(
    "⬇️ Télécharger le rapport PDF",
    data=pdf_file.getvalue(),
    file_name="rapport_analyse.pdf",
    mime="application/pdf",
    use_container_width=True
)
st.success("PDF généré avec succès ✅")
