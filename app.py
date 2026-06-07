# app.py
# Prototype pédagogique d'indicateur socio-économique communal en Île-de-France
# Version avec explication claire des bornes par percentiles sous chaque variable

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st


# -----------------------------------------------------------------------------
# Configuration générale
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Indicateur socio-économique communal",
    page_icon="📊",
    layout="wide",
)


# -----------------------------------------------------------------------------
# Style CSS
# -----------------------------------------------------------------------------

st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.35rem;
            font-weight: 800;
            color: #0f3d75;
            margin-bottom: 0.2rem;
        }
        .subtitle {
            font-size: 1.05rem;
            color: #475569;
            margin-bottom: 1.4rem;
        }
        .section-title {
            background: linear-gradient(90deg, #dbeafe, #eff6ff);
            color: #1e3a8a;
            font-size: 1.35rem;
            font-weight: 750;
            padding: 0.65rem 0.9rem;
            border-left: 6px solid #2563eb;
            border-radius: 0.6rem;
            margin-top: 1.2rem;
            margin-bottom: 0.8rem;
        }
        .dimension-title {
            color: #0f3d75;
            font-size: 1.12rem;
            font-weight: 750;
            margin-top: 0.8rem;
        }
        .variable-title {
            color: #1d4ed8;
            font-size: 1.08rem;
            font-weight: 750;
            margin-top: 1.0rem;
            margin-bottom: 0.25rem;
        }
        .info-box {
            background-color: #f8fafc;
            border: 1px solid #dbeafe;
            border-left: 5px solid #2563eb;
            border-radius: 0.7rem;
            padding: 0.9rem 1rem;
            margin: 0.5rem 0 1rem 0;
            line-height: 1.48;
            color: #1f2937;
        }
        .percentile-box {
            background-color: #f3f7ff;
            border-left: 5px solid #2563eb;
            padding: 0.85rem 1rem;
            border-radius: 0.7rem;
            margin-top: 0.35rem;
            margin-bottom: 0.9rem;
            font-size: 0.96rem;
            line-height: 1.48;
            color: #1f2937;
        }
        .warning-box {
            background-color: #fff1f2;
            border-left: 5px solid #dc2626;
            padding: 0.8rem 1rem;
            border-radius: 0.7rem;
            margin-top: 0.5rem;
            margin-bottom: 0.7rem;
            color: #7f1d1d;
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
        }
        .big-score {
            color: #1d4ed8;
            font-size: 2.4rem;
            font-weight: 850;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Données de normalisation
# -----------------------------------------------------------------------------

@dataclass
class VariableConfig:
    key: str
    label: str
    short_label: str
    dimension: str
    description: str
    unit: str
    p5: float
    p95: float
    real_min: float
    real_max: float
    real_min_commune: str
    real_max_commune: str
    source: str
    formula_source: str
    sens: str  # "positif" ou "negatif"
    default_value: float
    decimals: int = 2


VARIABLES: Dict[str, VariableConfig] = {
    "revenu_median": VariableConfig(
        key="revenu_median",
        label="Revenu médian par unité de consommation",
        short_label="Revenu médian",
        dimension="Revenus et inégalités",
        description=(
            "Le revenu médian partage la population en deux : 50 % des personnes vivent "
            "dans un ménage dont le niveau de vie est inférieur à cette valeur, et 50 % "
            "dans un ménage dont le niveau de vie est supérieur."
        ),
        unit="€",
        p5=20460,
        p95=34765,
        real_min=14790,
        real_max=48010,
        real_min_commune="Grigny (91286)",
        real_max_commune="Neuilly-sur-Seine (92051)",
        source="Filosofi 2021 / Observatoire des territoires, variable med_disp",
        formula_source="x = médiane du revenu disponible par unité de consommation",
        sens="positif",
        default_value=29730,
        decimals=0,
    ),
    "rapport_d9_d1": VariableConfig(
        key="rapport_d9_d1",
        label="Rapport interdécile D9/D1 du revenu disponible",
        short_label="Rapport D9/D1",
        dimension="Revenus et inégalités",
        description=(
            "Le rapport D9/D1 mesure l'écart entre les 10 % les plus aisés et les 10 % "
            "les moins aisés. Plus il est élevé, plus les inégalités de revenu sont fortes."
        ),
        unit="",
        p5=2.5,
        p95=4.5,
        real_min=2.2,
        real_max=8.1,
        real_min_commune="Moncourt-Fromonville (77302)",
        real_max_commune="Neuilly-sur-Seine (92051)",
        source="Filosofi 2021 / Observatoire des territoires, variable rap_interdec",
        formula_source="x = D9 / D1",
        sens="negatif",
        default_value=4.2,
        decimals=2,
    ),
    "taux_pauvrete": VariableConfig(
        key="taux_pauvrete",
        label="Taux de pauvreté au seuil de 60 % du revenu médian",
        short_label="Taux de pauvreté",
        dimension="Revenus et inégalités",
        description=(
            "Le taux de pauvreté mesure la part des personnes vivant avec un niveau de vie "
            "inférieur à 60 % du niveau de vie médian. Plus il est élevé, plus la situation "
            "sociale est défavorable."
        ),
        unit="%",
        p5=5,
        p95=29,
        real_min=5,
        real_max=44,
        real_min_commune="28 communes, dont Bois-le-Roi (77037)",
        real_max_commune="Grigny (91286)",
        source="Filosofi 2021 / Insee-DGFIP-Cnaf-Cnav-CCMSA / Observatoire des territoires, variable tx_pauv_60",
        formula_source="x = tx_pauv_60",
        sens="negatif",
        default_value=16,
        decimals=1,
    ),
    "taux_chomage": VariableConfig(
        key="taux_chomage",
        label="Taux de chômage des 15-64 ans",
        short_label="Taux de chômage",
        dimension="Emploi",
        description=(
            "Le taux de chômage rapporte le nombre de chômeurs à la population active "
            "des 15-64 ans. Plus il est élevé, plus la situation de l'emploi est défavorable."
        ),
        unit="%",
        p5=4.8812,
        p95=15.2901,
        real_min=0,
        real_max=22.9971,
        real_min_commune="2 communes, dont Montenils (77304)",
        real_max_commune="La Courneuve (93027)",
        source="Insee, Recensement de la population 2021, base Emploi - Population active",
        formula_source="x = P21_CHOM1564 / P21_ACT1564 × 100",
        sens="negatif",
        default_value=10.7472,
        decimals=2,
    ),
    "actifs_peu_pas_diplomes": VariableConfig(
        key="actifs_peu_pas_diplomes",
        label="Part des actifs peu ou pas diplômés parmi les actifs",
        short_label="Actifs peu ou pas diplômés",
        dimension="Éducation",
        description=(
            "Cette variable mesure la part des actifs ayant un niveau de diplôme faible "
            "ou aucun diplôme. Elle est utilisée comme indicateur de fragilité scolaire "
            "et sociale parmi la population active."
        ),
        unit="%",
        p5=6.1995,
        p95=22.7569,
        real_min=0.9679,
        real_max=46.9962,
        real_min_commune="Milon-la-Chapelle (78406)",
        real_max_commune="Hautefeuille (77224)",
        source="Insee, Recensement de la population 2021, base Emploi - Population active",
        formula_source="x = (P21_ACT_DIPLMIN + P21_ACT_BEPC) / P21_ACT1564 × 100",
        sens="negatif",
        default_value=8.8045,
        decimals=2,
    ),
}

DIMENSIONS: List[str] = [
    "Revenus et inégalités",
    "Emploi",
    "Éducation",
]


# -----------------------------------------------------------------------------
# Fonctions utilitaires
# -----------------------------------------------------------------------------

def format_nombre(valeur: float, decimals: int = 2) -> str:
    """Formate un nombre en écriture française."""
    if valeur is None or (isinstance(valeur, float) and math.isnan(valeur)):
        return "—"
    if decimals == 0:
        txt = f"{valeur:,.0f}"
    else:
        txt = f"{valeur:,.{decimals}f}"
        txt = txt.rstrip("0").rstrip(".")
    return txt.replace(",", " ").replace(".", ",")


def format_valeur(valeur: float, variable: VariableConfig, decimals: Optional[int] = None) -> str:
    """Formate une valeur avec l'unité de la variable."""
    d = variable.decimals if decimals is None else decimals
    txt = format_nombre(valeur, d)
    if variable.unit:
        return f"{txt} {variable.unit}"
    return txt


def score_normalise(valeur: float, variable: VariableConfig) -> Dict[str, float]:
    """Calcule le score brut et le score final plafonné entre 0 et 100."""
    amplitude = variable.p95 - variable.p5
    if amplitude == 0:
        return {"score_brut": 0.0, "score_final": 0.0}

    if variable.sens == "positif":
        score_brut = ((valeur - variable.p5) / amplitude) * 100
    else:
        score_brut = ((variable.p95 - valeur) / amplitude) * 100

    score_final = max(0, min(100, score_brut))
    return {"score_brut": score_brut, "score_final": score_final}


def afficher_titre_section(titre: str) -> None:
    st.markdown(f'<div class="section-title">{titre}</div>', unsafe_allow_html=True)


def afficher_explication_percentiles(variable: VariableConfig) -> None:
    """Affiche l'explication pédagogique des bornes par percentiles sous une variable."""
    p5_txt = format_valeur(variable.p5, variable)
    p95_txt = format_valeur(variable.p95, variable)

    if variable.sens == "positif":
        phrase_sens = (
            "Comme cette variable est <strong>favorable</strong>, plus la valeur est élevée, "
            "plus le score augmente. Dans le calcul, une commune située à la borne basse "
            "obtient <strong>0 / 100</strong>, une commune située à la borne haute obtient "
            "<strong>100 / 100</strong>."
        )
    else:
        phrase_sens = (
            "Comme cette variable mesure une <strong>difficulté sociale</strong>, le score est "
            "inversé : une commune située à la borne basse obtient <strong>100 / 100</strong>, "
            "une commune située à la borne haute obtient <strong>0 / 100</strong>."
        )

    st.markdown(
        f"""
        <div class="percentile-box">
            <strong>Bornes par percentiles utilisées pour le calcul</strong><br><br>
            La borne basse correspond au <strong>5e percentile</strong> : environ
            <strong>5 % des communes d’Île-de-France</strong> ont une valeur inférieure à
            <strong>{p5_txt}</strong>.<br><br>
            La borne haute correspond au <strong>95e percentile</strong> : environ
            <strong>5 % des communes d’Île-de-France</strong> ont une valeur supérieure à
            <strong>{p95_txt}</strong>.<br><br>
            Ces bornes sont dites robustes car elles utilisent les percentiles 5 et 95
            au lieu des valeurs extrêmes réelles. Le score est ensuite calculé sur
            <strong>100</strong> entre ces deux bornes. Les valeurs situées en dehors de ces
            bornes sont plafonnées à <strong>0</strong> ou à <strong>100</strong>.<br><br>
            {phrase_sens}
        </div>
        """,
        unsafe_allow_html=True,
    )


def afficher_alerte_extreme(valeur: float, variable: VariableConfig, score_final: float) -> None:
    """Affiche une alerte rouge si la valeur saisie est hors des bornes par percentiles."""
    if valeur < variable.p5:
        st.markdown(
            f"""
            <div class="warning-box">
                <strong>Valeur réelle extrême basse.</strong><br>
                La valeur saisie, <strong>{format_valeur(valeur, variable)}</strong>, est inférieure
                à la borne par percentile basse de <strong>{format_valeur(variable.p5, variable)}</strong>.
                Le score est donc plafonné à <strong>{format_nombre(score_final, 2)} / 100</strong>,
                mais la valeur réelle reste affichée pour l’interprétation.
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif valeur > variable.p95:
        st.markdown(
            f"""
            <div class="warning-box">
                <strong>Valeur réelle extrême haute.</strong><br>
                La valeur saisie, <strong>{format_valeur(valeur, variable)}</strong>, est supérieure
                à la borne par percentile haute de <strong>{format_valeur(variable.p95, variable)}</strong>.
                Le score est donc plafonné à <strong>{format_nombre(score_final, 2)} / 100</strong>,
                mais la valeur réelle reste affichée pour l’interprétation.
            </div>
            """,
            unsafe_allow_html=True,
        )


def formuler_calcul(variable: VariableConfig, valeur: float, score_brut: float, score_final: float) -> str:
    amplitude = variable.p95 - variable.p5
    x_txt = format_valeur(valeur, variable)
    p5_txt = format_valeur(variable.p5, variable)
    p95_txt = format_valeur(variable.p95, variable)
    amp_txt = format_valeur(amplitude, variable)

    if variable.sens == "positif":
        formule = (
            f"Score brut = (({x_txt} - {p5_txt}) / ({p95_txt} - {p5_txt})) × 100  "
            f"\n\n= (({x_txt} - {p5_txt}) / {amp_txt}) × 100"
        )
    else:
        formule = (
            f"Score brut = (({p95_txt} - {x_txt}) / ({p95_txt} - {p5_txt})) × 100  "
            f"\n\n= (({p95_txt} - {x_txt}) / {amp_txt}) × 100"
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
    '<div class="subtitle">Prototype pédagogique participatif pour comparer les communes d’Île-de-France à partir de variables normalisées sur 100.</div>',
    unsafe_allow_html=True,
)

with st.expander("Comment fonctionne cet outil ?", expanded=False):
    st.markdown(
        """
        Cet outil permet de construire un indicateur synthétique communal à partir de plusieurs variables
        socio-économiques. Les variables n'ont pas les mêmes unités : euros, pourcentages, rapports.
        Elles doivent donc être transformées sur une échelle commune.

        La méthode utilisée ici est une **normalisation par bornes par percentiles**.

        Au lieu d'utiliser directement le minimum et le maximum réels, on utilise :

        - le **5e percentile**, c'est-à-dire le seuil sous lequel se trouvent environ 5 % des communes ;
        - le **95e percentile**, c'est-à-dire le seuil au-dessus duquel se trouvent environ 5 % des communes.

        Ces bornes par percentiles sont aussi des **bornes robustes**, car elles évitent qu'une commune très
        extrême déforme toute l'échelle de comparaison. Le score de chaque variable est ensuite calculé sur
        **100**. Les valeurs situées en dehors des bornes sont plafonnées à **0** ou à **100**.
        """
    )


# -----------------------------------------------------------------------------
# Barre latérale : sélection
# -----------------------------------------------------------------------------

st.sidebar.title("Paramètres")

commune_nom = st.sidebar.text_input("Nom de la commune étudiée", value="Paris")

st.sidebar.markdown("---")
st.sidebar.subheader("1. Choisir les dimensions et variables")

selected_dimensions: List[str] = []
selected_variables: List[str] = []

for dimension in DIMENSIONS:
    dim_key = f"select_dim_{dimension}"
    include_dim = st.sidebar.checkbox(dimension, value=True, key=dim_key)
    if include_dim:
        selected_dimensions.append(dimension)
        variables_dimension = [v for v in VARIABLES.values() if v.dimension == dimension]
        for var in variables_dimension:
            var_key = f"select_var_{var.key}"
            include_var = st.sidebar.checkbox(f"↳ {var.short_label}", value=True, key=var_key)
            if include_var:
                selected_variables.append(var.key)

st.sidebar.markdown("---")
st.sidebar.subheader("2. Pondérer les dimensions")

weights: Dict[str, float] = {}
for dimension in selected_dimensions:
    weights[dimension] = st.sidebar.slider(
        f"Poids : {dimension}",
        min_value=0,
        max_value=100,
        value=100,
        step=5,
        key=f"weight_{dimension}",
    )

st.sidebar.caption(
    "Les poids sont automatiquement normalisés : ce sont les proportions relatives entre les dimensions retenues."
)


# -----------------------------------------------------------------------------
# Corps : valeurs à saisir
# -----------------------------------------------------------------------------

if not selected_variables:
    st.warning("Sélectionnez au moins une variable dans la barre latérale.")
    st.stop()

values: Dict[str, float] = {}
results: Dict[str, Dict[str, float]] = {}

afficher_titre_section("1. Saisir ou modifier les valeurs de la commune")

st.markdown(
    f"Les valeurs ci-dessous servent à calculer l’indicateur pour : **{commune_nom}**. "
    "Les valeurs affichées par défaut sont seulement des valeurs d’exemple."
)

for dimension in selected_dimensions:
    vars_in_dim = [VARIABLES[k] for k in selected_variables if VARIABLES[k].dimension == dimension]
    if not vars_in_dim:
        continue

    st.markdown(f'<div class="dimension-title">{dimension}</div>', unsafe_allow_html=True)

    for var in vars_in_dim:
        st.markdown(f'<div class="variable-title">{var.label}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="small-muted">{var.description}</div>', unsafe_allow_html=True)

        col_input, col_source = st.columns([1, 1.2])
        with col_input:
            step = 1.0 if var.decimals == 0 else 0.1
            value = st.number_input(
                f"Valeur de la commune — {var.short_label}",
                value=float(var.default_value),
                step=step,
                format="%.4f" if var.decimals > 2 else "%.2f",
                key=f"input_{var.key}",
            )
            values[var.key] = value

        with col_source:
            st.markdown(
                f"""
                <div class="info-box">
                    <strong>Source</strong> : {var.source}<br>
                    <strong>Calcul de la variable</strong> : {var.formula_source}<br>
                    <strong>Valeurs réelles observées en 2021</strong> : de
                    <strong>{format_valeur(var.real_min, var)}</strong> ({var.real_min_commune})
                    à <strong>{format_valeur(var.real_max, var)}</strong> ({var.real_max_commune}).
                </div>
                """,
                unsafe_allow_html=True,
            )

        afficher_explication_percentiles(var)

        calc = score_normalise(value, var)
        results[var.key] = calc
        afficher_alerte_extreme(value, var, calc["score_final"])


# -----------------------------------------------------------------------------
# Calcul des scores par dimension et de l'indicateur final
# -----------------------------------------------------------------------------

dimension_scores: Dict[str, float] = {}
for dimension in selected_dimensions:
    scores = [
        results[k]["score_final"]
        for k in selected_variables
        if VARIABLES[k].dimension == dimension and k in results
    ]
    if scores:
        dimension_scores[dimension] = sum(scores) / len(scores)

valid_weights = {dim: weights.get(dim, 0) for dim in dimension_scores.keys()}
total_weight = sum(valid_weights.values())

if total_weight == 0:
    indicateur_final = sum(dimension_scores.values()) / len(dimension_scores) if dimension_scores else 0
else:
    indicateur_final = sum(dimension_scores[d] * valid_weights[d] for d in dimension_scores) / total_weight


# -----------------------------------------------------------------------------
# Résultats synthétiques
# -----------------------------------------------------------------------------

afficher_titre_section("2. Résultat synthétique")

col_score, col_table = st.columns([0.8, 1.4])

with col_score:
    st.markdown('<div class="score-card">', unsafe_allow_html=True)
    st.markdown("Score final de l’indicateur")
    st.markdown(f'<div class="big-score">{format_nombre(indicateur_final, 2)} / 100</div>', unsafe_allow_html=True)
    st.progress(int(round(indicateur_final)))
    st.markdown('</div>', unsafe_allow_html=True)

with col_table:
    df_dimensions = pd.DataFrame(
        [
            {
                "Dimension": dim,
                "Score moyen / 100": round(score, 2),
                "Poids saisi": valid_weights.get(dim, 0),
            }
            for dim, score in dimension_scores.items()
        ]
    )
    st.dataframe(df_dimensions, use_container_width=True, hide_index=True)

if dimension_scores:
    st.bar_chart(pd.DataFrame.from_dict(dimension_scores, orient="index", columns=["Score / 100"]))


# -----------------------------------------------------------------------------
# Détail du calcul par variable
# -----------------------------------------------------------------------------

afficher_titre_section("3. Détail du calcul par variable")

for dimension in selected_dimensions:
    vars_in_dim = [VARIABLES[k] for k in selected_variables if VARIABLES[k].dimension == dimension]
    if not vars_in_dim:
        continue

    with st.expander(f"{dimension}", expanded=True):
        for var in vars_in_dim:
            valeur = values[var.key]
            calc = results[var.key]
            score_brut = calc["score_brut"]
            score_final = calc["score_final"]

            st.markdown(f"### {var.label}")
            afficher_explication_percentiles(var)
            afficher_alerte_extreme(valeur, var, score_final)

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Valeur saisie", format_valeur(valeur, var))
            col_b.metric("Score brut", f"{format_nombre(score_brut, 2)} / 100")
            col_c.metric("Score final", f"{format_nombre(score_final, 2)} / 100")

            st.markdown("**Formule appliquée**")
            st.markdown(formuler_calcul(var, valeur, score_brut, score_final))

            st.markdown(
                f"""
                <div class="info-box">
                    <strong>Rappel des bornes réelles observées</strong><br>
                    Minimum réel : <strong>{format_valeur(var.real_min, var)}</strong> — {var.real_min_commune}<br>
                    Maximum réel : <strong>{format_valeur(var.real_max, var)}</strong> — {var.real_max_commune}<br><br>
                    Ces valeurs réelles ne sont pas supprimées : elles servent à l'interprétation.
                    Mais la normalisation utilise les bornes par percentiles afin d'éviter que les valeurs extrêmes
                    déforment toute l'échelle de comparaison.
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("---")


# -----------------------------------------------------------------------------
# Tableau récapitulatif
# -----------------------------------------------------------------------------

afficher_titre_section("4. Tableau récapitulatif")

rows = []
for key in selected_variables:
    var = VARIABLES[key]
    calc = results[key]
    rows.append(
        {
            "Dimension": var.dimension,
            "Variable": var.label,
            "Valeur saisie": format_valeur(values[key], var),
            "Borne P5": format_valeur(var.p5, var),
            "Borne P95": format_valeur(var.p95, var),
            "Sens": "favorable" if var.sens == "positif" else "défavorable",
            "Score / 100": round(calc["score_final"], 2),
        }
    )

st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

csv = pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="Télécharger le tableau récapitulatif en CSV",
    data=csv,
    file_name="resultats_indicateur_communal.csv",
    mime="text/csv",
)
