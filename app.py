import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# CONFIGURATION DE LA PAGE
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Indicateur Socio-Économique",
    page_icon="📊",
    layout="wide"
)

# ─────────────────────────────────────────────
# DONNÉES : DIMENSIONS ET VARIABLES (LISS)
# ─────────────────────────────────────────────
DIMENSIONS = {
    "Revenu": {
        "Revenu médian":         {"min": 8000,  "max": 35000, "valeur": 20000},
        "Taux de pauvreté (%)":  {"min": 5,     "max": 45,    "valeur": 18},
        "Part bas revenus (%)":  {"min": 5,     "max": 40,    "valeur": 20},
    },
    "Éducation": {
        "Diplômés du supérieur (%)": {"min": 5,  "max": 60, "valeur": 25},
        "Sans diplôme (%)":          {"min": 5,  "max": 50, "valeur": 30},
        "Taux de scolarisation (%)": {"min": 50, "max": 99, "valeur": 80},
    },
    "Emploi": {
        "Taux de chômage (%)":      {"min": 2,  "max": 30, "valeur": 12},
        "Part contrats précaires (%)": {"min": 5, "max": 40, "valeur": 20},
        "Taux d'activité (%)":      {"min": 40, "max": 80, "valeur": 60},
    },
    "Logement": {
        "Suroccupation (%)":          {"min": 1,  "max": 25, "valeur": 10},
        "Part logements sociaux (%)": {"min": 0,  "max": 60, "valeur": 20},
        "Résidences sans confort (%)":{"min": 0,  "max": 20, "valeur": 5},
    },
    "Santé": {
        "Densité médecins (pour 10k hab)": {"min": 1, "max": 30, "valeur": 10},
        "Espérance de vie (ans)":          {"min": 70, "max": 86, "valeur": 79},
    },
    "Services": {
        "Accès commerces (min)":   {"min": 1,  "max": 30, "valeur": 10},
        "Accès école (min)":       {"min": 1,  "max": 25, "valeur": 8},
        "Accès transports (min)":  {"min": 1,  "max": 40, "valeur": 15},
    },
    "Participation": {
        "Taux inscription électorale (%)": {"min": 50, "max": 99, "valeur": 75},
        "Taux de participation (%)":       {"min": 20, "max": 85, "valeur": 55},
    },
}

# ─────────────────────────────────────────────
# NORMALISATION (min-max, sens positif)
# ─────────────────────────────────────────────
VARIABLES_INVERSES = {
    "Taux de pauvreté (%)",
    "Part bas revenus (%)",
    "Sans diplôme (%)",
    "Taux de chômage (%)",
    "Part contrats précaires (%)",
    "Suroccupation (%)",
    "Résidences sans confort (%)",
    "Accès commerces (min)",
    "Accès école (min)",
    "Accès transports (min)",
}

def normaliser(label, valeur, vmin, vmax):
    if vmax == vmin:
        return 0.5
    n = (valeur - vmin) / (vmax - vmin)
    if label in VARIABLES_INVERSES:
        n = 1 - n
    return round(np.clip(n, 0, 1), 3)

# ─────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────
st.title("📊 Constructeur d'indicateur socio-économique")
st.caption("Inspiré des travaux de Jean Gadrey & Florence Jany-Catrice · Données INSEE")

st.markdown("---")

# ── ÉTAPE 1 : Choix des dimensions
st.header("① Choisir les dimensions")

cols = st.columns(4)
dims_choisies = []
for i, dim in enumerate(DIMENSIONS.keys()):
    with cols[i % 4]:
        if st.checkbox(dim, value=True):
            dims_choisies.append(dim)

if not dims_choisies:
    st.warning("Sélectionne au moins une dimension.")
    st.stop()

st.markdown("---")

# ── ÉTAPE 2 : Choix des variables et valeurs
st.header("② Ajuster les valeurs des variables")

variables_actives = {}

for dim in dims_choisies:
    with st.expander(f"📂 {dim}", expanded=True):
        cols2 = st.columns(2)
        for j, (var, meta) in enumerate(DIMENSIONS[dim].items()):
            with cols2[j % 2]:
                val = st.slider(
                    label=var,
                    min_value=float(meta["min"]),
                    max_value=float(meta["max"]),
                    value=float(meta["valeur"]),
                    step=0.1,
                    key=f"{dim}_{var}"
                )
                variables_actives[var] = {
                    "dimension": dim,
                    "valeur": val,
                    "min": meta["min"],
                    "max": meta["max"],
                }

st.markdown("---")

