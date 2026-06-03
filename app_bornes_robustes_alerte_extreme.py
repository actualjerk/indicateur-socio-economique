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
    .extreme-warning {
        background-color: #ffecec;
        color: #8a1f1f;
        border-left: 6px solid #d62728;
        border-radius: 10px;
        padding: 12px 14px;
        margin-top: 8px;
        margin-bottom: 8px;
        font-size: 0.95rem;
        font-weight: 500;
    }
    .extreme-warning strong {
        color: #7a0000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# DONNÉES : DIMENSIONS, VARIABLES ET BORNES
# ─────────────────────────────────────────────

DIMENSIONS = {
    "Revenus et inégalités": {
        "description": "Cette dimension mesure le niveau de vie, la pauvreté et les inégalités monétaires.",
        "variables": {
            "Revenu médian": {
                "min": 20460,
                "max": 34765,
                "valeur": 27612,
                "unite": "€",
                "sens": "positif",
                "source": "Filosofi 2021, communes d’Île-de-France — normalisation robuste P5-P95",
                "commune_min": "Commune la plus proche du P5 : Étampes (91223)",
                "commune_max": "Commune la plus proche du P95 : Saint-Rémy-lès-Chevreuse (78575)"
            },
            "Taux de pauvreté au seuil de 60 % du revenu médian": {
                "min": 5.0,
                "max": 29.0,
                "valeur": 17.0,
                "unite": "%",
                "sens": "negatif",
                "source": "Filosofi 2021, communes d’Île-de-France — normalisation robuste P5-P95",
                "commune_min": "Commune la plus proche du P5 : Bois-le-Roi (77037)",
                "commune_max": "Commune la plus proche du P95 : Aulnay-sous-Bois (93005)"
            },
            "Rapport interdécile du revenu disponible par unité de consommation D9/D1": {
                "min": 2.5,
                "max": 4.5,
                "valeur": 3.5,
                "unite": "",
                "sens": "negatif",
                "source": "Filosofi 2021, communes d’Île-de-France — normalisation robuste P5-P95",
                "commune_min": "Commune la plus proche du P5 : Boissy-le-Châtel (77042)",
                "commune_max": "Commune la plus proche du P95 : Bois-Colombes (92009)"
            },
        },
    },

    "Éducation": {
        "description": "Cette dimension mesure le niveau de formation, la scolarisation et l'accès aux diplômes.",
        "variables": {
            "Part des diplômés du supérieur parmi les personnes de 15 ans ou plus non scolarisées": {
                "min": 20.1,
                "max": 61.0,
                "valeur": 40.5,
                "unite": "%",
                "sens": "positif",
                "source": "INSEE, Recensement de la population 2021, base communale Diplômes-Formation, communes d’Île-de-France — normalisation robuste P5-P95",
                "commune_min": "Commune la plus proche du P5 : Saint-Mars-Vieux-Maisons (77421)",
                "commune_max": "Commune la plus proche du P95 : Davron (78196)"
            },
            "Part des actifs peu ou pas diplômés parmi les actifs": {
                "min": 6.2,
                "max": 22.8,
                "valeur": 14.5,
                "unite": "%",
                "sens": "negatif",
                "source": "INSEE, Recensement de la population 2021, base communale Emploi-Population active, communes d’Île-de-France — normalisation robuste P5-P95",
                "commune_min": "Commune la plus proche du P5 : Vieille-Église-en-Yvelines (78655)",
                "commune_max": "Commune la plus proche du P95 : La Ferté-sous-Jouarre (77183)"
            },
            "Taux de scolarisation": {
                "min": 50,
                "max": 99,
                "valeur": 80,
                "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter",
                "commune_max": "À documenter"
            },
        },
    },

    "Emploi": {
        "description": "Cette dimension mesure l'accès à l'emploi, le chômage et la stabilité professionnelle.",
        "variables": {
            "Taux de chômage au sens du recensement des 15-64 ans": {
                "min": 4.9,
                "max": 15.3,
                "valeur": 10.1,
                "unite": "%",
                "sens": "negatif",
                "source": "INSEE, Recensement de la population 2021, base communale Emploi-Population active, communes d’Île-de-France — normalisation robuste P5-P95",
                "commune_min": "Commune la plus proche du P5 : Neauphle-le-Vieux (78443)",
                "commune_max": "Commune la plus proche du P95 : Gouaix (77208)"
            },
            "Part des contrats précaires": {
                "min": 5,
                "max": 40,
                "valeur": 20,
                "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter",
                "commune_max": "À documenter"
            },
            "Taux d'activité": {
                "min": 45,
                "max": 85,
                "valeur": 70,
                "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter",
                "commune_max": "À documenter"
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
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter",
                "commune_max": "À documenter"
            },
            "Médecins pour 1000 habitants": {
                "min": 0,
                "max": 10,
                "valeur": 3,
                "unite": "",
                "sens": "positif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter",
                "commune_max": "À documenter"
            },
            "Mortalité prématurée": {
                "min": 100,
                "max": 500,
                "valeur": 250,
                "unite": "pour 100 000",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter",
                "commune_max": "À documenter"
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
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter",
                "commune_max": "À documenter"
            },
            "Mal-logement": {
                "min": 0,
                "max": 30,
                "valeur": 10,
                "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter",
                "commune_max": "À documenter"
            },
            "Surpopulation des logements": {
                "min": 0,
                "max": 25,
                "valeur": 8,
                "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter",
                "commune_max": "À documenter"
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
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter",
                "commune_max": "À documenter"
            },
            "Familles monoparentales": {
                "min": 5,
                "max": 40,
                "valeur": 18,
                "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter",
                "commune_max": "À documenter"
            },
            "Criminalité pour 1000 habitants": {
                "min": 0,
                "max": 100,
                "valeur": 35,
                "unite": "",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter",
                "commune_max": "À documenter"
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
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter",
                "commune_max": "À documenter"
            },
            "Pollution de l'air": {
                "min": 5,
                "max": 40,
                "valeur": 20,
                "unite": "µg/m³",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter",
                "commune_max": "À documenter"
            },
            "Densité de population": {
                "min": 50,
                "max": 25000,
                "valeur": 5000,
                "unite": "hab/km²",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter",
                "commune_max": "À documenter"
            },
        },
    },
}

# ─────────────────────────────────────────────
# BORNES RÉELLES OBSERVÉES
# ─────────────────────────────────────────────
# Les bornes robustes P5-P95 sont stockées dans DIMENSIONS[...]["min"] et ["max"].
# Les bornes réelles ci-dessous ne servent pas au calcul : elles sont affichées uniquement
# dans la partie 4 « Détail du calcul par variable » pour garder la mémoire des extrêmes.

BORNES_REELLES = {
    "Revenu médian": {
        "min": 14790,
        "max": 48010,
        "commune_min": "Grigny (91286)",
        "commune_max": "Neuilly-sur-Seine (92051)",
    },
    "Taux de pauvreté au seuil de 60 % du revenu médian": {
        "min": 5,
        "max": 44,
        "commune_min": "28 communes, dont Bois-le-Roi (77037)",
        "commune_max": "Grigny (91286)",
    },
    "Rapport interdécile du revenu disponible par unité de consommation D9/D1": {
        "min": 2.2,
        "max": 8.1,
        "commune_min": "Moncourt-Fromonville (77302)",
        "commune_max": "Neuilly-sur-Seine (92051)",
    },
    "Part des diplômés du supérieur parmi les personnes de 15 ans ou plus non scolarisées": {
        "min": 9.4,
        "max": 74.2,
        "commune_min": "Mouy-sur-Seine (77325)",
        "commune_max": "Saint-Aubin (91538)",
    },
    "Part des actifs peu ou pas diplômés parmi les actifs": {
        "min": 1.0,
        "max": 47.0,
        "commune_min": "Milon-la-Chapelle (78406)",
        "commune_max": "Hautefeuille (77224)",
    },
    "Taux de chômage au sens du recensement des 15-64 ans": {
        "min": 0.0,
        "max": 23.0,
        "commune_min": "2 communes, dont Montenils (77304)",
        "commune_max": "La Courneuve (93027)",
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


def format_nombre(valeur):
    """
    Formate les nombres pour l'affichage :
    - pas de zéro inutile après la virgule ;
    - deux décimales maximum si nécessaire ;
    - espace comme séparateur de milliers ;
    - virgule décimale en français.
    """
    if valeur is None or valeur == "":
        return ""

    if isinstance(valeur, str):
        return valeur

    try:
        nombre = float(valeur)
    except (TypeError, ValueError):
        return str(valeur)

    if np.isnan(nombre):
        return ""

    if abs(nombre - round(nombre)) < 1e-9:
        return f"{int(round(nombre)):,}".replace(",", " ")

    texte = f"{nombre:,.2f}".replace(",", " ").replace(".", ",")
    texte = texte.rstrip("0").rstrip(",")
    return texte


def format_dataframe(df):
    """Prépare un tableau d'affichage sans zéros inutiles après la virgule."""
    df_affichage = df.copy()
    colonnes_a_formater = [
        "Valeur",
        "Borne robuste min",
        "Borne robuste max",
        "Borne réelle min",
        "Borne réelle max",
        "Poids variable",
        "Score normalisé 0-100",
    ]

    for colonne in colonnes_a_formater:
        if colonne in df_affichage.columns:
            df_affichage[colonne] = df_affichage[colonne].apply(format_nombre)

    return df_affichage


def statut_valeur_extreme(valeur, borne_robuste_min, borne_robuste_max):
    """Indique si la valeur saisie se situe en dehors des bornes robustes P5-P95."""
    if valeur < borne_robuste_min:
        return "Extrême sous P5"
    if valeur > borne_robuste_max:
        return "Extrême au-dessus du P95"
    return "Dans l'intervalle robuste P5-P95"


def afficher_alerte_valeur_extreme(nom_variable, valeur, infos):
    """Affiche un message rouge si la valeur réelle est hors bornes robustes."""
    borne_min = infos["min"]
    borne_max = infos["max"]
    unite = infos.get("unite", "")

    if valeur < borne_min:
        st.markdown(
            f'''
            <div class="extreme-warning">
            <strong>Valeur réelle extrême :</strong> la valeur saisie pour <strong>{nom_variable}</strong>
            est de <strong>{format_nombre(valeur)} {unite}</strong>, donc elle est située
            <strong>sous la borne robuste P5</strong> de <strong>{format_nombre(borne_min)} {unite}</strong>.
            Cela signifie que la commune fait partie des situations les plus atypiques pour cette variable.
            Le score est plafonné afin qu'une valeur très extrême ne déforme pas l'ensemble de l'indicateur.
            </div>
            ''',
            unsafe_allow_html=True
        )
    elif valeur > borne_max:
        st.markdown(
            f'''
            <div class="extreme-warning">
            <strong>Valeur réelle extrême :</strong> la valeur saisie pour <strong>{nom_variable}</strong>
            est de <strong>{format_nombre(valeur)} {unite}</strong>, donc elle est située
            <strong>au-dessus de la borne robuste P95</strong> de <strong>{format_nombre(borne_max)} {unite}</strong>.
            Cela signifie que la commune fait partie des situations les plus atypiques pour cette variable.
            Le score est plafonné afin qu'une valeur très extrême ne déforme pas l'ensemble de l'indicateur.
            </div>
            ''',
            unsafe_allow_html=True
        )


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

            bornes_reelles = BORNES_REELLES.get(nom_variable, {})

            resultats_variables.append({
                "Dimension": nom_dimension,
                "Variable": nom_variable,
                "Valeur": valeur,
                "Unité": infos.get("unite", ""),
                "Borne robuste min": infos["min"],
                "Commune proche P5": infos.get("commune_min", ""),
                "Borne robuste max": infos["max"],
                "Commune proche P95": infos.get("commune_max", ""),
                "Borne réelle min": bornes_reelles.get("min", "À documenter"),
                "Commune min réelle": bornes_reelles.get("commune_min", "À documenter"),
                "Borne réelle max": bornes_reelles.get("max", "À documenter"),
                "Commune max réelle": bornes_reelles.get("commune_max", "À documenter"),
                "Statut de la valeur": statut_valeur_extreme(valeur, infos["min"], infos["max"]),
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
            bornes_reelles = BORNES_REELLES.get(nom_variable, {})

            lignes.append({
                "Dimension": nom_dimension,
                "Variable": nom_variable,
                "Borne robuste min": infos["min"],
                "Commune proche P5": infos.get("commune_min", ""),
                "Borne robuste max": infos["max"],
                "Commune proche P95": infos.get("commune_max", ""),
                "Borne réelle min": bornes_reelles.get("min", "À documenter"),
                "Commune min réelle": bornes_reelles.get("commune_min", "À documenter"),
                "Borne réelle max": bornes_reelles.get("max", "À documenter"),
                "Commune max réelle": bornes_reelles.get("commune_max", "À documenter"),
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
        L'indicateur est construit en trois étapes : choix des dimensions, choix des variables, puis pondération.

        Les variables déjà documentées utilisent une **normalisation robuste par percentiles**.
        Cela signifie que le calcul ne prend pas directement la commune la plus basse et la commune la plus haute
        comme bornes principales. À la place, on utilise :

        - le **5e percentile** comme borne basse ;
        - le **95e percentile** comme borne haute.

        Exemple avec le **taux de pauvreté** :
        - les 5 % des communes les moins pauvres sont sous environ **5 %** ;
        - les 5 % des communes les plus pauvres sont au-dessus d'environ **29 %**.

        Le score est donc calculé entre ces deux bornes robustes. Cela évite qu'une commune très atypique écrase
        toutes les autres dans le calcul. Les bornes réelles restent toutefois visibles dans la partie
        **4. Détail du calcul par variable**.

        Si une valeur réelle saisie est **inférieure au P5** ou **supérieure au P95**, l'application l'indique en rouge.
        Cela signifie que la commune est dans une situation **extrême** par rapport à la majorité des communes.
        La valeur réelle n'est pas supprimée : elle reste affichée dans le détail, mais le score est **plafonné**
        à 0 ou 100 pour éviter qu'une valeur très atypique déforme l'ensemble de l'indicateur.

        **1. Choix des dimensions**  
        Une dimension correspond à un grand domaine de la réalité sociale ou économique : revenus et inégalités, santé, emploi, logement, etc.

        **2. Choix des variables**  
        Une variable est une donnée précise utilisée pour mesurer une dimension.  
        Par exemple, dans la dimension revenus et inégalités, on peut retenir le revenu médian,
        le taux de pauvreté au seuil de 60 % du revenu médian ou le rapport interdécile D9/D1.

        **3. Pondération**  
        Les élèves peuvent ensuite décider du poids de chaque variable et du poids de chaque dimension.
        Cela permet de discuter démocratiquement de ce qui compte le plus dans l'indicateur.
        """
    )

with st.expander("📌 Voir toutes les dimensions et variables disponibles", expanded=False):
    st.dataframe(format_dataframe(tableau_variables()), use_container_width=True)

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

    st.header("📌 Bornes robustes P5-P95")
    st.write("**Revenu médian** : 20 460 € → 34 765 €")
    st.write("**Taux de pauvreté au seuil de 60 %** : 5 % → 29 %")
    st.write("**Rapport D9/D1** : 2,5 → 4,5")
    st.write("**Diplômés du supérieur** : 20,1 % → 61 %")
    st.write("**Actifs peu ou pas diplômés** : 6,2 % → 22,8 %")
    st.write("**Taux de chômage** : 4,9 % → 15,3 %")

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
                    f"Borne robuste min : {format_nombre(infos['min'])} {infos.get('unite', '')} | "
                    f"Borne robuste max : {format_nombre(infos['max'])} {infos.get('unite', '')}"
                )

                if actif:
                    variables_choisies[nom_dimension].append(nom_variable)

                    col1, col2 = st.columns([2, 1])

                    with col1:
                        bornes_reelles_saisie = BORNES_REELLES.get(nom_variable, {})
                        min_saisie = float(bornes_reelles_saisie.get("min", infos["min"]))
                        max_saisie = float(bornes_reelles_saisie.get("max", infos["max"]))

                        step = 0.1 if isinstance(infos["min"], float) or isinstance(infos["max"], float) else 1.0
                        format_affichage = "%.1f" if step == 0.1 else "%.0f"
                        unite_label = f"({infos.get('unite')})" if infos.get("unite") else ""

                        valeurs[nom_variable] = st.number_input(
                            label=f"Valeur observée {unite_label}",
                            min_value=min_saisie,
                            max_value=max_saisie,
                            value=float(infos["valeur"]),
                            step=float(step),
                            format=format_affichage,
                            key=f"valeur_{nom_dimension}_{nom_variable}"
                        )

                        afficher_alerte_valeur_extreme(
                            nom_variable=nom_variable,
                            valeur=valeurs[nom_variable],
                            infos=infos
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
        Les bornes robustes P5-P95 sont celles utilisées pour calculer le score.
        Les bornes réelles sont affichées ici seulement pour conserver l'information sur les valeurs extrêmes observées.
        """
    )

    colonnes_detail = [
        "Dimension",
        "Variable",
        "Valeur",
        "Unité",
        "Borne robuste min",
        "Commune proche P5",
        "Borne robuste max",
        "Commune proche P95",
        "Borne réelle min",
        "Commune min réelle",
        "Borne réelle max",
        "Commune max réelle",
        "Statut de la valeur",
        "Poids variable",
        "Score normalisé 0-100",
        "Source"
    ]

    st.dataframe(
        format_dataframe(df_resultats[colonnes_detail]),
        use_container_width=True
    )

    if "Revenus et inégalités" in scores_dimensions:
        st.subheader("Zoom sur la dimension Revenus et inégalités")

        df_revenus = df_resultats[df_resultats["Dimension"] == "Revenus et inégalités"][
            [
                "Variable",
                "Valeur",
                "Unité",
                "Borne robuste min",
                "Commune proche P5",
                "Borne robuste max",
                "Commune proche P95",
                "Borne réelle min",
                "Commune min réelle",
                "Borne réelle max",
                "Commune max réelle",
                "Statut de la valeur",
                "Score normalisé 0-100",
                "Source"
            ]
        ]

        st.dataframe(format_dataframe(df_revenus), use_container_width=True)

        with st.expander("🧠 Pourquoi le rapport D9/D1 réduit-il le score ?", expanded=False):
            st.write(
                """
                Le rapport interdécile D9/D1 mesure l'écart entre les 10 % les plus aisés et les 10 % les plus modestes.

                Un rapport D9/D1 élevé signifie que les écarts de revenus sont importants.
                Dans un indicateur de santé sociale ou socio-économique, cela correspond à une situation moins favorable.

                C'est pourquoi, dans le calcul, plus le rapport D9/D1 augmente, plus le score de cette variable diminue.
                """
            )

    if "Éducation" in scores_dimensions:
        st.subheader("Zoom sur la dimension Éducation")

        df_education = df_resultats[df_resultats["Dimension"] == "Éducation"][
            [
                "Variable",
                "Valeur",
                "Unité",
                "Borne robuste min",
                "Commune proche P5",
                "Borne robuste max",
                "Commune proche P95",
                "Borne réelle min",
                "Commune min réelle",
                "Borne réelle max",
                "Commune max réelle",
                "Statut de la valeur",
                "Score normalisé 0-100",
                "Source"
            ]
        ]

        st.dataframe(format_dataframe(df_education), use_container_width=True)

        with st.expander("🧠 Pourquoi la part des actifs peu ou pas diplômés réduit-elle le score ?", expanded=False):
            st.write(
                """
                La variable « Part des actifs peu ou pas diplômés parmi les actifs » mesure la part des actifs
                sans diplôme, avec un CEP, ou avec le BEPC / brevet des collèges / DNB.

                Une valeur élevée indique une plus forte proportion d'actifs faiblement diplômés.
                Dans un indicateur socio-économique, cette situation est interprétée comme moins favorable.

                C'est pourquoi, dans le calcul, plus cette part augmente, plus le score de cette variable diminue.
                """
            )

    if "Emploi" in scores_dimensions:
        st.subheader("Zoom sur la dimension Emploi")

        df_emploi = df_resultats[df_resultats["Dimension"] == "Emploi"][
            [
                "Variable",
                "Valeur",
                "Unité",
                "Borne robuste min",
                "Commune proche P5",
                "Borne robuste max",
                "Commune proche P95",
                "Borne réelle min",
                "Commune min réelle",
                "Borne réelle max",
                "Commune max réelle",
                "Statut de la valeur",
                "Score normalisé 0-100",
                "Source"
            ]
        ]

        st.dataframe(format_dataframe(df_emploi), use_container_width=True)

        with st.expander("🧠 Pourquoi le taux de chômage réduit-il le score ?", expanded=False):
            st.write(
                """
                Le taux de chômage au sens du recensement rapporte les chômeurs de 15 à 64 ans
                à l'ensemble des actifs de 15 à 64 ans.

                Une valeur élevée indique une plus forte difficulté d'accès à l'emploi.
                Dans un indicateur socio-économique, cette situation est interprétée comme moins favorable.

                C'est pourquoi, dans le calcul, plus le taux de chômage augmente, plus le score de cette variable diminue.
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
        - Revenus et inégalités
        - Santé
        - Emploi
        - Logement
        - Éducation

        Une **variable** est une donnée statistique précise utilisée pour mesurer une dimension.

        Exemple dans la dimension revenus et inégalités :
        - Revenu médian
        - Taux de pauvreté au seuil de 60 % du revenu médian
        - Rapport interdécile D9/D1

        Exemples dans la dimension éducation :
        - Part des diplômés du supérieur parmi les personnes de 15 ans ou plus non scolarisées
        - Part des actifs peu ou pas diplômés parmi les actifs

        Le choix des dimensions et des variables n'est pas neutre.
        Il reflète une certaine définition de ce que l'on considère comme une situation sociale favorable ou défavorable.
        C'est pourquoi ce prototype permet de discuter ces choix collectivement.
        """
    )
