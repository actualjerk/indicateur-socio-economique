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
# STYLE
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.05rem;
        color: #555;
        margin-bottom: 1.4rem;
    }
    .metric-card {
        background-color: #f7f7f9;
        border-radius: 14px;
        padding: 16px;
        border: 1px solid #e6e6eb;
        margin-bottom: 10px;
    }
    .small-note {
        color: #666;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# DONNÉES : DIMENSIONS, VARIABLES ET BORNES
# ─────────────────────────────────────────────
# sens = "positif" : plus la valeur est élevée, meilleur est le score.
# sens = "negatif" : plus la valeur est élevée, plus le score est dégradé.
#
# Modifications intégrées :
# - Revenu médian : bornes Île-de-France calculées dans le fichier Filosofi 2021
#   min = 14 790 € ; max = 48 010 €
# - Rapport interdécile D9/D1 : nouvelle variable de la dimension Revenu
#   min = 2,2 ; max = 8,1
#   sens négatif car un D9/D1 élevé traduit davantage d'inégalités de revenus.

DIMENSIONS = {
    "Revenu": {
        "description": "Niveau de vie, pauvreté et inégalités monétaires.",
        "variables": {
            "Revenu médian": {
                "min": 14790,
                "max": 48010,
                "valeur": 25210,
                "unite": "€",
                "sens": "positif",
                "source": "Filosofi 2021, communes d'Île-de-France"
            },
            "Taux de pauvreté (%)": {
                "min": 5,
                "max": 44,
                "valeur": 18,
                "unite": "%",
                "sens": "negatif",
                "source": "Filosofi, communes d'Île-de-France"
            },
            "Rapport interdécile du revenu disponible par unité de consommation (D9/D1)": {
                "min": 2.2,
                "max": 8.1,
                "valeur": 4.4,
                "unite": "",
                "sens": "negatif",
                "source": "Filosofi 2021, communes d'Île-de-France"
            },
            "Part bas revenus (%)": {
                "min": 5,
                "max": 40,
                "valeur": 20,
                "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter"
            },
        },
    },
    "Éducation": {
        "description": "Accès aux diplômes, niveau de formation et scolarisation.",
        "variables": {
            "Diplômés du supérieur (%)": {
                "min": 5,
                "max": 60,
                "valeur": 25,
                "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter"
            },
            "Sans diplôme (%)": {
                "min": 5,
                "max": 50,
                "valeur": 30,
                "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter"
            },
            "Taux de scolarisation (%)": {
                "min": 50,
                "max": 99,
                "valeur": 80,
                "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter"
            },
        },
    },
    "Emploi": {
        "description": "Accès à l'emploi, chômage et stabilité des situations professionnelles.",
        "variables": {
            "Taux de chômage (%)": {
                "min": 2,
                "max": 30,
                "valeur": 12,
                "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter"
            },
            "Part contrats précaires (%)": {
                "min": 5,
                "max": 40,
                "valeur": 20,
                "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter"
            },
            "Taux d'activité (%)": {
                "min": 45,
                "max": 85,
                "valeur": 70,
                "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter"
            },
        },
    },
    "Santé": {
        "description": "État de santé et accès potentiel aux soins.",
        "variables": {
            "Espérance de vie": {
                "min": 70,
                "max": 90,
                "valeur": 82,
                "unite": "ans",
                "sens": "positif",
                "source": "Borne indicative à discuter"
            },
            "Médecins pour 1000 habitants": {
                "min": 0,
                "max": 10,
                "valeur": 3,
                "unite": "",
                "sens": "positif",
                "source": "Borne indicative à discuter"
            },
            "Mortalité prématurée": {
                "min": 100,
                "max": 500,
                "valeur": 250,
                "unite": "pour 100 000",
                "sens": "negatif",
                "source": "Borne indicative à discuter"
            },
        },
    },
    "Logement": {
        "description": "Conditions de logement et accès au logement social.",
        "variables": {
            "Part logements sociaux (%)": {
                "min": 0,
                "max": 60,
                "valeur": 20,
                "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter"
            },
            "Mal-logement (%)": {
                "min": 0,
                "max": 30,
                "valeur": 10,
                "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter"
            },
            "Surpopulation des logements (%)": {
                "min": 0,
                "max": 25,
                "valeur": 8,
                "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter"
            },
        },
    },
    "Cohésion sociale": {
        "description": "Participation, liens sociaux et fragilités sociales.",
        "variables": {
            "Participation électorale (%)": {
                "min": 30,
                "max": 90,
                "valeur": 60,
                "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter"
            },
            "Familles monoparentales (%)": {
                "min": 5,
                "max": 40,
                "valeur": 18,
                "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter"
            },
            "Criminalité pour 1000 habitants": {
                "min": 0,
                "max": 100,
                "valeur": 35,
                "unite": "",
                "sens": "negatif",
                "source": "Borne indicative à discuter"
            },
        },
    },
    "Environnement": {
        "description": "Cadre de vie environnemental et exposition aux nuisances.",
        "variables": {
            "Espaces verts (%)": {
                "min": 0,
                "max": 80,
                "valeur": 25,
                "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter"
            },
            "Pollution de l'air (µg/m³)": {
                "min": 5,
                "max": 40,
                "valeur": 20,
                "unite": "",
                "sens": "negatif",
                "source": "Borne indicative à discuter"
            },
            "Densité de population (hab/km²)": {
                "min": 50,
                "max": 25000,
                "valeur": 5000,
                "unite": "",
                "sens": "negatif",
                "source": "Borne indicative à discuter"
            },
        },
    },
}

VARIABLES_INVERSES = [
    nom_variable
    for dimension in DIMENSIONS.values()
    for nom_variable, infos in dimension["variables"].items()
    if infos.get("sens") == "negatif"
]

# ─────────────────────────────────────────────
# FONCTIONS DE CALCUL
# ─────────────────────────────────────────────
def normaliser(valeur, vmin, vmax, sens="positif"):
    """
    Normalisation linéaire min-max sur une échelle 0-1.

    Variable positive :
        score = (valeur - min) / (max - min)

    Variable négative :
        score = 1 - (valeur - min) / (max - min)

    Le score est borné entre 0 et 1 pour éviter les valeurs aberrantes.
    """
    if vmax == vmin:
        return 0.0

    score = (valeur - vmin) / (vmax - vmin)

    if sens == "negatif":
        score = 1 - score

    return float(np.clip(score, 0, 1))


def moyenne_ponderee(scores, poids):
    """Calcule une moyenne pondérée en ignorant les poids nuls."""
    scores = np.array(scores, dtype=float)
    poids = np.array(poids, dtype=float)

    if len(scores) == 0 or poids.sum() == 0:
        return 0.0

    return float(np.average(scores, weights=poids))


def calculer_indicateur(valeurs, poids_variables, poids_dimensions):
    """
    Calcule :
    - les scores normalisés de chaque variable ;
    - les scores de chaque dimension ;
    - l'indicateur synthétique global.
    """
    resultats_variables = []
    scores_dimensions = {}

    for nom_dimension, contenu_dimension in DIMENSIONS.items():
        scores_var_dim = []
        poids_var_dim = []

        for nom_variable, infos in contenu_dimension["variables"].items():
            valeur = valeurs[nom_variable]
            poids = poids_variables[nom_variable]

            score = normaliser(
                valeur=valeur,
                vmin=infos["min"],
                vmax=infos["max"],
                sens=infos.get("sens", "positif")
            )

            scores_var_dim.append(score)
            poids_var_dim.append(poids)

            resultats_variables.append({
                "Dimension": nom_dimension,
                "Variable": nom_variable,
                "Valeur": valeur,
                "Unité": infos.get("unite", ""),
                "Min": infos["min"],
                "Max": infos["max"],
                "Sens": infos.get("sens", "positif"),
                "Poids variable": poids,
                "Score normalisé 0-1": round(score, 4),
                "Score normalisé 0-100": round(score * 100, 2),
                "Source / remarque": infos.get("source", "")
            })

        score_dimension = moyenne_ponderee(scores_var_dim, poids_var_dim)
        scores_dimensions[nom_dimension] = score_dimension

    indicateur_global = moyenne_ponderee(
        list(scores_dimensions.values()),
        [poids_dimensions[dim] for dim in scores_dimensions.keys()]
    )

    return resultats_variables, scores_dimensions, indicateur_global


def creer_radar(scores_dimensions):
    """Crée un graphique radar agrandi pour visualiser les scores des dimensions."""
    dimensions = list(scores_dimensions.keys())
    scores = [scores_dimensions[dim] * 100 for dim in dimensions]

    # Fermer le radar
    dimensions_fermees = dimensions + [dimensions[0]]
    scores_fermes = scores + [scores[0]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=scores_fermes,
            theta=dimensions_fermees,
            fill="toself",
            name="Score des dimensions",
            line=dict(width=3)
        )
    )

    fig.update_layout(
        height=700,  # Radar agrandi
        margin=dict(l=90, r=90, t=80, b=80),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=12)
            ),
            angularaxis=dict(
                tickfont=dict(size=14)
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.08,
            xanchor="center",
            x=0.5
        )
    )

    return fig


