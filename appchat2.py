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
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ── Titre principal ── */
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

/* ── Badges ── */
.badge-todo {
    display: inline-block;
    background: #fef9c3;
    color: #854d0e;
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-left: 6px;
}

/* ── Bornes visuelles ── */
.bornes-wrap {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 5px;
    flex-wrap: wrap;
}
.borne-block {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    border-radius: 7px;
    padding: 4px 10px;
    font-size: 0.8rem;
}
.borne-min-block {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
}
.borne-max-block {
    background: #fff7ed;
    border: 1px solid #fed7aa;
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
.borne-commune {
    font-size: 0.75rem;
    color: #64748b;
    font-style: italic;
}
.borne-arrow {
    color: #94a3b8;
    font-size: 0.85rem;
}

/* ── Carte variable ── */
.var-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.var-card.inactive {
    opacity: 0.45;
}
.var-name {
    font-size: 0.97rem;
    font-weight: 600;
    color: #1e3a5f;
    margin-bottom: 4px;
}
.var-meta {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 2px;
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

/* ── Dimension header ── */
.dim-header {
    background: linear-gradient(90deg, #1e3a5f 0%, #2563eb 100%);
    color: white;
    border-radius: 10px;
    padding: 10px 16px;
    margin-bottom: 8px;
    font-size: 1rem;
    font-weight: 700;
}
.dim-desc {
    font-size: 0.88rem;
    color: #64748b;
    margin-bottom: 10px;
}

/* ── Score global ── */
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

/* ── Barre de score dimension ── */
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

/* ── Steps visuels ── */
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

/* ── Note pédagogique ── */
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
# DONNÉES : DIMENSIONS, VARIABLES ET BORNES
# ─────────────────────────────────────────────

DIMENSIONS = {
    "Revenus et inégalités": {
        "emoji": "💶",
        "description": "Cette dimension mesure le niveau de vie, la pauvreté et les inégalités monétaires.",
        "variables": {
            "Revenu médian": {
                "min": 14790, "max": 48010, "valeur": 25210, "unite": "€",
                "sens": "positif",
                "source": "Filosofi 2021, communes d'Île-de-France",
                "commune_min": "Grigny (91286)", "commune_max": "Neuilly-sur-Seine (92051)"
            },
            "Taux de pauvreté au seuil de 60 % du revenu médian": {
                "min": 5, "max": 44, "valeur": 18, "unite": "%",
                "sens": "negatif",
                "source": "Filosofi 2021, communes d'Île-de-France",
                "commune_min": "28 communes, dont Bois-le-Roi (77037)", "commune_max": "Grigny (91286)"
            },
            "Rapport interdécile du revenu disponible D9/D1": {
                "min": 2.2, "max": 8.1, "valeur": 4.4, "unite": "",
                "sens": "negatif",
                "source": "Filosofi 2021, communes d'Île-de-France",
                "commune_min": "Moncourt-Fromonville (77302)", "commune_max": "Neuilly-sur-Seine (92051)"
            },
        },
    },
    "Éducation": {
        "emoji": "🎓",
        "description": "Cette dimension mesure le niveau de formation, la scolarisation et l'accès aux diplômes.",
        "variables": {
            "Part des diplômés du supérieur (15 ans+ non scolarisés)": {
                "min": 9.4, "max": 74.2, "valeur": 35.0, "unite": "%",
                "sens": "positif",
                "source": "INSEE, RP 2021, base communale Diplômes-Formation, Île-de-France",
                "commune_min": "Mouy-sur-Seine (77325)", "commune_max": "Saint-Aubin (91538)"
            },
            "Part des actifs peu ou pas diplômés parmi les actifs": {
                "min": 1.0, "max": 47.0, "valeur": 20.0, "unite": "%",
                "sens": "negatif",
                "source": "INSEE, RP 2021, base communale Emploi-Population active, Île-de-France",
                "commune_min": "Milon-la-Chapelle (78406)", "commune_max": "Hautefeuille (77224)"
            },
            "Taux de scolarisation": {
                "min": 50, "max": 99, "valeur": 80, "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter", "commune_max": "À documenter"
            },
        },
    },
    "Emploi": {
        "emoji": "💼",
        "description": "Cette dimension mesure l'accès à l'emploi, le chômage et la stabilité professionnelle.",
        "variables": {
            "Taux de chômage au sens du recensement des 15-64 ans": {
                "min": 0.0, "max": 23.0, "valeur": 12.0, "unite": "%",
                "sens": "negatif",
                "source": "INSEE, RP 2021, base communale Emploi-Population active, Île-de-France",
                "commune_min": "2 communes, dont Montenils (77304)", "commune_max": "La Courneuve (93027)"
            },
            "Part des contrats précaires": {
                "min": 5, "max": 40, "valeur": 20, "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter", "commune_max": "À documenter"
            },
            "Taux d'activité": {
                "min": 45, "max": 85, "valeur": 70, "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter", "commune_max": "À documenter"
            },
        },
    },
    "Santé": {
        "emoji": "🏥",
        "description": "Cette dimension mesure l'état de santé et l'accès potentiel aux soins.",
        "variables": {
            "Espérance de vie": {
                "min": 70, "max": 90, "valeur": 82, "unite": "ans",
                "sens": "positif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter", "commune_max": "À documenter"
            },
            "Médecins pour 1 000 habitants": {
                "min": 0, "max": 10, "valeur": 3, "unite": "",
                "sens": "positif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter", "commune_max": "À documenter"
            },
            "Mortalité prématurée": {
                "min": 100, "max": 500, "valeur": 250, "unite": "pour 100 000",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter", "commune_max": "À documenter"
            },
        },
    },
    "Logement": {
        "emoji": "🏠",
        "description": "Cette dimension mesure les conditions de logement et l'accès au logement social.",
        "variables": {
            "Part des logements sociaux": {
                "min": 0, "max": 60, "valeur": 20, "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter", "commune_max": "À documenter"
            },
            "Mal-logement": {
                "min": 0, "max": 30, "valeur": 10, "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter", "commune_max": "À documenter"
            },
            "Surpopulation des logements": {
                "min": 0, "max": 25, "valeur": 8, "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter", "commune_max": "À documenter"
            },
        },
    },
    "Cohésion sociale": {
        "emoji": "🤝",
        "description": "Cette dimension mesure les liens sociaux, la participation et certaines fragilités sociales.",
        "variables": {
            "Participation électorale": {
                "min": 30, "max": 90, "valeur": 60, "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter", "commune_max": "À documenter"
            },
            "Familles monoparentales": {
                "min": 5, "max": 40, "valeur": 18, "unite": "%",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter", "commune_max": "À documenter"
            },
            "Criminalité pour 1 000 habitants": {
                "min": 0, "max": 100, "valeur": 35, "unite": "",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter", "commune_max": "À documenter"
            },
        },
    },
    "Environnement": {
        "emoji": "🌿",
        "description": "Cette dimension mesure la qualité du cadre de vie environnemental.",
        "variables": {
            "Espaces verts": {
                "min": 0, "max": 80, "valeur": 25, "unite": "%",
                "sens": "positif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter", "commune_max": "À documenter"
            },
            "Pollution de l'air": {
                "min": 5, "max": 40, "valeur": 20, "unite": "µg/m³",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter", "commune_max": "À documenter"
            },
            "Densité de population": {
                "min": 50, "max": 25000, "valeur": 5000, "unite": "hab/km²",
                "sens": "negatif",
                "source": "Borne indicative à discuter",
                "commune_min": "À documenter", "commune_max": "À documenter"
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
                "Valeur saisie": valeur,
                "Unité": infos.get("unite", ""),
                "Min": infos["min"],
                "Commune borne min": infos.get("commune_min", ""),
                "Max": infos["max"],
                "Commune borne max": infos.get("commune_max", ""),
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
    lignes = []
    for nom_dimension, contenu in DIMENSIONS.items():
        for nom_variable, infos in contenu["variables"].items():
            source_courte = infos.get("source", "")
            est_documente = "À documenter" not in infos.get("commune_min", "À documenter")
            lignes.append({
                "Dimension": nom_dimension,
                "Variable": nom_variable,
                "Min": infos["min"],
                "Commune borne min": infos.get("commune_min", ""),
                "Max": infos["max"],
                "Commune borne max": infos.get("commune_max", ""),
                "Unité": infos.get("unite", ""),
                "Sens": "✅ positif" if infos.get("sens") == "positif" else "🔻 négatif",
                "Documenté": "✅" if est_documente else "⏳",
                "Source": source_courte
            })
    return pd.DataFrame(lignes)



# ─────────────────────────────────────────────
# EN-TÊTE
# ─────────────────────────────────────────────

st.markdown('<div class="main-title">📊 Indicateur Socio-Économique communal</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Outil pédagogique participatif — choisissez des dimensions, des variables et des pondérations pour construire votre propre indicateur.</div>',
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# NOTE MÉTHODOLOGIQUE (compacte)
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

    st.markdown('<div class="info-box">🧩 <b>Dimension ou variable ?</b> — Une <b>dimension</b> est un domaine (ex. Santé), une <b>variable</b> est une mesure précise dans ce domaine (ex. Espérance de vie). Le choix n\'est pas neutre : il reflète ce que l\'on considère comme une situation favorable.</div>', unsafe_allow_html=True)

with st.expander("📋 Toutes les variables disponibles", expanded=False):
    df_all = tableau_variables()
    st.dataframe(df_all, use_container_width=True, height=300)

# ─────────────────────────────────────────────
# SIDEBAR : poids dimensions (calculé après saisie)
# ─────────────────────────────────────────────

with st.sidebar:
    st.header("⚖️ Poids des dimensions")
    st.caption("Ajustez l'importance de chaque dimension dans le score final (0 = ignorée, 5 = très importante).")
    # Rempli dynamiquement plus bas


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
# SIDEBAR : sliders poids dimensions (maintenant qu'on sait lesquelles sont actives)
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

            est_documente = "À documenter" not in infos.get("commune_min", "À documenter")
            unite_label = f" ({infos['unite']})" if infos.get("unite") else ""

            # Ligne d'en-tête variable
            col_check, col_info = st.columns([0.05, 0.95])

            with col_check:
                actif = st.checkbox(
                    label="",
                    value=True,
                    key=f"actif_{nom_dimension}_{nom_variable}",
                    label_visibility="collapsed"
                )

            with col_info:
                commune_min = infos.get("commune_min", "")
                commune_max = infos.get("commune_max", "")
                commune_min_str = f'<span class="borne-commune">{commune_min}</span>' if commune_min and commune_min != "À documenter" else ""
                commune_max_str = f'<span class="borne-commune">{commune_max}</span>' if commune_max and commune_max != "À documenter" else ""
                st.markdown(
                    f'<div class="var-name">{nom_variable}</div>'
                    f'<div class="bornes-wrap">'
                    f'  <span class="borne-block borne-min-block">'
                    f'    <span class="borne-label">Min</span>'
                    f'    <span class="borne-val">{infos["min"]}{unite_label}</span>'
                    f'    {commune_min_str}'
                    f'  </span>'
                    f'  <span class="borne-arrow">→</span>'
                    f'  <span class="borne-block borne-max-block">'
                    f'    <span class="borne-label">Max</span>'
                    f'    <span class="borne-val">{infos["max"]}{unite_label}</span>'
                    f'    {commune_max_str}'
                    f'  </span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            if actif:
                variables_choisies[nom_dimension].append(nom_variable)

                col_val, col_poids = st.columns([2, 1])

                with col_val:
                    step = 0.1 if isinstance(infos["min"], float) or isinstance(infos["max"], float) else 1.0
                    fmt = "%.1f" if step == 0.1 else "%.0f"

                    valeurs[nom_variable] = st.number_input(
                        label=f"Valeur observée{unite_label}",
                        min_value=float(infos["min"]),
                        max_value=float(infos["max"]),
                        value=float(infos["valeur"]),
                        step=float(step),
                        format=fmt,
                        key=f"valeur_{nom_dimension}_{nom_variable}"
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
    st.caption("Ce tableau montre les variables retenues, leurs bornes, communes de référence, poids et score calculé.")

    df_affichage = df_resultats[[
        "Dimension", "Variable", "Valeur saisie", "Unité",
        "Min", "Commune borne min",
        "Max", "Commune borne max",
        "Poids variable", "Score normalisé 0-100", "Source"
    ]]

    st.dataframe(
        df_affichage.style.highlight_between(
            subset=["Valeur saisie"],
            color="#fef9c3"
        ),
        use_container_width=True
    )

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
