# pages/01_Analyses avancées.py
import streamlit as st
import pandas as pd
import plotly.express as px
from dateutil.relativedelta import relativedelta

from utils_io import read_table
from utils_validate import clean_and_validate
from utils_export import fig_to_png, fig_to_pdf

st.set_page_config(page_title="Analyses avancées", page_icon="🧪", layout="wide")
st.header("🧪 Analyses avancées")

tab1, tab2 = st.tabs(["📂 Multi‑fichiers (A vs B)", "⏱️ Comparaison de périodes (1 fichier)"])

def _export_buttons(fig, basename):
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("⬇️ PNG", data=fig_to_png(fig), file_name=f"{basename}.png", mime="image/png", use_container_width=True)
    with c2:
        st.download_button("⬇️ PDF", data=fig_to_pdf(fig), file_name=f"{basename}.pdf", mime="application/pdf", use_container_width=True)

# --- Tab 1: Multi-fichiers ---
with tab1:
    st.subheader("Comparer deux fichiers (CSV/Excel)")
    files = st.file_uploader("Téléverser exactement 2 fichiers", type=["csv","xlsx","xls"], accept_multiple_files=True)
    if len(files) == 2:
        dfA_raw, dfB_raw = read_table(files[0]), read_table(files[1])
        dfA, issuesA = clean_and_validate(dfA_raw)
        dfB, issuesB = clean_and_validate(dfB_raw)
        for msg in issuesA + issuesB:
            st.warning(msg)

        la, lb = getattr(files[0], "name", "Dataset A"), getattr(files[1], "name", "Dataset B")

        needed = {"Date", "Total (€)"}
        if not needed.issubset(dfA.columns) or not needed.issubset(dfB.columns):
            st.error("Les fichiers doivent contenir au minimum `Date` et `Total (€)`.")
        else:
            # KPIs comparés
            def kpis(df):
                total = df["Total (€)"].sum() if "Total (€)" in df else 0
                n = len(df); panier = (total/n) if n else 0
                return total, n, panier

            c1, c2, c3 = st.columns(3)
            tA, nA, pA = kpis(dfA)
            tB, nB, pB = kpis(dfB)
            c1.metric(f"{la} — Total", f"{tA:,.2f} €".replace(",", " "))
            c2.metric(f"{lb} — Total", f"{tB:,.2f} €".replace(",", " "))
            c3.metric("Différence (B - A)", f"{(tB - tA):,.2f} €".replace(",", " "))

            # Évolution
            A = dfA.groupby("Date", as_index=False)["Total (€)"].sum().assign(Source=la)
            B = dfB.groupby("Date", as_index=False)["Total (€)"].sum().assign(Source=lb)
            combo = pd.concat([A, B], ignore_index=True)
            fig = px.line(combo, x="Date", y="Total (€)", color="Source", markers=True,
                          title="Évolution des ventes — A vs B")
            st.plotly_chart(fig, use_container_width=True)
            _export_buttons(fig, "comparaison_evolution_A_vs_B")

            # Par produit si dispo
            if {"Produit", "Total (€)"}.issubset(dfA.columns) and {"Produit", "Total (€)"}.issubset(dfB.columns):
                gA = dfA.groupby("Produit", as_index=False)["Total (€)"].sum().assign(Source=la)
                gB = dfB.groupby("Produit", as_index=False)["Total (€)"].sum().assign(Source=lb)
                gb = pd.concat([gA, gB], ignore_index=True)
                fig2 = px.bar(gb, x="Produit", y="Total (€)", color="Source", barmode="group",
                              title="Ventes par produit — A vs B")
                st.plotly_chart(fig2, use_container_width=True)
                _export_buttons(fig2, "comparaison_produits_A_vs_B")
    else:
        st.info("Charge **2 fichiers** pour activer la comparaison.")

# --- Tab 2: Comparaison de périodes ---
with tab2:
    st.subheader("Comparer deux périodes (un seul fichier CSV/Excel)")
    f = st.file_uploader("Fichier unique", type=["csv","xlsx","xls"], key="period_file")
    if f:
        df_raw = read_table(f)
        df, issues = clean_and_validate(df_raw)
        for msg in issues:
            st.warning(msg)

        if "Date" not in df or "Total (€)" not in df:
            st.error("Il faut les colonnes `Date` et `Total (€)`.")
        else:
            dmin, dmax = df["Date"].min(), df["Date"].max()
            st.caption(f"Période disponible : {dmin.date()} → {dmax.date()}")

            c1, c2 = st.columns(2)
            with c1:
                r1 = st.date_input("Période A", value=(dmin, dmin + relativedelta(days=14)))
            with c2:
                r2 = st.date_input("Période B", value=(dmax - relativedelta(days=14), dmax))

            def sub(df, r):
                s, e = pd.to_datetime(r[0]), pd.to_datetime(r[1])
                return df[(df["Date"] >= s) & (df["Date"] <= e)].copy()

            A = sub(df, r1).assign(Source="Période A")
            B = sub(df, r2).assign(Source="Période B")

            # KPIs
            def kpis(d):
                total = d["Total (€)"].sum() if "Total (€)" in d else 0
                n = len(d); panier = (total/n) if n else 0
                return total, n, panier
            tA, nA, pA = kpis(A); tB, nB, pB = kpis(B)
            c1, c2, c3 = st.columns(3)
            c1.metric("Total A", f"{tA:,.2f} €".replace(",", " "))
            c2.metric("Total B", f"{tB:,.2f} €".replace(",", " "))
            c3.metric("Différence B - A", f"{(tB - tA):,.2f} €".replace(",", " "))

            # Évolution
            gA = A.groupby("Date", as_index=False)["Total (€)"].sum()
            gB = B.groupby("Date", as_index=False)["Total (€)"].sum()
            gA["Source"] = "Période A"; gB["Source"] = "Période B"
            both = pd.concat([gA, gB], ignore_index=True)
            fig = px.line(both, x="Date", y="Total (€)", color="Source", markers=True,
                          title="Évolution des ventes — Période A vs B")
            st.plotly_chart(fig, use_container_width=True)
            _export_buttons(fig, "evolution_periodes_A_vs_B")

            # Produits
            if "Produit" in df.columns:
                pA = A.groupby("Produit", as_index=False)["Total (€)"].sum().assign(Source="Période A")
                pB = B.groupby("Produit", as_index=False)["Total (€)"].sum().assign(Source="Période B")
                pp = pd.concat([pA, pB], ignore_index=True)
                fig2 = px.bar(pp, x="Produit", y="Total (€)", color="Source", barmode="group",
                              title="Ventes par produit — Période A vs B")
                st.plotly_chart(fig2, use_container_width=True)
                _export_buttons(fig2, "produits_periodes_A_vs_B")
    else:
        st.info("Charge un **fichier** pour comparer deux plages de dates.")