# ─────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">📊 Indicateur Socio-Économique communal</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Prototype pédagogique participatif inspiré des indicateurs alternatifs de richesse et de santé sociale.</div>',
    unsafe_allow_html=True
)

with st.expander("ℹ️ Méthode de normalisation utilisée", expanded=False):
    st.write(
        """
        Chaque variable est normalisée entre 0 et 1 avec une méthode min-max.

        - Pour une variable positive, un niveau élevé améliore le score.
        - Pour une variable négative, un niveau élevé dégrade le score.

        Formule pour une variable positive :

        `score = (valeur - min) / (max - min)`

        Formule pour une variable négative :

        `score = 1 - ((valeur - min) / (max - min))`

        Les scores sont ensuite bornés entre 0 et 1, puis exprimés sur 100 pour l'affichage.
        """
    )

with st.sidebar:
    st.header("⚙️ Pondération des dimensions")
    st.caption("Poids de chaque dimension dans l'indicateur final.")

    poids_dimensions = {}
    for nom_dimension in DIMENSIONS.keys():
        poids_dimensions[nom_dimension] = st.slider(
            label=f"Poids — {nom_dimension}",
            min_value=0.0,
            max_value=5.0,
            value=1.0,
            step=0.5,
            key=f"poids_dimension_{nom_dimension}"
        )

    st.divider()
    st.header("📌 Bornes intégrées")
    st.write("**Revenu médian** : 14 790 € → 48 010 €")
    st.write("**D9/D1** : 2,2 → 8,1")
    st.write("**Taux de pauvreté** : 5 % → 44 %")

