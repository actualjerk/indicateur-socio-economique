import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# Prototype graphique : style "carte interactive Île-de-France"
# À intégrer progressivement dans ton app.py existant.
# Remplace le jeu de données ci-dessous par ton DataFrame final.
# ============================================================

st.set_page_config(
    page_title="ISS communal participatif — Île-de-France",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# CSS général
# -----------------------------
st.markdown(
    """
    <style>
    :root {
        --bg: #f5f3ee;
        --card: #ffffff;
        --ink: #172033;
        --muted: #667085;
        --blue: #243b63;
        --blue-soft: #e8eef8;
        --green: #2e7d61;
        --orange: #c97822;
        --red: #b93838;
        --border: #e4e7ec;
    }

    .stApp {
        background: linear-gradient(180deg, #f5f3ee 0%, #eef2f6 100%);
        color: var(--ink);
    }

    section[data-testid="stSidebar"] {
        background: #172033;
        color: white;
    }

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: white !important;
    }

    .main-title {
        padding: 1.2rem 1.4rem;
        background: linear-gradient(135deg, #172033 0%, #243b63 65%, #2e7d61 100%);
        color: white;
        border-radius: 26px;
        margin-bottom: 1rem;
        box-shadow: 0 14px 35px rgba(23, 32, 51, 0.22);
    }

    .main-title h1 {
        margin: 0;
        font-size: 2.15rem;
        line-height: 1.15;
        letter-spacing: -0.03em;
    }

    .main-title p {
        margin: .45rem 0 0 0;
        color: rgba(255,255,255,.86);
        font-size: 1.03rem;
    }

    .stepbar {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: .7rem;
        margin: 1rem 0 1.2rem 0;
    }

    .step {
        background: rgba(255,255,255,.78);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: .8rem .9rem;
        font-weight: 700;
        color: var(--blue);
        box-shadow: 0 8px 22px rgba(23, 32, 51, .06);
    }

    .step span {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 1.55rem;
        height: 1.55rem;
        margin-right: .35rem;
        border-radius: 999px;
        background: var(--blue-soft);
        color: var(--blue);
        font-size: .85rem;
    }

    .card {
        background: rgba(255,255,255,.86);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 12px 30px rgba(23, 32, 51, .08);
        margin-bottom: 1rem;
    }

    .card h3 {
        margin-top: 0;
        color: var(--blue);
        letter-spacing: -0.02em;
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 22px;
        padding: 1rem;
        min-height: 126px;
        box-shadow: 0 10px 24px rgba(23, 32, 51, .07);
    }

    .metric-label {
        color: var(--muted);
        font-size: .86rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .05em;
    }

    .metric-value {
        font-size: 2.1rem;
        font-weight: 800;
        color: var(--blue);
        line-height: 1.1;
        margin-top: .35rem;
    }

    .metric-comment {
        color: var(--muted);
        font-size: .92rem;
        margin-top: .3rem;
    }

    .alert-red {
        border-left: 7px solid var(--red);
        background: #fff4f4;
        color: #6f1d1d;
        padding: .9rem 1rem;
        border-radius: 18px;
        font-weight: 650;
    }

    .alert-orange {
        border-left: 7px solid var(--orange);
        background: #fff7ed;
        color: #733f12;
        padding: .9rem 1rem;
        border-radius: 18px;
        font-weight: 650;
    }

    .alert-green {
        border-left: 7px solid var(--green);
        background: #eefaf5;
        color: #18513d;
        padding: .9rem 1rem;
        border-radius: 18px;
        font-weight: 650;
    }

    .method-box {
        background: #f8fafc;
        border: 1px dashed #98a2b3;
        border-radius: 20px;
        padding: 1rem;
        color: #344054;
        font-size: .96rem;
    }

    div[data-testid="stMetric"] {
        background: white;
        padding: 1rem;
        border-radius: 20px;
        border: 1px solid var(--border);
        box-shadow: 0 8px 22px rgba(23, 32, 51, .06);
    }

    .stButton > button {
        border-radius: 999px;
        border: 0;
        background: #243b63;
        color: white;
        font-weight: 800;
        padding: .7rem 1rem;
    }

    .stButton > button:hover {
        background: #2e7d61;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Données de démonstration
# -----------------------------
# Les scores ci-dessous sont déjà normalisés sur 0-100 pour faciliter le prototype.
# Dans ton app réelle, tu remplaceras ces colonnes par les normalisations calculées.
communes_demo = pd.DataFrame(
    [
        {
            "commune": "Paris",
            "departement": "75",
            "lat": 48.8566,
            "lon": 2.3522,
            "revenus_inegalites": 58,
            "education": 78,
            "emploi": 69,
            "logement": 42,
            "sante_sociale": 70,
            "revenu_median": 30300,
            "taux_pauvrete": 16.2,
            "d9_d1": 6.4,
        },
        {
            "commune": "Versailles",
            "departement": "78",
            "lat": 48.8049,
            "lon": 2.1204,
            "revenus_inegalites": 74,
            "education": 82,
            "emploi": 75,
            "logement": 56,
            "sante_sociale": 73,
            "revenu_median": 34600,
            "taux_pauvrete": 8.9,
            "d9_d1": 4.1,
        },
        {
            "commune": "Saint-Denis",
            "departement": "93",
            "lat": 48.9362,
            "lon": 2.3574,
            "revenus_inegalites": 34,
            "education": 41,
            "emploi": 38,
            "logement": 35,
            "sante_sociale": 44,
            "revenu_median": 17600,
            "taux_pauvrete": 33.0,
            "d9_d1": 4.8,
        },
        {
            "commune": "Cergy",
            "departement": "95",
            "lat": 49.0361,
            "lon": 2.0631,
            "revenus_inegalites": 49,
            "education": 57,
            "emploi": 53,
            "logement": 50,
            "sante_sociale": 55,
            "revenu_median": 22600,
            "taux_pauvrete": 20.4,
            "d9_d1": 3.8,
        },
        {
            "commune": "Créteil",
            "departement": "94",
            "lat": 48.7904,
            "lon": 2.4556,
            "revenus_inegalites": 52,
            "education": 58,
            "emploi": 57,
            "logement": 48,
            "sante_sociale": 59,
            "revenu_median": 23900,
            "taux_pauvrete": 18.7,
            "d9_d1": 3.9,
        },
        {
            "commune": "Évry-Courcouronnes",
            "departement": "91",
            "lat": 48.6238,
            "lon": 2.4292,
            "revenus_inegalites": 45,
            "education": 51,
            "emploi": 50,
            "logement": 47,
            "sante_sociale": 53,
            "revenu_median": 21300,
            "taux_pauvrete": 22.6,
            "d9_d1": 3.7,
        },
        {
            "commune": "Meaux",
            "departement": "77",
            "lat": 48.9607,
            "lon": 2.8787,
            "revenus_inegalites": 47,
            "education": 48,
            "emploi": 49,
            "logement": 52,
            "sante_sociale": 50,
            "revenu_median": 21700,
            "taux_pauvrete": 21.3,
            "d9_d1": 3.5,
        },
        {
            "commune": "Nanterre",
            "departement": "92",
            "lat": 48.8924,
            "lon": 2.2153,
            "revenus_inegalites": 55,
            "education": 62,
            "emploi": 60,
            "logement": 45,
            "sante_sociale": 61,
            "revenu_median": 26100,
            "taux_pauvrete": 17.8,
            "d9_d1": 4.7,
        },
    ]
)

DIMENSIONS = {
    "revenus_inegalites": "Revenus et inégalités",
    "education": "Éducation",
    "emploi": "Emploi",
    "logement": "Logement",
    "sante_sociale": "Santé sociale",
}

# -----------------------------
# Sidebar : choix et pondérations
# -----------------------------
st.sidebar.markdown("## 🗺️ Carte interactive")
st.sidebar.markdown("Choisis une commune, puis modifie les pondérations pour observer l'effet sur le score.")

commune_choisie = st.sidebar.selectbox(
    "Commune sélectionnée",
    communes_demo["commune"].sort_values().tolist(),
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚖️ Pondérations")
st.sidebar.caption("Les poids sont normalisés automatiquement pour totaliser 100 %.")

poids_bruts = {}
for col, label in DIMENSIONS.items():
    poids_bruts[col] = st.sidebar.slider(label, 0, 10, 5)

total_poids = sum(poids_bruts.values())
if total_poids == 0:
    poids = {k: 1 / len(poids_bruts) for k in poids_bruts}
else:
    poids = {k: v / total_poids for k, v in poids_bruts.items()}

st.sidebar.markdown("---")
afficher_methode = st.sidebar.toggle("Afficher les notes méthodologiques", value=True)

# -----------------------------
# Calcul du score global
# -----------------------------
def calculer_score_global(df: pd.DataFrame, poids_normalises: dict) -> pd.DataFrame:
    df = df.copy()
    df["score_global"] = 0.0
    for col, p in poids_normalises.items():
        df["score_global"] += df[col] * p
    df["score_global"] = df["score_global"].round(1)
    return df

communes = calculer_score_global(communes_demo, poids)
selection = communes.loc[communes["commune"] == commune_choisie].iloc[0]

# -----------------------------
# En-tête
# -----------------------------
st.markdown(
    """
    <div class="main-title">
        <h1>ISS communal participatif — Île-de-France</h1>
        <p>Explorer les communes, visualiser les écarts territoriaux et discuter collectivement les choix de construction de l'indicateur.</p>
    </div>
    <div class="stepbar">
        <div class="step"><span>1</span>Choisir</div>
        <div class="step"><span>2</span>Pondérer</div>
        <div class="step"><span>3</span>Cartographier</div>
        <div class="step"><span>4</span>Comparer</div>
        <div class="step"><span>5</span>Débattre</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Indicateurs rapides
# -----------------------------
col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    st.metric("Commune", selection["commune"], f"Département {selection['departement']}")
with col_b:
    st.metric("Score global", f"{selection['score_global']}/100")
with col_c:
    st.metric("Taux de pauvreté", f"{selection['taux_pauvrete']} %")
with col_d:
    st.metric("Rapport D9/D1", f"{selection['d9_d1']}")

# -----------------------------
# Corps principal : carte + panneau commune
# -----------------------------
left, right = st.columns([1.65, 1], gap="large")

with left:
    st.markdown('<div class="card"><h3>Carte des scores communaux</h3>', unsafe_allow_html=True)

    fig_map = px.scatter_mapbox(
        communes,
        lat="lat",
        lon="lon",
        hover_name="commune",
        hover_data={
            "departement": True,
            "score_global": True,
            "revenu_median": ":,.0f",
            "taux_pauvrete": True,
            "lat": False,
            "lon": False,
        },
        color="score_global",
        size="score_global",
        zoom=8,
        height=560,
        color_continuous_scale=["#b93838", "#c97822", "#2e7d61"],
        size_max=34,
    )
    fig_map.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(title="Score"),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.caption(
        "Prototype : les points représentent les communes. Dans une version avancée, on pourra remplacer ces points par un vrai fond de carte communal GeoJSON."
    )
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="card"><h3>Profil de la commune sélectionnée</h3>', unsafe_allow_html=True)

    score = selection["score_global"]
    if score < 45:
        st.markdown(
            '<div class="alert-red">🔴 Situation fragile : le score invite à regarder les variables défavorables et les effets de cumul.</div>',
            unsafe_allow_html=True,
        )
    elif score < 60:
        st.markdown(
            '<div class="alert-orange">🟠 Situation intermédiaire : le résultat dépend fortement des pondérations choisies.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="alert-green">🟢 Situation relativement favorable selon les choix de variables et de pondérations.</div>',
            unsafe_allow_html=True,
        )

    st.write("")

    radar_values = [selection[col] for col in DIMENSIONS.keys()]
    radar_labels = list(DIMENSIONS.values())

    fig_radar = go.Figure()
    fig_radar.add_trace(
        go.Scatterpolar(
            r=radar_values + [radar_values[0]],
            theta=radar_labels + [radar_labels[0]],
            fill="toself",
            name=selection["commune"],
        )
    )
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=360,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Comparaison des dimensions
# -----------------------------
st.markdown('<div class="card"><h3>Comparer les dimensions de la commune</h3>', unsafe_allow_html=True)

bar_df = pd.DataFrame(
    {
        "Dimension": list(DIMENSIONS.values()),
        "Score normalisé": [selection[col] for col in DIMENSIONS.keys()],
    }
).sort_values("Score normalisé")

fig_bar = px.bar(
    bar_df,
    x="Score normalisé",
    y="Dimension",
    orientation="h",
    range_x=[0, 100],
    text="Score normalisé",
    height=360,
)
fig_bar.update_traces(textposition="outside")
fig_bar.update_layout(
    margin=dict(l=10, r=30, t=10, b=10),
    xaxis_title="Score sur 100",
    yaxis_title="",
)
st.plotly_chart(fig_bar, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Tableau comparatif
# -----------------------------
with st.expander("Voir le tableau comparatif des communes"):
    colonnes_tableau = ["commune", "departement", "score_global"] + list(DIMENSIONS.keys()) + [
        "revenu_median",
        "taux_pauvrete",
        "d9_d1",
    ]
    table = communes[colonnes_tableau].sort_values("score_global", ascending=False)
    table = table.rename(columns={**DIMENSIONS, "commune": "Commune", "departement": "Département", "score_global": "Score global"})
    st.dataframe(table, use_container_width=True, hide_index=True)

# -----------------------------
# Méthode et discussion collective
# -----------------------------
if afficher_methode:
    st.markdown('<div class="card"><h3>Notes méthodologiques et discussion collective</h3>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="method-box">
        <strong>Principe pédagogique :</strong> la carte ne doit pas être lue comme un classement naturel des communes.
        Elle rend visibles les effets des choix collectifs : sélection des variables, sens favorable ou défavorable,
        bornes de normalisation, pondérations et seuils d'alerte.
        <br><br>
        <strong>À discuter avec les élèves :</strong>
        <ul>
            <li>Le score global masque-t-il certaines fragilités locales ?</li>
            <li>Une commune peut-elle être favorisée par le choix des pondérations ?</li>
            <li>Faut-il afficher des alertes rouges lorsqu'une variable dépasse un seuil critique ?</li>
            <li>Quels indicateurs manquent pour mieux représenter la santé sociale d'une commune ?</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Préparation à l'intégration dans ton app.py
# -----------------------------
with st.expander("Comment intégrer ce style dans ton app.py existant ?"):
    st.markdown(
        """
        1. Garde ton code de calcul actuel : normalisation, variables, dimensions et score global.
        2. Ajoute les colonnes `lat` et `lon` à ta base communale pour afficher les communes sur la carte.
        3. Remplace `communes_demo` par ton DataFrame final.
        4. Conserve les blocs CSS et la structure `carte + panneau latéral + radar + tableau`.
        5. Plus tard, remplace `scatter_mapbox` par une vraie carte communale avec un fichier GeoJSON des communes d'Île-de-France.
        """
    )
