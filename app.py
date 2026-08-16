import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import html

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
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

.main-title {
    font-size: 2rem;
    font-weight: 700;
    color: #12203f;
    margin-bottom: 0.15rem;
}
.subtitle {
    font-size: 1rem;
    color: #6b7280;
    margin-bottom: 1.5rem;
}

/* ── Bornes visuelles ── */
.bornes-wrap {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-top: 6px;
    flex-wrap: wrap;
}
.borne-group {
    display: flex;
    flex-direction: column;
    gap: 3px;
}
.borne-block {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    border-radius: 7px;
    padding: 4px 10px;
    font-size: 0.8rem;
}
.borne-p5-block {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
}
.borne-p95-block {
    background: #fff7ed;
    border: 1px solid #fed7aa;
}
.borne-reel-block {
    background: #f8fafc;
    border: 1px dashed #cbd5e1;
    cursor: help;
}
.borne-label {
    font-weight: 700;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748b;
}
.borne-val {
    font-weight: 700;
    font-size: 0.88rem;
    color: #1e3a5f;
}
.borne-reel-label {
    font-weight: 600;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #94a3b8;
}
.borne-reel-val {
    font-size: 0.8rem;
    color: #94a3b8;
}
.borne-expl {
    font-size: 0.73rem;
    color: #64748b;
    font-style: italic;
    margin-top: 1px;
    max-width: 300px;
    line-height: 1.35;
}
.borne-arrow {
    color: #94a3b8;
    font-size: 0.85rem;
    margin-top: 6px;
}
.borne-sep {
    color: #cbd5e1;
    font-size: 0.85rem;
    margin: 0 2px;
    margin-top: 6px;
}

