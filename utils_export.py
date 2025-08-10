# utils_export.py
import io
import zipfile

def fig_to_png(fig, scale: int = 2) -> bytes:
    return fig.to_image(format="png", scale=scale)  # nécessite kaleido

def fig_to_pdf(fig) -> bytes:
    return fig.to_image(format="pdf")

def export_zip(figs: dict, df_export, kpis: dict) -> io.BytesIO:
    """
    figs: dict { "nom_graph": plotly_fig, ... }
    df_export: DataFrame à exporter en CSV
    kpis: dict {"Total ventes": "...", ...}
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        # CSV
        z.writestr("donnees_filtrees.csv", df_export.to_csv(index=False).encode("utf-8"))
        # Graphs PNG
        for name, fig in figs.items():
            z.writestr(f"{name}.png", fig_to_png(fig, scale=2))
        # README KPIs
        z.writestr("README.txt", "\n".join([f"{k}: {v}" for k, v in kpis.items()]).encode("utf-8"))
    buf.seek(0)
    return buf