# ─────────────────────────────────────────────
# SAISIE DES VALEURS
# ─────────────────────────────────────────────
st.header("1. Choix des valeurs et des poids des variables")

valeurs = {}
poids_variables = {}

tabs = st.tabs(list(DIMENSIONS.keys()))

for tab, (nom_dimension, contenu_dimension) in zip(tabs, DIMENSIONS.items()):
    with tab:
        st.subheader(nom_dimension)
        st.write(contenu_dimension["description"])

        for nom_variable, infos in contenu_dimension["variables"].items():
            st.markdown(f"#### {nom_variable}")

            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                step = 0.1 if isinstance(infos["min"], float) or isinstance(infos["max"], float) else 1.0
                format_affichage = "%.1f" if step == 0.1 else "%.0f"
                unite_label = f"({infos.get('unite')})" if infos.get("unite") else ""

                valeurs[nom_variable] = st.number_input(
                    label=f"Valeur observée {unite_label}",
                    min_value=float(infos["min"]),
                    max_value=float(infos["max"]),
                    value=float(infos["valeur"]),
                    step=float(step),
                    format=format_affichage,
                    key=f"valeur_{nom_dimension}_{nom_variable}"
                )

            with col2:
                poids_variables[nom_variable] = st.slider(
                    label="Poids",
                    min_value=0.0,
                    max_value=5.0,
                    value=1.0,
                    step=0.5,
                    key=f"poids_variable_{nom_dimension}_{nom_variable}"
                )

            with col3:
                sens = infos.get("sens", "positif")
                sens_affiche = "positif" if sens == "positif" else "négatif / inversé"
                st.metric("Sens", sens_affiche)
                st.caption(f"Bornes : {infos['min']} → {infos['max']} {infos.get('unite', '')}")

            st.markdown("---")

