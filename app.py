# app.py
# Prototype pédagogique d'indicateur socio-économique communal en Île-de-France
# Version conservant l'esprit de l'ancienne application :
# - choix des dimensions et variables par cases à cocher ;
# - pondérations ;
# - normalisation sur 100 ;
# - détail du calcul par variable ;
# - ajout local : explication des bornes par percentiles sous chaque variable.

import math
from typing import Dict, List

import pandas as pd
import streamlit as st


# -----------------------------------------------------------------------------
# Configuration de la page
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Indicateur socio-économique communal",
    page_icon="📊",
    layout="wide",
)


# -----------------------------------------------------------------------------
# Style visuel
# -----------------------------------------------------------------------------

st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 800;
            color: #0f3d75;
            margin-bottom: 0.15rem;
        }
        .subtitle {
            font-size: 1.05rem;
            color: #475569;
            margin-bottom: 1.2rem;
        }
        .bloc-intro {
            background-color: #f8fafc;
            border: 1px solid #dbeafe;
            border-left: 5px solid #2563eb;
            border-radius: 0.7rem;
            padding: 0.9rem 1rem;
            margin-bottom: 1rem;
            line-height: 1.5;
        }
        .dimension-header {
            background: linear-gradient(90deg, #dbeafe, #eff6ff);
            color: #1e3a8a;
            font-size: 1.25rem;
            font-weight: 750;
            padding: 0.7rem 0.9rem;
            border-left: 6px solid #2563eb;
            border-radius: 0.6rem;
            margin-top: 1.2rem;
            margin-bottom: 0.8rem;
        }
        .variable-title {
            color: #1d4ed8;
            font-size: 1.08rem;
            font-weight: 750;
            margin-top: 0.3rem;
            margin-bottom: 0.2rem;
        }
        .variable-help {
            color: #475569;
            font-size: 0.93rem;
            line-height: 1.4;
            margin-bottom: 0.4rem;
        }
        .percentile-box {
            background-color: #f8fbff;
            border-left: 4px solid #2563eb;
            padding: 10px 13px;
            border-radius: 8px;
            margin-top: 6px;
            margin-bottom: 12px;
            font-size: 0.92rem;
            line-height: 1.45;
            color: #1f2937;
        }
        .extreme-box {
            background-color: #fff1f2;
            border-left: 5px solid #dc2626;
            padding: 10px 13px;
            border-radius: 8px;
            margin-top: 6px;
            margin-bottom: 12px;
            font-size: 0.92rem;
            line-height: 1.45;
            color: #7f1d1d;
        }
        .detail-box {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 0.7rem;
            padding: 0.8rem 0.9rem;
            margin-top: 0.5rem;
            margin-bottom: 0.8rem;
            line-height: 1.45;
        }
        .small-muted {
            color: #64748b;
            font-size: 0.9rem;
        }
        .score-card {
            background-color: #ffffff;
            border: 1px solid #dbeafe;
            border-radius: 0.9rem;
            padding: 1rem;
            box-shadow: 0 1px 4px rgba(15, 23, 42, 0.06);
            margin-bottom: 1rem;
        }
        .score-big {
            color: #1d4ed8;
            font-size: 2.4rem;
            font-weight: 850;
            line-height: 1.1;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Données de base : dimensions et variables
# -----------------------------------------------------------------------------
# Important : dans ce dictionnaire, les champs "min" et "max" correspondent
# maintenant aux bornes par percentiles P5 et P95 utilisées pour le calcul.
# Les bornes réelles sont conservées uniquement pour l'interprétation.

DIMENSIONS: Dict[str, Dict] = {
    "Revenus et inégalités": {
        "description": "Dimension centrée sur le niveau de vie, la pauvreté et les inégalités monétaires.",
        "variables": {
            "Revenu médian par unité de consommation": {
                "description": (
                    "Le revenu médian partage la population en deux : 50 % des personnes vivent "
                    "dans un ménage dont le niveau de vie est inférieur à cette valeur, et 50 % "
                    "dans un ménage dont le niveau de vie est supérieur."
                ),
                "unite": "€",
                "min": 20460,
                "max": 34765,
                "valeur_defaut": 29730,
                "sens": "positif",
                "source": "Filosofi 2021 - Insee-DGFIP-Cnaf-Cnav-CCMSA / Observatoire des territoires, variable med_disp",
                "calcul_variable": "x = médiane du revenu disponible par unité de consommation",
                "minimum_reel": 14790,
                "maximum_reel": 48010,
                "commune_min_reel": "Grigny (91286)",
                "commune_max_reel": "Neuilly-sur-Seine (92051)",
                "decimales": 0,
            },
            "Rapport interdécile D9/D1 du revenu disponible": {
                "description": (
                    "Le rapport D9/D1 mesure l'écart entre les 10 % les plus aisés et les 10 % "
                    "les moins aisés. Plus il est élevé, plus les inégalités de revenu sont fortes."
                ),
                "unite": "",
                "min": 2.5,
                "max": 4.5,
                "valeur_defaut": 4.2,
                "sens": "negatif",
                "source": "Filosofi 2021 - Observatoire des territoires, variable rap_interdec",
                "calcul_variable": "x = D9 / D1",
                "minimum_reel": 2.2,
                "maximum_reel": 8.1,
                "commune_min_reel": "Moncourt-Fromonville (77302)",
                "commune_max_reel": "Neuilly-sur-Seine (92051)",
                "decimales": 2,
            },
            "Taux de pauvreté au seuil de 60 % du revenu médian": {
                "description": (
                    "Le taux de pauvreté mesure la part des personnes vivant avec un niveau de vie "
                    "inférieur à 60 % du niveau de vie médian. Plus il est élevé, plus la situation "
                    "sociale est défavorable."
                ),
                "unite": "%",
                "min": 5,
                "max": 29,
                "valeur_defaut": 16,
                "sens": "negatif",
                "source": "Filosofi 2021 - Insee-DGFIP-Cnaf-Cnav-CCMSA / Observatoire des territoires, variable tx_pauv_60",
                "calcul_variable": "x = taux de pauvreté au seuil de 60 % du revenu médian",
                "minimum_reel": 5,
                "maximum_reel": 44,
                "commune_min_reel": "28 communes, dont Bois-le-Roi (77037)",
                "commune_max_reel": "Grigny (91286)",
                "decimales": 1,
            },
        },
    },
    "Emploi": {
        "description": "Dimension centrée sur l'accès à l'emploi et la fragilité sur le marché du travail.",
        "variables": {
            "Taux de chômage au sens du recensement des 15-64 ans": {
                "description": (
                    "Le taux de chômage rapporte le nombre de chômeurs à la population active "
                    "des 15-64 ans. Plus il est élevé, plus la situation de l'emploi est défavorable."
                ),
                "unite": "%",
                "min": 4.8812,
                "max": 15.2901,
                "valeur_defaut": 10.7472,
                "sens": "negatif",
                "source": "INSEE, Recensement de la population 2021, base communale Emploi-Population active, France hors Mayotte, géographie au 01/01/2024",
                "calcul_variable": "x = P21_CHOM1564 / P21_ACT1564 × 100 (taux de chômage au sens du recensement)",
                "minimum_reel": 0,
                "maximum_reel": 22.9971,
                "commune_min_reel": "2 communes, dont Montenils (77304)",
                "commune_max_reel": "La Courneuve (93027)",
                "decimales": 2,
            },
        },
    },
    "Éducation": {
        "description": "Dimension centrée sur le niveau de diplôme et les fragilités scolaires dans la population active.",
        "variables": {
            "Part des actifs peu ou pas diplômés parmi les actifs": {
                "description": (
                    "Cette variable mesure la part des actifs ayant un faible niveau de diplôme "
                    "ou aucun diplôme. Plus elle est élevée, plus la situation éducative et sociale "
                    "est fragile."
                ),
                "unite": "%",
                "min": 6.1995,
                "max": 22.7569,
                "valeur_defaut": 8.8045,
                "sens": "negatif",
                "source": "INSEE, Recensement de la population 2021, base communale Emploi-Population active, France hors Mayotte, géographie au 01/01/2024",
                "calcul_variable": "x = (P21_ACT_DIPLMIN + P21_ACT_BEPC) / P21_ACT1564 × 100",
                "minimum_reel": 0.9679,
                "maximum_reel": 46.9962,
                "commune_min_reel": "Milon-la-Chapelle (78406)",
                "commune_max_reel": "Hautefeuille (77224)",
                "decimales": 2,
            },
        },
    },
}


# -----------------------------------------------------------------------------
# Fonctions de formatage et de calcul
# -----------------------------------------------------------------------------

def format_nombre(valeur, decimales: int = 2) -> str:
    """Format français : espaces pour les milliers, virgule décimale, sans zéros inutiles."""
    try:
        valeur_float = float(valeur)
    except Exception:
        return str(valeur)

    if math.isnan(valeur_float):
        return "—"

    if decimales == 0 or valeur_float.is_integer():
        texte = f"{valeur_float:,.0f}".replace(",", " ")
    else:
        texte = f"{valeur_float:,.{decimales}f}".replace(",", " ").replace(".", ",")
        texte = texte.rstrip("0").rstrip(",")

    return texte


def format_valeur(valeur, unite: str = "", decimales: int = 2) -> str:
    texte = format_nombre(valeur, decimales)
    return f"{texte} {unite}".strip()


def normaliser_score(valeur: float, borne_basse: float, borne_haute: float, sens: str) -> Dict[str, float]:
    """Calcule le score brut et le score final plafonné entre 0 et 100."""
    amplitude = borne_haute - borne_basse
    if amplitude == 0:
        return {"score_brut": 0.0, "score_final": 0.0}

    if sens == "positif":
        score_brut = ((valeur - borne_basse) / amplitude) * 100
    else:
        score_brut = ((borne_haute - valeur) / amplitude) * 100

    score_final = max(0, min(100, score_brut))
    return {"score_brut": score_brut, "score_final": score_final}


def afficher_bornes_percentiles(var: Dict) -> None:
    """Affiche l'explication succincte et précise sous chaque variable."""
    unite = var.get("unite", "")
    decimales = var.get("decimales", 2)
    borne_basse_txt = format_valeur(var["min"], unite, decimales)
    borne_haute_txt = format_valeur(var["max"], unite, decimales)

    if var.get("sens") == "negatif":
        phrase_score = (
            "Comme cette variable mesure une difficulté sociale, le score est inversé : "
            "une valeur faible est favorable et une valeur élevée est défavorable."
        )
    else:
        phrase_score = (
            "Comme cette variable est favorable, plus la valeur est élevée, plus le score augmente."
        )

    st.markdown(
        f"""
        <div class="percentile-box">
            <strong>Bornes par percentiles utilisées pour le calcul</strong><br>
            La borne basse correspond au <strong>5e percentile</strong> : environ 5 % des communes
            ont une valeur inférieure à <strong>{borne_basse_txt}</strong>.<br>
            La borne haute correspond au <strong>95e percentile</strong> : environ 5 % des communes
            ont une valeur supérieure à <strong>{borne_haute_txt}</strong>.<br>
            Le score est calculé sur <strong>100</strong> entre ces deux bornes. {phrase_score}
        </div>
        """,
        unsafe_allow_html=True,
    )


def afficher_alerte_valeur_extreme(nom_variable: str, var: Dict, valeur: float, score_final: float) -> None:
    """Signale en rouge les valeurs situées hors des bornes par percentiles."""
    unite = var.get("unite", "")
    decimales = var.get("decimales", 2)
    valeur_txt = format_valeur(valeur, unite, decimales)
    p5_txt = format_valeur(var["min"], unite, decimales)
    p95_txt = format_valeur(var["max"], unite, decimales)
    score_txt = format_nombre(score_final, 2)

    if valeur < var["min"]:
        st.markdown(
            f"""
            <div class="extreme-box">
                <strong>Valeur réelle extrême basse.</strong><br>
                Pour la variable <strong>{nom_variable}</strong>, la valeur saisie
                (<strong>{valeur_txt}</strong>) est inférieure à la borne par percentile basse
                (<strong>{p5_txt}</strong>). Le score est donc plafonné à
                <strong>{score_txt} / 100</strong>, mais la valeur réelle reste affichée pour l’interprétation.
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif valeur > var["max"]:
        st.markdown(
            f"""
            <div class="extreme-box">
                <strong>Valeur réelle extrême haute.</strong><br>
                Pour la variable <strong>{nom_variable}</strong>, la valeur saisie
                (<strong>{valeur_txt}</strong>) est supérieure à la borne par percentile haute
                (<strong>{p95_txt}</strong>). Le score est donc plafonné à
                <strong>{score_txt} / 100</strong>, mais la valeur réelle reste affichée pour l’interprétation.
            </div>
            """,
            unsafe_allow_html=True,
        )


def formule_normalisation(var: Dict, valeur: float, score_brut: float, score_final: float) -> str:
    """Produit une explication textuelle du calcul appliqué."""
    unite = var.get("unite", "")
    decimales = var.get("decimales", 2)
    p5 = var["min"]
    p95 = var["max"]
    amplitude = p95 - p5

    valeur_txt = format_valeur(valeur, unite, decimales)
    p5_txt = format_valeur(p5, unite, decimales)
    p95_txt = format_valeur(p95, unite, decimales)
    amplitude_txt = format_valeur(amplitude, unite, decimales)

    if var["sens"] == "positif":
        formule = (
            f"Score brut = (({valeur_txt} - {p5_txt}) / ({p95_txt} - {p5_txt})) × 100  \n"
            f"= (({valeur_txt} - {p5_txt}) / {amplitude_txt}) × 100"
        )
    else:
        formule = (
            f"Score brut = (({p95_txt} - {valeur_txt}) / ({p95_txt} - {p5_txt})) × 100  \n"
            f"= (({p95_txt} - {valeur_txt}) / {amplitude_txt}) × 100"
        )

    return (
        f"{formule}\n\n"
        f"Score brut = {format_nombre(score_brut, 2)} / 100  \n"
        f"Score final plafonné = {format_nombre(score_final, 2)} / 100"
    )


# -----------------------------------------------------------------------------
# En-tête
# -----------------------------------------------------------------------------

st.markdown('<div class="main-title">Indicateur socio-économique communal</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Prototype pédagogique participatif pour construire un indicateur synthétique à l’échelle communale en Île-de-France.</div>',
    unsafe_allow_html=True,
)

with st.expander("Comment fonctionne cet outil ?", expanded=False):
    st.markdown(
        """
        Cet outil transforme plusieurs variables socio-économiques en scores comparables sur **100**.
        Comme les variables n'ont pas les mêmes unités, elles sont normalisées avant d'être agrégées.

        La normalisation utilisée ici repose sur des **bornes par percentiles** :

        - le **5e percentile** sert de borne basse ;
        - le **95e percentile** sert de borne haute.

        Ces bornes permettent de limiter l'effet des valeurs extrêmes. Les valeurs situées en dehors de ces bornes
        ne sont pas supprimées : elles restent visibles dans le détail du calcul, mais leur score est plafonné à
        **0** ou à **100**.
        """
    )


# -----------------------------------------------------------------------------
# Barre latérale : commune, sélection et pondérations
# -----------------------------------------------------------------------------

st.sidebar.title("Paramètres")
commune = st.sidebar.text_input("Nom de la commune étudiée", value="Paris")

st.sidebar.markdown("---")
st.sidebar.subheader("1. Sélectionner les dimensions")

selection_dimensions: Dict[str, bool] = {}
selection_variables: Dict[str, bool] = {}

for dimension in DIMENSIONS.keys():
    selection_dimensions[dimension] = st.sidebar.checkbox(dimension, value=True, key=f"dim_{dimension}")

st.sidebar.markdown("---")
st.sidebar.subheader("2. Pondérer les dimensions")

poids_dimensions: Dict[str, float] = {}
for dimension in DIMENSIONS.keys():
    if selection_dimensions[dimension]:
        poids_dimensions[dimension] = st.sidebar.slider(
            f"Poids : {dimension}",
            min_value=0,
            max_value=100,
            value=100,
            step=5,
            key=f"poids_{dimension}",
        )

st.sidebar.caption("Les poids sont utilisés de manière relative entre les dimensions sélectionnées.")


# -----------------------------------------------------------------------------
# Saisie des valeurs par variable
# -----------------------------------------------------------------------------

st.markdown(
    f"""
    <div class="bloc-intro">
        <strong>Commune étudiée :</strong> {commune}<br>
        Sélectionnez les variables, modifiez éventuellement les valeurs, puis observez le score obtenu.
    </div>
    """,
    unsafe_allow_html=True,
)

valeurs_saisies: Dict[str, float] = {}
resultats_variables: Dict[str, Dict] = {}
variables_selectionnees: List[str] = []

for dimension, contenu in DIMENSIONS.items():
    if not selection_dimensions[dimension]:
        continue

    st.markdown(f'<div class="dimension-header">{dimension}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="small-muted">{contenu["description"]}</div>', unsafe_allow_html=True)

    for nom_variable, var in contenu["variables"].items():
        col_check, col_input = st.columns([0.08, 0.92])
        with col_check:
            checked = st.checkbox("", value=True, key=f"check_{dimension}_{nom_variable}")
        with col_input:
            st.markdown(f'<div class="variable-title">{nom_variable}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="variable-help">{var["description"]}</div>', unsafe_allow_html=True)

        if not checked:
            continue

        variables_selectionnees.append(nom_variable)
        selection_variables[nom_variable] = True

        col_valeur, col_infos = st.columns([0.7, 1.3])

        with col_valeur:
            valeur = st.number_input(
                f"Valeur pour {commune} — {nom_variable}",
                value=float(var["valeur_defaut"]),
                step=1.0 if var.get("decimales", 2) == 0 else 0.1,
                key=f"valeur_{dimension}_{nom_variable}",
            )

        with col_infos:
            st.markdown(
                f"""
                <div class="detail-box">
                    <strong>Source :</strong> {var['source']}<br>
                    <strong>Calcul de la variable :</strong> {var['calcul_variable']}
                </div>
                """,
                unsafe_allow_html=True,
            )

        valeurs_saisies[nom_variable] = valeur

        afficher_bornes_percentiles(var)

        scores = normaliser_score(valeur, var["min"], var["max"], var["sens"])
        resultats_variables[nom_variable] = {
            "dimension": dimension,
            "valeur": valeur,
            "score_brut": scores["score_brut"],
            "score_final": scores["score_final"],
            "var": var,
        }

        afficher_alerte_valeur_extreme(nom_variable, var, valeur, scores["score_final"])


# -----------------------------------------------------------------------------
# Calcul des scores par dimension et score final
# -----------------------------------------------------------------------------

if not resultats_variables:
    st.warning("Sélectionnez au moins une variable pour calculer l’indicateur.")
    st.stop()

scores_dimensions: Dict[str, float] = {}
for dimension in DIMENSIONS.keys():
    scores_dimension = [
        r["score_final"]
        for r in resultats_variables.values()
        if r["dimension"] == dimension
    ]
    if scores_dimension:
        scores_dimensions[dimension] = sum(scores_dimension) / len(scores_dimension)

poids_utilises = {
    dimension: poids_dimensions.get(dimension, 0)
    for dimension in scores_dimensions.keys()
}
somme_poids = sum(poids_utilises.values())

if somme_poids == 0:
    score_global = sum(scores_dimensions.values()) / len(scores_dimensions)
else:
    score_global = sum(
        scores_dimensions[dimension] * poids_utilises[dimension]
        for dimension in scores_dimensions.keys()
    ) / somme_poids


# -----------------------------------------------------------------------------
# Affichage du résultat global
# -----------------------------------------------------------------------------

st.markdown('<div class="dimension-header">Résultat synthétique</div>', unsafe_allow_html=True)

col_score, col_dim = st.columns([0.75, 1.25])

with col_score:
    st.markdown('<div class="score-card">', unsafe_allow_html=True)
    st.markdown("**Score global de l’indicateur**")
    st.markdown(f'<div class="score-big">{format_nombre(score_global, 2)} / 100</div>', unsafe_allow_html=True)
    st.progress(max(0, min(100, int(round(score_global)))))
    st.markdown('</div>', unsafe_allow_html=True)

with col_dim:
    df_dimensions = pd.DataFrame(
        [
            {
                "Dimension": dimension,
                "Score moyen / 100": round(score, 2),
                "Poids": poids_utilises.get(dimension, 0),
            }
            for dimension, score in scores_dimensions.items()
        ]
    )
    st.dataframe(df_dimensions, use_container_width=True, hide_index=True)

st.bar_chart(pd.DataFrame.from_dict(scores_dimensions, orient="index", columns=["Score / 100"]))


# -----------------------------------------------------------------------------
# Détail du calcul par variable
# -----------------------------------------------------------------------------

st.markdown('<div class="dimension-header">Détail du calcul par variable</div>', unsafe_allow_html=True)

for nom_variable, resultat in resultats_variables.items():
    var = resultat["var"]
    valeur = resultat["valeur"]
    score_brut = resultat["score_brut"]
    score_final = resultat["score_final"]
    unite = var.get("unite", "")
    decimales = var.get("decimales", 2)

    with st.expander(nom_variable, expanded=False):
        st.markdown(f"**Dimension :** {resultat['dimension']}")
        st.markdown(var["description"])

        afficher_bornes_percentiles(var)
        afficher_alerte_valeur_extreme(nom_variable, var, valeur, score_final)

        col1, col2, col3 = st.columns(3)
        col1.metric("Valeur saisie", format_valeur(valeur, unite, decimales))
        col2.metric("Score brut", f"{format_nombre(score_brut, 2)} / 100")
        col3.metric("Score final", f"{format_nombre(score_final, 2)} / 100")

        st.markdown("**Formule appliquée**")
        st.markdown(formule_normalisation(var, valeur, score_brut, score_final))

        st.markdown(
            f"""
            <div class="detail-box">
                <strong>Bornes réelles observées en 2021</strong><br>
                Minimum réel : <strong>{format_valeur(var['minimum_reel'], unite, decimales)}</strong>
                — {var['commune_min_reel']}<br>
                Maximum réel : <strong>{format_valeur(var['maximum_reel'], unite, decimales)}</strong>
                — {var['commune_max_reel']}<br><br>
                Ces bornes réelles ne sont pas utilisées comme bornes principales du calcul.
                Le calcul utilise les bornes par percentiles afin de limiter l'effet des valeurs extrêmes.
            </div>
            """,
            unsafe_allow_html=True,
        )


# -----------------------------------------------------------------------------
# Tableau récapitulatif et export
# -----------------------------------------------------------------------------

st.markdown('<div class="dimension-header">Tableau récapitulatif</div>', unsafe_allow_html=True)

lignes = []
for nom_variable, resultat in resultats_variables.items():
    var = resultat["var"]
    unite = var.get("unite", "")
    decimales = var.get("decimales", 2)
    lignes.append(
        {
            "Dimension": resultat["dimension"],
            "Variable": nom_variable,
            "Valeur saisie": format_valeur(resultat["valeur"], unite, decimales),
            "Borne P5": format_valeur(var["min"], unite, decimales),
            "Borne P95": format_valeur(var["max"], unite, decimales),
            "Sens": "favorable" if var["sens"] == "positif" else "défavorable",
            "Score final / 100": round(resultat["score_final"], 2),
        }
    )

df_recap = pd.DataFrame(lignes)
st.dataframe(df_recap, use_container_width=True, hide_index=True)

csv = df_recap.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="Télécharger le tableau récapitulatif en CSV",
    data=csv,
    file_name="resultats_indicateur_communal.csv",
    mime="text/csv",
)