/* ── Alerte valeur extrême ── */
.alerte-extreme {
    background: #fef2f2;
    border: 1.5px solid #fca5a5;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 0.82rem;
    color: #b91c1c;
    font-weight: 600;
    margin-top: 5px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.var-name {
    font-size: 0.97rem;
    font-weight: 600;
    color: #1e3a5f;
    margin-bottom: 4px;
}
.dim-desc {
    font-size: 0.88rem;
    color: #64748b;
    margin-bottom: 10px;
}
.source-tag {
    display: inline-block;
    font-size: 0.72rem;
    color: #475569;
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 5px;
    padding: 1px 7px;
    margin-top: 4px;
}

.score-card {
    background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    color: white;
}
.score-label {
    font-size: 0.9rem;
    font-weight: 600;
    opacity: 0.8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
}
.score-value {
    font-size: 3.2rem;
    font-weight: 700;
    line-height: 1;
}
.score-sub {
    font-size: 0.85rem;
    opacity: 0.65;
    margin-top: 4px;
}

.dim-score-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}
.dim-score-name {
    width: 160px;
    font-size: 0.82rem;
    font-weight: 600;
    color: #1e3a5f;
    flex-shrink: 0;
}
.dim-score-bar-wrap {
    flex: 1;
    background: #e2e8f0;
    border-radius: 999px;
    height: 10px;
    overflow: hidden;
}
.dim-score-bar {
    height: 10px;
    border-radius: 999px;
    background: linear-gradient(90deg, #2563eb, #38bdf8);
}
.dim-score-val {
    width: 48px;
    text-align: right;
    font-size: 0.82rem;
    font-weight: 700;
    color: #1e3a5f;
}

.step-pill {
    display: inline-block;
    background: #2563eb;
    color: white;
    border-radius: 999px;
    width: 26px;
    height: 26px;
    text-align: center;
    line-height: 26px;
    font-size: 0.82rem;
    font-weight: 700;
    margin-right: 8px;
}

.info-box {
    background: #eff6ff;
    border-left: 4px solid #2563eb;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    font-size: 0.88rem;
    color: #1e3a5f;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DONNÉES
# "min"/"max"       → bornes P5/P95 (normalisation)
# "min_reel"/"max_reel" → bornes réelles (limites de saisie)
# "commune_min"/"commune_max" → communes aux valeurs extrêmes réelles
# ─────────────────────────────────────────────

DIMENSIONS = {
    "Revenus et inégalités": {
        "emoji": "💶",
        "description": "Cette dimension mesure le niveau de vie, la pauvreté et les inégalités monétaires.",
        "variables": {
            "Revenu médian": {
                "min": 20460, "max": 34765,
                "min_reel": 14790, "max_reel": 48010,
                "commune_min": "Grigny (91286)", "commune_max": "Neuilly-sur-Seine (92051)",
                "valeur": 25210, "unite": "€",
                "sens": "positif",
                "source": "Filosofi 2021, communes d'Île-de-France",
            },
            "Taux de pauvreté au seuil de 60 % du revenu médian": {
                "min": 5, "max": 29,
                "min_reel": 5, "max_reel": 44,
                "commune_min": "28 communes, dont Bois-le-Roi (77037)", "commune_max": "Grigny (91286)",
                "valeur": 18, "unite": "%",
                "sens": "negatif",
                "source": "Filosofi 2021, communes d'Île-de-France",
            },
            "Rapport interdécile du revenu disponible D9/D1": {
                "min": 2.5, "max": 4.5,
                "min_reel": 2.2, "max_reel": 8.1,
                "commune_min": "Moncourt-Fromonville (77302)", "commune_max": "Neuilly-sur-Seine (92051)",
                "valeur": 4.4, "unite": "",
                "sens": "negatif",
                "source": "Filosofi 2021, communes d'Île-de-France",
            },
        },
    },
    "Éducation": {
        "emoji": "🎓",
        "description": "Cette dimension mesure le niveau de formation, la scolarisation et l'accès aux diplômes.",
        "variables": {
            "Part des diplômés du supérieur (15 ans+ non scolarisés)": {
                "min": 20.1, "max": 61.0,
                "min_reel": 9.4, "max_reel": 74.2,
                "commune_min": "Mouy-sur-Seine (77325)", "commune_max": "Saint-Aubin (91538)",
                "valeur": 35.0, "unite": "%",
                "sens": "positif",
                "source": "INSEE, RP 2021, base communale Diplômes-Formation, Île-de-France",
            },
            "Part des actifs peu ou pas diplômés parmi les actifs": {
                "min": 6.2, "max": 22.8,
                "min_reel": 1.0, "max_reel": 47.0,
                "commune_min": "Milon-la-Chapelle (78406)", "commune_max": "Hautefeuille (77224)",
                "valeur": 20.0, "unite": "%",
                "sens": "negatif",
                "source": "INSEE, RP 2021, base communale Emploi-Population active, Île-de-France",
            },
        },
    },
    "Emploi": {
        "emoji": "💼",
        "description": "Cette dimension mesure l'accès à l'emploi, le chômage et la stabilité professionnelle.",
        "variables": {
            "Taux de chômage au sens du recensement des 15-64 ans": {
                "min": 4.9, "max": 15.3,
                "min_reel": 0.0, "max_reel": 23.0,
                "commune_min": "2 communes, dont Montenils (77304)", "commune_max": "La Courneuve (93027)",
                "valeur": 12.0, "unite": "%",
                "sens": "negatif",
                "source": "INSEE, RP 2021, base communale Emploi-Population active, Île-de-France",
            },
            "Part des salariés en emploi non stable parmi les salariés": {
                "min": 6.64, "max": 16.69,
                "min_reel": 0.0, "max_reel": 28.37,
                "commune_min": "3 communes, dont Boisdon (77036)", "commune_max": "Nanteau-sur-Lunain (77329)",
                "valeur": 12.0, "unite": "%",
                "sens": "negatif",
                "source": "INSEE, RP 2021, base communale Caractéristiques de l'emploi, Île-de-France",
            },
            "Taux d'activité": {
                "min": 71.10, "max": 83.52,
                "min_reel": 42.48, "max_reel": 88.84,
                "commune_min": "Fleury-Mérogis (91235)", "commune_max": "Dhuisy (77157)",
                "valeur": 76.0, "unite": "%",
                "sens": "positif",
                "source": "INSEE, RP 2021, base communale Emploi-Population active, Île-de-France",
            },
        },
    },
    "Santé": {
        "emoji": "🏥",
        "description": "Cette dimension mesure l'accès potentiel aux soins de médecine générale.",
        "variables": {
            "Accessibilité potentielle localisée aux médecins généralistes": {
                "min": 1.3422, "max": 3.8351,
                "min_reel": 0.627, "max_reel": 5.600,
                "commune_min": "Moisson (78410)", "commune_max": "Bois-d'Arcy (78073)",
                "valeur": 2.5, "unite": "consult./an/hab. std.",
                "sens": "positif",
                "source": "DREES, APL médecins généralistes 2021, Méthode concertée V2 2015-2022 ; Paris agrégé en commune 75056 par population standardisée 2019",
            },
        },
    },
    "Logement": {
        "emoji": "🏠",
        "description": "Cette dimension mesure les conditions de logement et l'accès au logement social.",
        "variables": {
            "Part des logements sociaux": {
                "min": 0, "max": 60,
                "min_reel": 0, "max_reel": 60,
                "commune_min": "À documenter", "commune_max": "À documenter",
                "valeur": 20, "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter",
            },
            "Mal-logement": {
                "min": 0, "max": 30,
                "min_reel": 0, "max_reel": 30,
                "commune_min": "À documenter", "commune_max": "À documenter",
                "valeur": 10, "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
            },
            "Part des résidences principales suroccupées": {
                "min": 0.00, "max": 15.85,
                "min_reel": 0.00, "max_reel": 33.73,
                "commune_min": "291 communes, dont Amponville (77003)", "commune_max": "Aubervilliers (93001)",
                "valeur": 3.40, "unite": "%",
                "sens": "negatif",
                "source": "INSEE, RP 2021, base communale Logement, Île-de-France ; résidences principales hors studios occupés par une personne",
            },
        },
    },
    "Vulnérabilité sociale": {
        "emoji": "🤝",
        "description": "Cette dimension mesure certaines situations d’isolement et de vulnérabilité relationnelle.",
        "variables": {
            "Part des personnes de 65 ans ou plus vivant seules": {
                "min": 15.78, "max": 38.50,
                "min_reel": 0.00, "max_reel": 100.00,
                "commune_min": "3 communes, dont Chatignonville (91145)", "commune_max": "2 communes, dont Montenils (77304)",
                "valeur": 26.24, "unite": "%",
                "sens": "negatif",
                "source": "INSEE, RP 2021, base communale Couples-Familles-Ménages, Île-de-France ; formule : (P21_POP6579_PSEUL + P21_POP80P_PSEUL) / (P21_POP6579 + P21_POP80P) × 100",
            },
            "Part des familles monoparentales parmi les familles": {
                "min": 3.19, "max": 25.64,
                "min_reel": 0.00, "max_reel": 100.00,
                "commune_min": "53 communes, dont Amponville (77003)", "commune_max": "Charmont (95141)",
                "valeur": 14.28, "unite": "%",
                "sens": "negatif",
                "source": "INSEE, RP 2021, base communale Couples-Familles-Ménages, Île-de-France ; formule : C21_FAMMONO / C21_FAM × 100",
            },
        },
    },
    "Environnement": {
        "emoji": "🌿",
        "description": "Cette dimension mesure la qualité du cadre de vie environnemental.",
        "variables": {
            "Espaces verts": {
                "min": 0, "max": 80,
                "min_reel": 0, "max_reel": 80,
                "commune_min": "À documenter", "commune_max": "À documenter",
                "valeur": 25, "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter",
            },
            "Pollution de l'air": {
                "min": 5, "max": 40,
                "min_reel": 5, "max_reel": 40,
                "commune_min": "À documenter", "commune_max": "À documenter",
                "valeur": 20, "unite": "µg/m³",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
            },
            "Densité de population": {
                "min": 50, "max": 25000,
                "min_reel": 50, "max_reel": 25000,
                "commune_min": "À documenter", "commune_max": "À documenter",
                "valeur": 5000, "unite": "hab/km²",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
            },
        },
    },
}

# ─────────────────────────────────────────────
# UTILITAIRES
# ─────────────────────────────────────────────

def fmt_val(v):
    """Formate un nombre : supprime les .0 inutiles, garde les décimales significatives."""
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    if isinstance(v, float):
        # Supprime les zéros de fin après la virgule
        s = f"{v:.4f}".rstrip("0").rstrip(".")
        return s
    return str(v)


def attr_html(v):
    """Protège un texte avant de l'utiliser dans un attribut HTML title."""
    return html.escape(str(v), quote=True)


# ─────────────────────────────────────────────
# FONCTIONS
# ─────────────────────────────────────────────

def normaliser(valeur, vmin, vmax, sens="positif"):
    """Normalise sur [0,1] via les bornes P5/P95 ; plafonne à 0 ou 1 si hors bornes."""
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

            hors_bornes = valeur < infos["min"] or valeur > infos["max"]

            resultats_variables.append({
                "Dimension": nom_dimension,
                "Variable": nom_variable,
                "Valeur saisie": valeur,
                "Unité": infos.get("unite", ""),
                "P5": infos["min"],
                "P95": infos["max"],
                "Sens": infos.get("sens", "positif"),
                "Hors bornes P5-P95": "⚠️ Oui" if hors_bornes else "Non",
                "Poids variable": poids,
                "Score normalisé 0-100": round(score * 100, 1),
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
    fig.add_trace(go.Scatterpolar(
        r=scores_fermes,
        theta=dimensions_fermees,
        fill="toself",
        name="Score des dimensions",
        fillcolor="rgba(37, 99, 235, 0.15)",
        line=dict(color="#2563eb", width=3)
    ))

    fig.update_layout(
        height=400,
        margin=dict(l=60, r=60, t=60, b=60),
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=11)),
            angularaxis=dict(tickfont=dict(size=12))
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def tableau_variables():
    """Tableau synthétique : P5/P95 + min/max réels avec communes."""
    lignes = []
    for nom_dimension, contenu in DIMENSIONS.items():
        for nom_variable, infos in contenu["variables"].items():
            has_reel = infos.get("min_reel") != infos.get("min") or infos.get("max_reel") != infos.get("max")
            commune_min = infos.get("commune_min", "")
            commune_max = infos.get("commune_max", "")
            lignes.append({
                "Dimension": nom_dimension,
                "Variable": nom_variable,
                "P5 (normalisation)": infos["min"],
                "P95 (normalisation)": infos["max"],
                "Min réel": infos.get("min_reel", infos["min"]) if has_reel else "—",
                "Commune min réel": commune_min if (has_reel and commune_min and commune_min != "À documenter") else "—",
                "Max réel": infos.get("max_reel", infos["max"]) if has_reel else "—",
                "Commune max réel": commune_max if (has_reel and commune_max and commune_max != "À documenter") else "—",
                "Unité": infos.get("unite", ""),
                "Sens": "✅ positif" if infos.get("sens") == "positif" else "🔻 négatif",
                "Source": infos.get("source", "")
            })
    return pd.DataFrame(lignes)


def explication_borne(nom_variable, p5, p95, unite, min_reel, max_reel, commune_min, commune_max):
    """Génère une explication pédagogique dynamique des bornes P5/P95."""
    u = f" {unite}" if unite else ""
    p5_fmt = fmt_val(p5)
    p95_fmt = fmt_val(p95)

    texte_p5 = f"Environ 5 % des communes d'Île-de-France ont une valeur inférieure ou égale à {p5_fmt}{u} pour cette variable."
    texte_p95 = f"Environ 5 % des communes d'Île-de-France ont une valeur supérieure ou égale à {p95_fmt}{u} pour cette variable."

    has_reel = (min_reel != p5 or max_reel != p95)
    if has_reel:
        min_reel_fmt = fmt_val(min_reel)
        max_reel_fmt = fmt_val(max_reel)
        cm = f" ({commune_min})" if commune_min and commune_min != "À documenter" else ""
        cM = f" ({commune_max})" if commune_max and commune_max != "À documenter" else ""
        texte_reel = (
            f"Valeurs extrêmes observées : {min_reel_fmt}{u}{cm} → {max_reel_fmt}{u}{cM}. "
            f"La saisie accepte ces valeurs réelles, mais le score sera plafonné à 0 ou 100."
        )
    else:
        texte_reel = ""

    return texte_p5, texte_p95, texte_reel


# ─────────────────────────────────────────────
# EN-TÊTE
# ─────────────────────────────────────────────

st.markdown('<div class="main-title">📊 Indicateur Socio-Économique communal</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Outil pédagogique participatif — choisissez des dimensions, des variables et des pondérations pour construire votre propre indicateur.</div>',
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# NOTE MÉTHODOLOGIQUE
# ─────────────────────────────────────────────

with st.expander("ℹ️ Comment fonctionne cet outil ?", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**<span class='step-pill'>1</span> Choisir les dimensions**", unsafe_allow_html=True)
        st.caption("Un grand domaine de la réalité sociale : revenus, santé, emploi…")
    with c2:
        st.markdown("**<span class='step-pill'>2</span> Choisir les variables**", unsafe_allow_html=True)
        st.caption("Une donnée statistique précise pour mesurer chaque dimension.")
    with c3:
        st.markdown("**<span class='step-pill'>3</span> Pondérer**", unsafe_allow_html=True)
        st.caption("Décider de l'importance relative de chaque variable et dimension.")

    st.markdown(
        '<div class="info-box">🧩 <b>Bornes P5 / P95</b> — La normalisation s\'appuie sur les percentiles 5 et 95 '
        'calculés sur les communes d\'Île-de-France. Les valeurs hors bornes sont plafonnées à 0 ou 100. '
        'La saisie accepte les vraies valeurs extrêmes observées.</div>',
        unsafe_allow_html=True
    )

with st.expander("📋 Toutes les variables disponibles", expanded=False):
    df_all = tableau_variables()
    st.dataframe(df_all, use_container_width=True, height=340)

# ─────────────────────────────────────────────
# SIDEBAR : poids dimensions
# ─────────────────────────────────────────────

with st.sidebar:
    st.header("⚖️ Poids des dimensions")
    st.caption("Ajustez l'importance de chaque dimension dans le score final (0 = ignorée, 5 = très importante).")

# ─────────────────────────────────────────────
# ÉTAPE 1 : CHOIX DES DIMENSIONS
# ─────────────────────────────────────────────

st.markdown("---")
st.markdown("### <span class='step-pill'>1</span> Dimensions à inclure", unsafe_allow_html=True)
st.caption("Cochez les grandes thématiques que vous souhaitez intégrer à l'indicateur.")

dimensions_disponibles = list(DIMENSIONS.keys())
dimensions_choisies = []

cols = st.columns(4)
for i, nom_dimension in enumerate(dimensions_disponibles):
    emoji = DIMENSIONS[nom_dimension]["emoji"]
    with cols[i % 4]:
        actif = st.checkbox(
            label=f"{emoji} {nom_dimension}",
            value=True,
            key=f"choix_dimension_{nom_dimension}"
        )
        if actif:
            dimensions_choisies.append(nom_dimension)

if len(dimensions_choisies) == 0:
    st.warning("⚠️ Vous devez choisir au moins une dimension pour calculer l'indicateur.")
    st.stop()

# ─────────────────────────────────────────────
# SIDEBAR : sliders poids dimensions
# ─────────────────────────────────────────────

poids_dimensions = {}
with st.sidebar:
    for nom_dimension in dimensions_choisies:
        emoji = DIMENSIONS[nom_dimension]["emoji"]
        poids_dimensions[nom_dimension] = st.slider(
            label=f"{emoji} {nom_dimension}",
            min_value=0.0,
            max_value=5.0,
            value=1.0,
            step=0.5,
            key=f"poids_dimension_{nom_dimension}"
        )

# ─────────────────────────────────────────────
# ÉTAPE 2 : CHOIX DES VARIABLES ET VALEURS
# ─────────────────────────────────────────────

st.markdown("---")
st.markdown("### <span class='step-pill'>2</span> Variables et valeurs observées", unsafe_allow_html=True)
st.caption("Pour chaque dimension, sélectionnez les variables à inclure et saisissez la valeur observée pour votre commune.")

variables_choisies = {}
valeurs = {}
poids_variables = {}

tabs = st.tabs([f"{DIMENSIONS[d]['emoji']} {d}" for d in dimensions_choisies])

for tab, nom_dimension in zip(tabs, dimensions_choisies):
    with tab:
        contenu_dimension = DIMENSIONS[nom_dimension]
        st.markdown(f'<div class="dim-desc">{contenu_dimension["description"]}</div>', unsafe_allow_html=True)

        variables_choisies[nom_dimension] = []

        for nom_variable, infos in contenu_dimension["variables"].items():

            unite = infos.get("unite", "")
            unite_label = f" ({unite})" if unite else ""
            p5 = infos["min"]
            p95 = infos["max"]
            min_reel = infos.get("min_reel", p5)
            max_reel = infos.get("max_reel", p95)
            commune_min = infos.get("commune_min", "")
            commune_max = infos.get("commune_max", "")

            p5_fmt = fmt_val(p5)
            p95_fmt = fmt_val(p95)
            min_reel_fmt = fmt_val(min_reel)
            max_reel_fmt = fmt_val(max_reel)

            has_reel = (min_reel != p5 or max_reel != p95)

            texte_p5, texte_p95, texte_reel = explication_borne(
                nom_variable, p5, p95, unite, min_reel, max_reel, commune_min, commune_max
            )

            col_check, col_info = st.columns([0.05, 0.95])

            with col_check:
                actif = st.checkbox(
                    label="",
                    value=True,
                    key=f"actif_{nom_dimension}_{nom_variable}",
                    label_visibility="collapsed"
                )

            with col_info:
                # Bornes réelles (si différentes des P5/P95)
                # L'explication des valeurs extrêmes est conservée en infobulle au survol
                # de "Min réel" et "Max réel", afin d'alléger l'affichage principal.
                reel_html = ""
                if has_reel:
                    tooltip_reel = attr_html(texte_reel)
                    reel_html = (
                        f'<span class="borne-sep">|</span>'
                        f'<div class="borne-group">'
                        f'  <span class="borne-block borne-reel-block" title="{tooltip_reel}">'
                        f'    <span class="borne-reel-label">Min réel ⓘ</span>'
                        f'    <span class="borne-reel-val">{min_reel_fmt}{unite_label}</span>'
                        f'  </span>'
                        f'  <span class="borne-block borne-reel-block" title="{tooltip_reel}">'
                        f'    <span class="borne-reel-label">Max réel ⓘ</span>'
                        f'    <span class="borne-reel-val">{max_reel_fmt}{unite_label}</span>'
                        f'  </span>'
                        f'</div>'
                    )

                st.markdown(
                    f'<div class="var-name">{nom_variable}</div>'
                    f'<div class="bornes-wrap">'
                    f'  <div class="borne-group">'
                    f'    <span class="borne-block borne-p5-block">'
                    f'      <span class="borne-label">Borne minimale P5</span>'
                    f'      <span class="borne-val">{p5_fmt}{unite_label}</span>'
                    f'    </span>'
                    f'    <div class="borne-expl">{texte_p5}</div>'
                    f'  </div>'
                    f'  <div class="borne-arrow">→</div>'
                    f'  <div class="borne-group">'
                    f'    <span class="borne-block borne-p95-block">'
                    f'      <span class="borne-label">Borne maximale P95</span>'
                    f'      <span class="borne-val">{p95_fmt}{unite_label}</span>'
                    f'    </span>'
                    f'    <div class="borne-expl">{texte_p95}</div>'
                    f'  </div>'
                    f'  {reel_html}'
                    f'</div>',
                    unsafe_allow_html=True
                )

            if actif:
                variables_choisies[nom_dimension].append(nom_variable)

                col_val, col_poids = st.columns([2, 1])

                with col_val:
                    step = 0.1 if isinstance(min_reel, float) or isinstance(max_reel, float) else 1.0
                    fmt_input = "%.1f" if step == 0.1 else "%.0f"

                    valeur_saisie = st.number_input(
                        label=f"Valeur observée{unite_label}",
                        min_value=float(min_reel),
                        max_value=float(max_reel),
                        value=float(infos["valeur"]),
                        step=float(step),
                        format=fmt_input,
                        key=f"valeur_{nom_dimension}_{nom_variable}"
                    )
                    valeurs[nom_variable] = valeur_saisie

                    # Alerte rouge si valeur hors bornes P5/P95
                    if valeur_saisie < p5 or valeur_saisie > p95:
                        st.markdown(
                            f'<div class="alerte-extreme">⚠️ Valeur extrême — en dehors des bornes par percentiles '
                            f'(borne min P5 = {p5_fmt}{unite_label}, borne max P95 = {p95_fmt}{unite_label})</div>',
                            unsafe_allow_html=True
                        )

                with col_poids:
                    poids_variables[nom_variable] = st.slider(
                        label="Poids",
                        min_value=0.0,
                        max_value=5.0,
                        value=1.0,
                        step=0.5,
                        key=f"poids_variable_{nom_dimension}_{nom_variable}"
                    )
            else:
                st.caption("_Variable exclue du calcul._")

            st.divider()

# ─────────────────────────────────────────────
# VÉRIFICATION
# ─────────────────────────────────────────────

nombre_variables_retenues = sum(len(v) for v in variables_choisies.values())

if nombre_variables_retenues == 0:
    st.warning("⚠️ Vous devez choisir au moins une variable pour calculer l'indicateur.")
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
# ÉTAPE 3 : RÉSULTATS
# ─────────────────────────────────────────────

st.markdown("---")
st.markdown("### <span class='step-pill'>3</span> Résultats", unsafe_allow_html=True)

col_score, col_bars, col_radar = st.columns([1, 1.4, 2])

with col_score:
    couleur_score = "#16a34a" if indicateur_global >= 0.6 else ("#d97706" if indicateur_global >= 0.35 else "#dc2626")
    st.markdown(f"""
    <div class="score-card" style="background: linear-gradient(135deg, #12203f 0%, {couleur_score} 100%);">
        <div class="score-label">Score global</div>
        <div class="score-value">{indicateur_global * 100:.1f}</div>
        <div class="score-sub">sur 100 points</div>
    </div>
    """, unsafe_allow_html=True)
    st.caption(f"Basé sur **{nombre_variables_retenues} variable(s)** répartie(s) en **{len(scores_dimensions)} dimension(s)**.")

with col_bars:
    st.markdown("**Scores par dimension**")
    for dim, score in scores_dimensions.items():
        pct = score * 100
        emoji = DIMENSIONS[dim]["emoji"]
        st.markdown(f"""
        <div class="dim-score-row">
            <div class="dim-score-name">{emoji} {dim}</div>
            <div class="dim-score-bar-wrap">
                <div class="dim-score-bar" style="width:{pct:.1f}%"></div>
            </div>
            <div class="dim-score-val">{pct:.0f}</div>
        </div>
        """, unsafe_allow_html=True)

with col_radar:
    fig_radar = creer_radar(scores_dimensions)
    st.plotly_chart(fig_radar, use_container_width=True)

# ─────────────────────────────────────────────
# DÉTAIL DES VARIABLES
# ─────────────────────────────────────────────

with st.expander("🔍 Détail du calcul par variable", expanded=False):
    st.caption("Ce tableau montre les variables retenues, leurs bornes P5/P95, poids et score calculé. **Cliquez sur une ligne** pour afficher le détail pédagogique du calcul.")

    # Formatage propre des colonnes numériques
    df_affichage = df_resultats[[
        "Dimension", "Variable", "Valeur saisie", "Unité",
        "P5", "P95",
        "Hors bornes P5-P95",
        "Poids variable", "Score normalisé 0-100", "Source"
    ]].copy()

    for col in ["Valeur saisie", "P5", "P95", "Poids variable", "Score normalisé 0-100"]:
        df_affichage[col] = df_affichage[col].apply(fmt_val)

    selection = st.dataframe(
        df_affichage.style.highlight_between(
            subset=["Valeur saisie"],
            color="#fef9c3"
        ),
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
        key="detail_selection"
    )

    # ── Panneau pédagogique déclenché par la sélection ──
    lignes_sel = selection.selection.get("rows", [])
    if lignes_sel:
        idx = lignes_sel[0]
        row = df_resultats.iloc[idx]

        valeur    = row["Valeur saisie"]
        p5        = row["P5"]
        p95       = row["P95"]
        sens      = row["Sens"]
        unite     = row["Unité"]
        score_100 = row["Score normalisé 0-100"]
        variable  = row["Variable"]
        hors      = row["Hors bornes P5-P95"] == "⚠️ Oui"

        u = f" {unite}" if unite else ""
        v_fmt   = fmt_val(valeur)
        p5_fmt  = fmt_val(p5)
        p95_fmt = fmt_val(p95)
        s_fmt   = fmt_val(score_100)

        # Calculs intermédiaires
        amplitude = p95 - p5
        if sens == "positif":
            numerateur = valeur - p5
            formule_gauche = "x - P5"
        else:
            numerateur = p95 - valeur
            formule_gauche = "P95 - x"

        ratio_brut = numerateur / amplitude if amplitude != 0 else 0
        ratio_clamp = max(0.0, min(1.0, ratio_brut))
        score_01 = round(ratio_clamp, 4)

        # Texte sens
        if sens == "positif":
            sens_expl = "**variable favorable** : plus la valeur est élevée, plus le score est élevé."
            application = f"({v_fmt}{u} − {p5_fmt}{u}) ÷ ({p95_fmt}{u} − {p5_fmt}{u})"
        else:
            sens_expl = "**variable défavorable** : plus la valeur est élevée, plus le score est bas (formule inversée)."
            application = f"({p95_fmt}{u} − {v_fmt}{u}) ÷ ({p95_fmt}{u} − {p5_fmt}{u})"

        # Alerte hors bornes
        alerte_hors = ""
        if hors:
            cote = "100" if ratio_brut > 1 else "0"
            alerte_hors = f"\n\n> ⚠️ **Valeur hors bornes P5/P95** — la valeur {v_fmt}{u} est en dehors de l'intervalle [{p5_fmt}{u} ; {p95_fmt}{u}]. Le ratio brut ({round(ratio_brut, 4)}) est plafonné à {'1' if ratio_brut > 1 else '0'}, soit un score final de **{cote}/100**."

        st.markdown("---")
        st.markdown(f"#### 🧮 Calcul détaillé — *{variable}*")

        col_calc, col_schema = st.columns([1.3, 0.7])

        with col_calc:
            st.markdown(f"""
**1. Type de variable :** {sens_expl}

**2. Formule de normalisation :**
""")
            if sens == "positif":
                st.latex(r"\text{score} = \frac{x - P5}{P95 - P5} \times 100")
            else:
                st.latex(r"\text{score} = \frac{P95 - x}{P95 - P5} \times 100")
            st.markdown(f"""
**3. Application numérique :**

| Élément | Valeur |
|---|---|
| Valeur observée (x) | **{v_fmt}{u}** |
| Borne minimale P5 | {p5_fmt}{u} |
| Borne maximale P95 | {p95_fmt}{u} |
| Amplitude (P95 − P5) | {fmt_val(amplitude)}{u} |
| = {application} | = **{round(ratio_brut, 4)}** |
| Après plafonnement [0 ; 1] | **{score_01}** |
| **Score final (× 100)** | **{s_fmt} / 100** |
{alerte_hors}
""")

        with col_schema:
            pct_display = min(100, max(0, score_100))
            couleur_jauge = "#16a34a" if pct_display >= 60 else ("#d97706" if pct_display >= 35 else "#dc2626")
            sens_icon = "🔼 Variable favorable" if sens == "positif" else "🔽 Variable défavorable"
            st.markdown(f"""
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:20px;text-align:center;">
  <div style="font-size:0.78rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;">Score normalisé</div>
  <div style="font-size:2.8rem;font-weight:700;color:{couleur_jauge};line-height:1;">{s_fmt}</div>
  <div style="font-size:0.8rem;color:#94a3b8;margin-bottom:14px;">sur 100</div>
  <div style="background:#e2e8f0;border-radius:999px;height:12px;overflow:hidden;">
    <div style="width:{pct_display:.1f}%;height:12px;border-radius:999px;background:{couleur_jauge};"></div>
  </div>
  <div style="font-size:0.75rem;color:#64748b;margin-top:10px;">{sens_icon}</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────

with st.expander("📥 Exporter les résultats", expanded=False):
    csv_resultats = df_resultats.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 Télécharger en CSV",
        data=csv_resultats,
        file_name="resultats_indicateur_socio_economique.csv",
        mime="text/csv"
    )