# ─────────────────────────────────────────────
# CALCUL
# ─────────────────────────────────────────────
resultats_variables, scores_dimensions, indicateur_global = calculer_indicateur(
    valeurs=valeurs,
    poids_variables=poids_variables,
    poids_dimensions=poids_dimensions
)

df_resultats = pd.DataFrame(resultats_variables)

# ─────────────────────────────────────────────
# AFFICHAGE DES RÉSULTATS
# ─────────────────────────────────────────────
st.header("2. Résultat de l'indicateur synthétique")

col_score, col_radar = st.columns([1, 2])

with col_score:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="Score global",
        value=f"{indicateur_global * 100:.1f} / 100"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Scores par dimension")
    for dim, score in scores_dimensions.items():
        st.write(f"**{dim}** : {score * 100:.1f} / 100")
        st.progress(score)

with col_radar:
    st.subheader("Radar des dimensions")
    fig_radar = creer_radar(scores_dimensions)
    st.plotly_chart(fig_radar, use_container_width=True)

# ─────────────────────────────────────────────
# TABLEAUX
# ─────────────────────────────────────────────
st.header("3. Détail des variables normalisées")

st.dataframe(
    df_resultats[
        [
            "Dimension",
            "Variable",
            "Valeur",
            "Unité",
            "Min",
            "Max",
            "Sens",
            "Poids variable",
            "Score normalisé 0-100",
            "Source / remarque"
        ]
    ],
    use_container_width=True
)

st.subheader("Lecture rapide des nouvelles bornes de la dimension Revenu")

df_revenu = df_resultats[df_resultats["Dimension"] == "Revenu"][
    [
        "Variable",
        "Valeur",
        "Min",
        "Max",
        "Sens",
        "Score normalisé 0-100",
        "Source / remarque"
    ]
]

st.dataframe(df_revenu, use_container_width=True)

# ─────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────
st.header("4. Export des résultats")

csv_resultats = df_resultats.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="📥 Télécharger les résultats en CSV",
    data=csv_resultats,
    file_name="resultats_indicateur_socio_economique.csv",
    mime="text/csv"
)

# ─────────────────────────────────────────────
# NOTE PÉDAGOGIQUE
# ─────────────────────────────────────────────
with st.expander("🧠 Note pédagogique : pourquoi D9/D1 est inversé ?", expanded=False):
    st.write(
        """
        Le rapport interdécile D9/D1 compare le niveau de vie au-dessus duquel se situent les 10 % les plus aisés
        au niveau de vie au-dessous duquel se situent les 10 % les plus modestes.

        Exemple : un D9/D1 égal à 4 signifie que le seuil des 10 % les plus aisés est environ quatre fois plus élevé
        que le seuil des 10 % les plus modestes.

        Dans un indicateur de santé sociale ou socio-économique, une valeur élevée du D9/D1 traduit donc une plus forte
        inégalité de revenus. C'est pourquoi la normalisation est inversée :
        plus le D9/D1 augmente, plus le score diminue.
        """
    )