# ── ÉTAPE 3 : Pondérations
st.header("③ Pondérer les dimensions")

poids_dims = {}
cols3 = st.columns(len(dims_choisies))
for i, dim in enumerate(dims_choisies):
    with cols3[i]:
        poids_dims[dim] = st.slider(
            f"{dim}",
            min_value=0,
            max_value=5,
            value=3,
            key=f"poids_{dim}"
        )

st.markdown("---")

# ── CALCUL
st.header("④ Résultats")

# Normalisation des variables
rows = []
for var, meta in variables_actives.items():
    norm = normaliser(var, meta["valeur"], meta["min"], meta["max"])
    rows.append({
        "Dimension": meta["dimension"],
        "Variable": var,
        "Valeur": meta["valeur"],
        "Score normalisé": norm,
        "Poids dimension": poids_dims[meta["dimension"]]
    })

df = pd.DataFrame(rows)

# Score par dimension
scores_dims = {}
for dim in dims_choisies:
    subset = df[df["Dimension"] == dim]
    if not subset.empty:
        scores_dims[dim] = round(subset["Score normalisé"].mean(), 3)

# Score global pondéré
total_poids = sum(poids_dims[d] for d in dims_choisies if poids_dims[d] > 0)
if total_poids == 0:
    st.warning("Augmente les pondérations pour calculer un score.")
    st.stop()

score_global = sum(
    scores_dims[d] * poids_dims[d]
    for d in dims_choisies
    if poids_dims[d] > 0
) / total_poids

# ── AFFICHAGE DU SCORE GLOBAL
col_score, col_jauge = st.columns([1, 2])

with col_score:
    couleur = (
        "#2ecc71" if score_global >= 0.66
        else "#e67e22" if score_global >= 0.33
        else "#e74c3c"
    )
    st.markdown(
        f"""
        <div style="
            background:{couleur};
            border-radius:16px;
            padding:30px;
            text-align:center;
            color:white;
        ">
            <div style="font-size:18px;">Score global</div>
            <div style="font-size:64px;font-weight:bold;">
                {round(score_global * 100, 1)}
            </div>
            <div style="font-size:16px;">/ 100</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_jauge:
    fig_jauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(score_global * 100, 1),
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": couleur},
            "steps": [
                {"range": [0, 33],  "color": "#fadbd8"},
                {"range": [33, 66], "color": "#fdebd0"},
                {"range": [66, 100],"color": "#d5f5e3"},
            ]
        },
        title={"text": "Indice synthétique"}
    ))
    fig_jauge.update_layout(height=280, margin=dict(t=40, b=0))
    st.plotly_chart(fig_jauge, use_container_width=True)

st.markdown("---")

# ── RADAR PAR DIMENSION
col_radar, col_bar = st.columns(2)

with col_radar:
    st.subheader("Radar des dimensions")
    labels = list(scores_dims.keys())
    values = list(scores_dims.values())
    values_closed = values + [values[0]]
    labels_closed = labels + [labels[0]]

    fig_radar = go.Figure(go.Scatterpolar(
        r=values_closed,
        theta=labels_closed,
        fill="toself",
        fillcolor="rgba(53,162,235,0.3)",
        line=dict(color="rgba(53,162,235,0.9)")
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col_bar:
    st.subheader("Score par dimension")
    df_dims = pd.DataFrame({
        "Dimension": list(scores_dims.keys()),
        "Score": [v * 100 for v in scores_dims.values()]
    }).sort_values("Score", ascending=True)

    fig_bar = go.Figure(go.Bar(
        x=df_dims["Score"],
        y=df_dims["Dimension"],
        orientation="h",
        marker_color="rgba(53,162,235,0.7)"
    ))
    fig_bar.update_layout(
        xaxis=dict(range=[0, 100]),
        height=400,
        margin=dict(l=10, r=10)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ── TABLEAU DÉTAILLÉ
st.subheader("Détail des variables")
df_display = df[["Dimension", "Variable", "Valeur", "Score normalisé"]].copy()
df_display["Score normalisé"] = (df_display["Score normalisé"] * 100).round(1)
df_display.columns = ["Dimension", "Variable", "Valeur saisie", "Score (0-100)"]
st.dataframe(df_display, use_container_width=True, hide_index=True)

st.markdown("---")

# ── EXPORT CSV
st.subheader("Exporter les résultats")
csv = df_display.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Télécharger les résultats (CSV)",
    data=csv,
    file_name="indicateur_socioeconomique.csv",
    mime="text/csv"
)

st.caption("Source : données inspirées INSEE · Gadrey & Jany-Catrice · LISS")
