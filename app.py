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
    .section-box {
        background-color: #f7f7f9;
        border-radius: 14px;
        padding: 16px;
        border: 1px solid #e6e6eb;
        margin-bottom: 14px;
    }
    .small-note {
        color: #666;
        font-size: 0.9rem;
    }
    .variable-title {
        background-color: #e8f1ff;
        color: #1f4e79;
        font-size: 1.15rem;
        font-weight: 700;
        padding: 10px 14px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin-top: 8px;
        margin-bottom: 8px;
    }
    .dimension-title {
        background-color: #e8f1ff;
        color: #1f4e79;
        font-size: 1.2rem;
        font-weight: 700;
        padding: 12px 16px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin-top: 12px;
        margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# DONNÉES : DIMENSIONS, VARIABLES ET BORNES
# ─────────────────────────────────────────────

DIMENSIONS = {
    "Revenu": {
        "description": "Cette dimension mesure le niveau de vie, la pauvreté et les inégalités monétaires.",
        "variables": {
            "Revenu médian": {
                "min": 14790,
                "max": 48010,
                "valeur": 25210,
                "unite": "€",
                "sens": "positif",
                "source": "Filosofi 2021, communes d'Île-de-France"
            },
            "Taux de pauvreté au seuil de 60 % du revenu médian": {
                "min": 5,
                "max": 44,
                "valeur": 18,
                "unite": "%",
                "sens": "negatif",
                "source": "Filosofi 2021, communes d'Île-de-France"
            },
            "Rapport interdécile du revenu disponible par unité de consommation D9/D1": {
                "min": 2.2,
                "max": 8.1,
                "valeur": 4.4,
                "unite": "",
                "sens": "negatif",
                "source": "Filosofi 2021, communes d'Île-de-France"
            },
            "Part des bas revenus": {
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
        "description": "Cette dimension mesure le niveau de formation, la scolarisation et l'accès aux diplômes.",
        "variables": {
            "Diplômés du supérieur": {
                "min": 5,
                "max": 60,
                "valeur": 25,
                "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter"
            },
            "Sans diplôme": {
                "min": 5,
                "max": 50,
                "valeur": 30,
                "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter"
            },
            "Taux de scolarisation": {
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
        "description": "Cette dimension mesure l'accès à l'emploi, le chômage et la stabilité professionnelle.",
        "variables": {
            "Taux de chômage": {
                "min": 2,
                "max": 30,
                "valeur": 12,
                "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter"
            },
            "Part des contrats précaires": {
                "min": 5,
                "max": 40,
                "valeur": 20,
                "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter"
            },
            "Taux d'activité": {
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
        "description": "Cette dimension mesure l'état de santé et l'accès potentiel aux soins.",
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
        "description": "Cette dimension mesure les conditions de logement et l'accès au logement social.",
        "variables": {
            "Part des logements sociaux": {
                "min": 0,
                "max": 60,
                "valeur": 20,
                "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter"
            },
            "Mal-logement": {
                "min": 0,
                "max": 30,
                "valeur": 10,
                "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter"
            },
            "Surpopulation des logements": {
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
        "description": "Cette dimension mesure les liens sociaux, la participation et certaines fragilités sociales.",
        "variables": {
            "Participation électorale": {
                "min": 30,
                "max": 90,
                "valeur": 60,
                "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter"
            },
            "Familles monoparentales": {
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
        "description": "Cette dimension mesure la qualité du cadre de vie environnemental.",
        "variables": {
            "Espaces verts": {
                "min": 0,
                "max": 80,
                "valeur": 25,
                "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter"
            },
            "Pollution de l'air": {
                "min": 5,
                "max": 40,
                "valeur": 20,
                "unite": "µg/m³",
                "sens": "negatif",
                "source": "Borne indicative à discuter"
            },
            "Densité de population": {
                "min": 50,
                "max": 25000,
                "valeur": 5000,
                "unite": "hab/km²",
                "sens": "negatif",
                "source": "Borne indicative à discuter"
            },
        },
    },
}

# ─────────────────────────────────────────────
# FONCTIONS
# ─────────────────────────────────────────────

def normaliser(valeur, vmin, vmax, sens="positif"):
    if vmax == vmin:
        return 0.0

    score = (valeur - vmin) / (vmax - vmin)

    if sens == "negatif":
        score = 1 - score

    return float(np.clip(score, 0, 1))


def moyenne_ponderee(scores, poids):
    scores = np.array(scores, dtype=float)
    poids = np.array(poids, dtype=float)

    if len(scores) == 0 or poids.sum() == 0:
        return 0.0

    return float(np.average(scores, weights=poids))


def calculer_indicateur(dimensions_choisies, variables_choisies, valeurs, poids_variables, poids_dimensions):
    resultats_variables = []
    scores_dimensions = {}

    for nom_dimension in dimensions_choisies:
        variables_dimension = variables_choisies.get(nom_dimension, [])

        if len(variables_dimension) == 0:
            continue

        scores_var_dim = []
        poids_var_dim = []

        for nom_variable in variables_dimension:
            infos = DIMENSIONS[nom_dimension]["variables"][nom_variable]

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
                "Poids variable": poids,
                "Score normalisé 0-1": round(score, 4),
                "Score normalisé 0-100": round(score * 100, 2),
                "Source": infos.get("source", "")
            })

        score_dimension = moyenne_ponderee(scores_var_dim, poids_var_dim)
        scores_dimensions[nom_dimension] = score_dimension

    if len(scores_dimensions) == 0:
        return resultats_variables, scores_dimensions, 0.0

    indicateur_global = moyenne_ponderee(
        list(scores_dimensions.values()),
        [poids_dimensions[dim] for dim in scores_dimensions.keys()]
    )

    return resultats_variables, scores_dimensions, indicateur_global


def creer_radar(scores_dimensions):
    dimensions = list(scores_dimensions.keys())
    scores = [scores_dimensions[dim] * 100 for dim in dimensions]

    if len(dimensions) == 0:
        return go.Figure()

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
        height=720,
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
        showlegend=True
    )

    return fig


def tableau_variables():
    lignes = []

    for nom_dimension, contenu in DIMENSIONS.items():
        for nom_variable, infos in contenu["variables"].items():
            lignes.append({
                "Dimension": nom_dimension,
                "Variable": nom_variable,
                "Min": infos["min"],
                "Max": infos["max"],
                "Unité": infos.get("unite", ""),
                "Source": infos.get("source", "")
            })

    return pd.DataFrame(lignes)


# ─────────────────────────────────────────────
# TITRE
# ─────────────────────────────────────────────

st.markdown(
    '<div class="main-title">📊 Indicateur Socio-Économique communal</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Prototype pédagogique participatif permettant de choisir des dimensions, des variables et des pondérations.</div>',
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# INTRODUCTION MÉTHODOLOGIQUE
# ─────────────────────────────────────────────

with st.expander("ℹ️ Comprendre la logique de construction de l'indicateur", expanded=False):
    st.write(
        """
        L'indicateur est construit en trois étapes :

        **1. Choix des dimensions**  
        Une dimension correspond à un grand domaine de la réalité sociale ou économique : revenu, santé, emploi, logement, etc.

        **2. Choix des variables**  
        Une variable est une donnée précise utilisée pour mesurer une dimension.  
        Par exemple, dans la dimension revenu, on peut retenir le revenu médian, le taux de pauvreté au seuil de 60 % du revenu médian ou le rapport interdécile D9/D1.

        **3. Pondération**  
        Les élèves peuvent ensuite décider du poids de chaque variable et du poids de chaque dimension.
        Cela permet de discuter démocratiquement de ce qui compte le plus dans l'indicateur.
        """
    )

with st.expander("📌 Voir toutes les dimensions et variables disponibles", expanded=False):
    st.dataframe(tableau_variables(), use_container_width=True)

# ─────────────────────────────────────────────
# 1. CHOIX DES DIMENSIONS
# ─────────────────────────────────────────────

with st.expander("1. Choisir les dimensions de l'indicateur", expanded=True):

    dimensions_disponibles = list(DIMENSIONS.keys())

    st.write("Cochez les dimensions que vous souhaitez intégrer dans l'indicateur final :")

    dimensions_choisies = []

    for nom_dimension in dimensions_disponibles:
        st.markdown(
            f'<div class="dimension-title">{nom_dimension}</div>',
            unsafe_allow_html=True
        )

        dimension_active = st.checkbox(
            label="Inclure cette dimension",
            value=True,
            key=f"choix_dimension_{nom_dimension}"
        )

        if dimension_active:
            dimensions_choisies.append(nom_dimension)

    if len(dimensions_choisies) == 0:
        st.warning("Vous devez choisir au moins une dimension pour calculer l'indicateur.")
        st.stop()

    st.markdown("Dimensions retenues : **" + ", ".join(dimensions_choisies) + "**")

# ─────────────────────────────────────────────
# PONDÉRATION DES DIMENSIONS
# ─────────────────────────────────────────────

with st.sidebar:
    st.header("⚖️ Poids des dimensions")
    st.caption("Ces poids indiquent l'importance de chaque dimension dans le score final.")

    poids_dimensions = {}

    for nom_dimension in dimensions_choisies:
        poids_dimensions[nom_dimension] = st.slider(
            label=f"{nom_dimension}",
            min_value=0.0,
            max_value=5.0,
            value=1.0,
            step=0.5,
            key=f"poids_dimension_{nom_dimension}"
        )

    st.divider()

    st.header("📌 Bornes importantes")
    st.write("**Revenu médian** : 14 790 € → 48 010 €")
    st.write("**Taux de pauvreté au seuil de 60 %** : 5 % → 44 %")
    st.write("**Rapport D9/D1** : 2,2 → 8,1")

# ─────────────────────────────────────────────
# 2. CHOIX DES VARIABLES ET VALEURS
# ─────────────────────────────────────────────

with st.expander("2. Choisir les variables dans chaque dimension", expanded=True):

    st.write(
        """
        Pour chaque dimension retenue, choisissez les variables qui doivent entrer dans le calcul.
        Une variable cochée est intégrée à l'indicateur. Une variable décochée est ignorée.
        """
    )

    variables_choisies = {}
    valeurs = {}
    poids_variables = {}

    tabs = st.tabs(dimensions_choisies)

    for tab, nom_dimension in zip(tabs, dimensions_choisies):
        with tab:
            contenu_dimension = DIMENSIONS[nom_dimension]

            st.subheader(f"Dimension : {nom_dimension}")
            st.write(contenu_dimension["description"])

            st.markdown("### Variables disponibles dans cette dimension")

            variables_choisies[nom_dimension] = []

            for nom_variable, infos in contenu_dimension["variables"].items():
                st.markdown("---")

                col_check, col_variable = st.columns([0.08, 0.92])

                with col_check:
                    actif = st.checkbox(
                        label=f"Sélectionner {nom_variable}",
                        value=True,
                        key=f"actif_{nom_dimension}_{nom_variable}",
                        label_visibility="collapsed"
                    )

                with col_variable:
                    st.markdown(
                        f'<div class="variable-title">{nom_variable}</div>',
                        unsafe_allow_html=True
                    )

                st.caption(
                    f"Borne min : {infos['min']} {infos.get('unite', '')} | "
                    f"Borne max : {infos['max']} {infos.get('unite', '')}"
                )

                if actif:
                    variables_choisies[nom_dimension].append(nom_variable)

                    col1, col2 = st.columns([2, 1])

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
                            label="Poids de la variable",
                            min_value=0.0,
                            max_value=5.0,
                            value=1.0,
                            step=0.5,
                            key=f"poids_variable_{nom_dimension}_{nom_variable}"
                        )

                else:
                    st.warning("Cette variable ne sera pas intégrée au calcul.")

# ─────────────────────────────────────────────
# VÉRIFICATION
# ─────────────────────────────────────────────

nombre_variables_retenues = sum(len(v) for v in variables_choisies.values())

if nombre_variables_retenues == 0:
    st.warning("Vous devez choisir au moins une variable pour calculer l'indicateur.")
    st.stop()

# ─────────────────────────────────────────────
# CALCUL
# ─────────────────────────────────────────────

resultats_variables, scores_dimensions, indicateur_global = calculer_indicateur(
    dimensions_choisies=dimensions_choisies,
    variables_choisies=variables_choisies,
    valeurs=valeurs,
    poids_variables=poids_variables,
    poids_dimensions=poids_dimensions
)

df_resultats = pd.DataFrame(resultats_variables)

# ─────────────────────────────────────────────
# 3. RÉSULTATS
# ─────────────────────────────────────────────

with st.expander("3. Résultat de l'indicateur synthétique", expanded=True):

    col_score, col_radar = st.columns([1, 2])

    with col_score:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
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
# 4. DÉTAIL DES VARIABLES
# ─────────────────────────────────────────────

with st.expander("4. Détail du calcul par variable", expanded=False):

    st.write(
        """
        Le tableau ci-dessous montre uniquement les variables retenues dans le calcul.
        Il permet de vérifier les bornes, le poids et le score obtenu.
        """
    )

    st.dataframe(
        df_resultats[
            [
                "Dimension",
                "Variable",
                "Valeur",
                "Unité",
                "Min",
                "Max",
                "Poids variable",
                "Score normalisé 0-100",
                "Source"
            ]
        ],
        use_container_width=True
    )

    if "Revenu" in scores_dimensions:
        st.subheader("Zoom sur la dimension Revenu")

        df_revenu = df_resultats[df_resultats["Dimension"] == "Revenu"][
            [
                "Variable",
                "Valeur",
                "Unité",
                "Min",
                "Max",
                "Score normalisé 0-100",
                "Source"
            ]
        ]

        st.dataframe(df_revenu, use_container_width=True)

        with st.expander("🧠 Pourquoi le rapport D9/D1 réduit-il le score ?", expanded=False):
            st.write(
                """
                Le rapport interdécile D9/D1 mesure l'écart entre les 10 % les plus aisés et les 10 % les plus modestes.

                Un rapport D9/D1 élevé signifie que les écarts de revenus sont importants.
                Dans un indicateur de santé sociale ou socio-économique, cela correspond à une situation moins favorable.

                C'est pourquoi, dans le calcul, plus le rapport D9/D1 augmente, plus le score de cette variable diminue.
                """
            )

# ─────────────────────────────────────────────
# 5. EXPORT
# ─────────────────────────────────────────────

with st.expander("5. Export des résultats", expanded=False):

    csv_resultats = df_resultats.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="📥 Télécharger les résultats en CSV",
        data=csv_resultats,
        file_name="resultats_indicateur_socio_economique.csv",
        mime="text/csv"
    )

# ─────────────────────────────────────────────
# NOTE FINALE
# ─────────────────────────────────────────────

with st.expander("🧩 Note pédagogique : dimension ou variable ?", expanded=False):
    st.write(
        """
        Une **dimension** est un grand domaine retenu pour évaluer la situation sociale ou économique d'une commune.

        Exemples :
        - Revenu
        - Santé
        - Emploi
        - Logement
        - Éducation

        Une **variable** est une donnée statistique précise utilisée pour mesurer une dimension.

        Exemple dans la dimension revenu :
        - Revenu médian
        - Taux de pauvreté au seuil de 60 % du revenu médian
        - Rapport interdécile D9/D1

        Le choix des dimensions et des variables n'est pas neutre.
        Il reflète une certaine définition de ce que l'on considère comme une situation sociale favorable ou défavorable.
        C'est pourquoi ce prototype permet de discuter ces choix collectivement.
        """
    )
