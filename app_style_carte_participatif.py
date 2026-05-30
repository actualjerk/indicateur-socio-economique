import math
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# ISS communal participatif — version élève
# Objectif : permettre à l'élève de choisir :
# - la base de données utilisée ;
# - les variables retenues ;
# - les dimensions ;
# - le sens favorable/défavorable des variables ;
# - les pondérations des variables et des dimensions.
# ============================================================

st.set_page_config(
    page_title="ISS communal participatif — Île-de-France",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# Style graphique : carte interactive / observatoire territorial
# ------------------------------------------------------------
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
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] small {
        color: white !important;
    }

    .main-title {
        padding: 1.25rem 1.45rem;
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
        font-weight: 750;
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
        background: rgba(255,255,255,.88);
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

# ------------------------------------------------------------
# Données de démonstration
# ------------------------------------------------------------

def donnees_demo() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "commune": "Paris",
                "code_commune": "75056",
                "departement": "75",
                "lat": 48.8566,
                "lon": 2.3522,
                "revenu_median": 30300,
                "taux_pauvrete": 16.2,
                "rapport_d9_d1": 6.4,
                "part_diplomes_superieur": 52.0,
                "part_actifs_peu_diplomes": 18.0,
                "taux_chomage": 10.4,
                "part_logements_suroccupes": 12.6,
            },
            {
                "commune": "Versailles",
                "code_commune": "78646",
                "departement": "78",
                "lat": 48.8049,
                "lon": 2.1204,
                "revenu_median": 34600,
                "taux_pauvrete": 8.9,
                "rapport_d9_d1": 4.1,
                "part_diplomes_superieur": 58.0,
                "part_actifs_peu_diplomes": 13.0,
                "taux_chomage": 7.5,
                "part_logements_suroccupes": 6.7,
            },
            {
                "commune": "Saint-Denis",
                "code_commune": "93066",
                "departement": "93",
                "lat": 48.9362,
                "lon": 2.3574,
                "revenu_median": 17600,
                "taux_pauvrete": 33.0,
                "rapport_d9_d1": 4.8,
                "part_diplomes_superieur": 24.0,
                "part_actifs_peu_diplomes": 38.0,
                "taux_chomage": 18.7,
                "part_logements_suroccupes": 24.2,
            },
            {
                "commune": "Cergy",
                "code_commune": "95127",
                "departement": "95",
                "lat": 49.0361,
                "lon": 2.0631,
                "revenu_median": 22600,
                "taux_pauvrete": 20.4,
                "rapport_d9_d1": 3.8,
                "part_diplomes_superieur": 38.0,
                "part_actifs_peu_diplomes": 27.0,
                "taux_chomage": 13.2,
                "part_logements_suroccupes": 16.4,
            },
            {
                "commune": "Créteil",
                "code_commune": "94028",
                "departement": "94",
                "lat": 48.7904,
                "lon": 2.4556,
                "revenu_median": 23900,
                "taux_pauvrete": 18.7,
                "rapport_d9_d1": 3.9,
                "part_diplomes_superieur": 41.0,
                "part_actifs_peu_diplomes": 25.0,
                "taux_chomage": 12.8,
                "part_logements_suroccupes": 14.6,
            },
            {
                "commune": "Évry-Courcouronnes",
                "code_commune": "91228",
                "departement": "91",
                "lat": 48.6238,
                "lon": 2.4292,
                "revenu_median": 21300,
                "taux_pauvrete": 22.6,
                "rapport_d9_d1": 3.7,
                "part_diplomes_superieur": 33.0,
                "part_actifs_peu_diplomes": 31.0,
                "taux_chomage": 14.5,
                "part_logements_suroccupes": 17.3,
            },
            {
                "commune": "Meaux",
                "code_commune": "77284",
                "departement": "77",
                "lat": 48.9607,
                "lon": 2.8787,
                "revenu_median": 21700,
                "taux_pauvrete": 21.3,
                "rapport_d9_d1": 3.5,
                "part_diplomes_superieur": 28.0,
                "part_actifs_peu_diplomes": 34.0,
                "taux_chomage": 13.9,
                "part_logements_suroccupes": 15.1,
            },
            {
                "commune": "Nanterre",
                "code_commune": "92050",
                "departement": "92",
                "lat": 48.8924,
                "lon": 2.2153,
                "revenu_median": 26100,
                "taux_pauvrete": 17.8,
                "rapport_d9_d1": 4.7,
                "part_diplomes_superieur": 45.0,
                "part_actifs_peu_diplomes": 22.0,
                "taux_chomage": 11.4,
                "part_logements_suroccupes": 14.8,
            },
        ]
    )

# ------------------------------------------------------------
# Chargement de fichiers
# ------------------------------------------------------------

SOURCES_LOCALES = {
    "Diplômes et formation 2021": "/mnt/data/base-cc-diplomes-formation-2021.xlsx",
    "Filosofi D9/D1": "/mnt/data/filosofiD9D1.csv",
    "Filosofi revenu médian": "/mnt/data/filosofi-Revenu médian.xlsx",
    "Filosofi taux de pauvreté": "/mnt/data/filosofi-Taux de pauvreté.xlsx",
    "Emploi / population active 2021": "/mnt/data/base-cc-emploi-pop-active-2021_xlsx.zip",
}


def chemins_locaux_disponibles() -> dict:
    return {nom: chemin for nom, chemin in SOURCES_LOCALES.items() if Path(chemin).exists()}


@st.cache_data(show_spinner=False)
def lire_csv_depuis_bytes(contenu: bytes) -> pd.DataFrame:
    essais = [
        {"sep": ";", "encoding": "utf-8"},
        {"sep": ",", "encoding": "utf-8"},
        {"sep": ";", "encoding": "latin1"},
        {"sep": ",", "encoding": "latin1"},
    ]
    derniere_erreur = None
    for params in essais:
        try:
            return pd.read_csv(BytesIO(contenu), **params)
        except Exception as exc:  # noqa: BLE001
            derniere_erreur = exc
    raise derniere_erreur


@st.cache_data(show_spinner=False)
def lire_fichier_local(chemin: str, feuille: str | int | None = None) -> pd.DataFrame:
    path = Path(chemin)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return lire_csv_depuis_bytes(path.read_bytes())

    if suffix in [".xlsx", ".xls"]:
        return pd.read_excel(path, sheet_name=feuille if feuille is not None else 0)

    if suffix == ".zip":
        with zipfile.ZipFile(path) as zf:
            noms = zf.namelist()
            candidats = [n for n in noms if n.lower().endswith((".csv", ".xlsx", ".xls"))]
            if not candidats:
                raise ValueError("Le fichier ZIP ne contient pas de CSV ou de fichier Excel lisible.")
            premier = candidats[0]
            contenu = zf.read(premier)
            if premier.lower().endswith(".csv"):
                return lire_csv_depuis_bytes(contenu)
            return pd.read_excel(BytesIO(contenu), sheet_name=feuille if feuille is not None else 0)

    raise ValueError(f"Format non pris en charge : {suffix}")


def lister_feuilles_excel_local(chemin: str) -> list[str]:
    path = Path(chemin)
    if path.suffix.lower() in [".xlsx", ".xls"]:
        try:
            return pd.ExcelFile(path).sheet_names
        except Exception:  # noqa: BLE001
            return []
    if path.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(path) as zf:
                candidats = [n for n in zf.namelist() if n.lower().endswith((".xlsx", ".xls"))]
                if not candidats:
                    return []
                contenu = zf.read(candidats[0])
                return pd.ExcelFile(BytesIO(contenu)).sheet_names
        except Exception:  # noqa: BLE001
            return []
    return []


def lire_fichier_importe(fichier, feuille: str | int | None = None) -> pd.DataFrame:
    nom = fichier.name.lower()
    contenu = fichier.getvalue()
    if nom.endswith(".csv"):
        return lire_csv_depuis_bytes(contenu)
    if nom.endswith((".xlsx", ".xls")):
        return pd.read_excel(BytesIO(contenu), sheet_name=feuille if feuille is not None else 0)
    raise ValueError("Format non pris en charge. Importer un fichier CSV ou Excel.")

# ------------------------------------------------------------
# Outils de préparation statistique
# ------------------------------------------------------------

def serie_numerique(serie: pd.Series) -> pd.Series:
    """Convertit une série en numérique, y compris les formats français avec virgule."""
    if pd.api.types.is_numeric_dtype(serie):
        return pd.to_numeric(serie, errors="coerce")

    propre = (
        serie.astype(str)
        .str.replace("\u202f", "", regex=False)
        .str.replace("\xa0", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace("%", "", regex=False)
    )
    propre = propre.replace({"nan": None, "None": None, "": None, "-": None})
    return pd.to_numeric(propre, errors="coerce")


def colonnes_numeriques_probables(df: pd.DataFrame, seuil: float = 0.55) -> list[str]:
    colonnes = []
    for col in df.columns:
        s = serie_numerique(df[col])
        nb_non_vides = df[col].notna().sum()
        if nb_non_vides == 0:
            continue
        ratio = s.notna().sum() / nb_non_vides
        if ratio >= seuil:
            colonnes.append(col)
    return colonnes


def normaliser_minmax(serie: pd.Series, sens: str) -> pd.Series:
    """Normalisation sur 0-100.

    - Favorable : plus la valeur est élevée, plus le score est élevé.
    - Défavorable : plus la valeur est élevée, plus le score est faible.
    """
    valeurs = serie_numerique(serie)
    minimum = valeurs.min(skipna=True)
    maximum = valeurs.max(skipna=True)

    if pd.isna(minimum) or pd.isna(maximum):
        return pd.Series([pd.NA] * len(serie), index=serie.index, dtype="Float64")

    if math.isclose(float(minimum), float(maximum)):
        return pd.Series([50.0] * len(serie), index=serie.index)

    if sens == "Défavorable : une valeur élevée dégrade le score":
        score = (maximum - valeurs) / (maximum - minimum) * 100
    else:
        score = (valeurs - minimum) / (maximum - minimum) * 100

    return score.clip(0, 100)


def moyenne_ponderee_ligne(df_scores: pd.DataFrame, poids: dict[str, float]) -> pd.Series:
    """Moyenne pondérée qui ignore les valeurs manquantes ligne par ligne."""
    numerateur = pd.Series(0.0, index=df_scores.index)
    denominateur = pd.Series(0.0, index=df_scores.index)

    for col, poids_col in poids.items():
        if col not in df_scores.columns:
            continue
        valeurs = df_scores[col]
        masque = valeurs.notna()
        numerateur.loc[masque] += valeurs.loc[masque] * poids_col
        denominateur.loc[masque] += poids_col

    resultat = numerateur / denominateur.replace(0, pd.NA)
    return resultat


def poids_normalises(poids_bruts: dict[str, float]) -> dict[str, float]:
    positifs = {k: max(float(v), 0.0) for k, v in poids_bruts.items()}
    total = sum(positifs.values())
    if total == 0 and positifs:
        return {k: 1 / len(positifs) for k in positifs}
    if total == 0:
        return {}
    return {k: v / total for k, v in positifs.items()}


def texte_alerte(score: float | None) -> tuple[str, str]:
    if score is None or pd.isna(score):
        return "alert-orange", "⚠️ Score non disponible : certaines variables manquent ou ne sont pas numériques."
    if score < 45:
        return "alert-red", "🔴 Situation fragile : le score invite à regarder les variables défavorables et les effets de cumul."
    if score < 60:
        return "alert-orange", "🟠 Situation intermédiaire : le résultat dépend fortement des pondérations choisies."
    return "alert-green", "🟢 Situation relativement favorable selon les choix de variables et de pondérations."

# ------------------------------------------------------------
# En-tête
# ------------------------------------------------------------
st.markdown(
    """
    <div class="main-title">
        <h1>ISS communal participatif — Île-de-France</h1>
        <p>Choisir les données, construire les dimensions, pondérer les variables et discuter les résultats.</p>
    </div>
    <div class="stepbar">
        <div class="step"><span>1</span>Données</div>
        <div class="step"><span>2</span>Variables</div>
        <div class="step"><span>3</span>Dimensions</div>
        <div class="step"><span>4</span>Pondérations</div>
        <div class="step"><span>5</span>Résultats</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Choix de la base de données
# ------------------------------------------------------------
st.sidebar.markdown("## 🗂️ Données")

sources_disponibles = chemins_locaux_disponibles()
options_source = ["Données de démonstration", "Importer un fichier CSV ou Excel"]
if sources_disponibles:
    options_source += [f"Source locale — {nom}" for nom in sources_disponibles]

source = st.sidebar.selectbox("Base utilisée", options_source)

df_original = donnees_demo()
nom_source = "Données de démonstration"

try:
    if source == "Importer un fichier CSV ou Excel":
        fichier = st.sidebar.file_uploader("Importer un fichier", type=["csv", "xlsx", "xls"])
        if fichier is not None:
            feuille_importee = None
            if fichier.name.lower().endswith((".xlsx", ".xls")):
                xls = pd.ExcelFile(BytesIO(fichier.getvalue()))
                feuille_importee = st.sidebar.selectbox("Feuille Excel", xls.sheet_names)
            df_original = lire_fichier_importe(fichier, feuille_importee)
            nom_source = fichier.name
        else:
            st.sidebar.info("Aucun fichier importé : la démonstration reste affichée.")
    elif source.startswith("Source locale — "):
        nom = source.replace("Source locale — ", "")
        chemin = sources_disponibles[nom]
        feuilles = lister_feuilles_excel_local(chemin)
        feuille_locale = None
        if feuilles:
            feuille_locale = st.sidebar.selectbox("Feuille Excel", feuilles)
        df_original = lire_fichier_local(chemin, feuille_locale)
        nom_source = nom
except Exception as exc:  # noqa: BLE001
    st.error(f"Impossible de charger la base : {exc}")
    st.stop()

# Nettoyage minimal des noms de colonnes
# On conserve le libellé original, mais on supprime les espaces en trop.
df_original = df_original.copy()
df_original.columns = [str(c).strip() for c in df_original.columns]

if df_original.empty:
    st.error("La base chargée est vide.")
    st.stop()

# ------------------------------------------------------------
# Identification des colonnes utiles
# ------------------------------------------------------------
colonnes = list(df_original.columns)
colonnes_num = colonnes_numeriques_probables(df_original)
colonnes_non_num = [c for c in colonnes if c not in colonnes_num]

st.sidebar.markdown("---")
st.sidebar.markdown("## 🏷️ Colonnes")

col_commune_defaut = "commune" if "commune" in colonnes else (colonnes_non_num[0] if colonnes_non_num else colonnes[0])
col_commune = st.sidebar.selectbox("Nom de la commune / unité observée", colonnes, index=colonnes.index(col_commune_defaut))

option_aucune = "— Aucune —"
colonnes_optionnelles = [option_aucune] + colonnes

col_code = st.sidebar.selectbox(
    "Code commune / identifiant",
    colonnes_optionnelles,
    index=colonnes_optionnelles.index("code_commune") if "code_commune" in colonnes_optionnelles else 0,
)
col_departement = st.sidebar.selectbox(
    "Département",
    colonnes_optionnelles,
    index=colonnes_optionnelles.index("departement") if "departement" in colonnes_optionnelles else 0,
)
col_lat = st.sidebar.selectbox(
    "Latitude",
    colonnes_optionnelles,
    index=colonnes_optionnelles.index("lat") if "lat" in colonnes_optionnelles else 0,
)
col_lon = st.sidebar.selectbox(
    "Longitude",
    colonnes_optionnelles,
    index=colonnes_optionnelles.index("lon") if "lon" in colonnes_optionnelles else 0,
)

# Conversion numérique des colonnes probables

df = df_original.copy()
for col in colonnes_num:
    df[col] = serie_numerique(df[col])

if col_lat != option_aucune:
    df[col_lat] = serie_numerique(df[col_lat])
if col_lon != option_aucune:
    df[col_lon] = serie_numerique(df[col_lon])

# ------------------------------------------------------------
# Dimensions choisies par l'élève
# ------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("## 🧩 Dimensions")

nb_dimensions = st.sidebar.slider("Nombre de dimensions", min_value=1, max_value=8, value=4)
dimensions = []
noms_defaut = [
    "Revenus et inégalités",
    "Éducation",
    "Emploi",
    "Logement",
    "Santé sociale",
    "Environnement",
    "Participation",
    "Autre dimension",
]

for i in range(nb_dimensions):
    nom_dim = st.sidebar.text_input(
        f"Dimension {i + 1}",
        value=noms_defaut[i],
        key=f"nom_dimension_{i}",
    ).strip()
    if nom_dim:
        dimensions.append(nom_dim)

# Évite les doublons vides ou identiques
seen = set()
dimensions = [d for d in dimensions if not (d in seen or seen.add(d))]
if not dimensions:
    dimensions = ["Dimension 1"]

# ------------------------------------------------------------
# Interface principale
# ------------------------------------------------------------
tab_donnees, tab_variables, tab_ponderations, tab_resultats, tab_methode = st.tabs(
    ["1. Données", "2. Variables et dimensions", "3. Pondérations", "4. Carte et résultats", "5. Méthode"]
)

with tab_donnees:
    st.markdown('<div class="card"><h3>Base de données utilisée</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Source", nom_source)
    c2.metric("Lignes", f"{len(df):,}".replace(",", " "))
    c3.metric("Colonnes", len(df.columns))

    st.write("Aperçu des premières lignes :")
    st.dataframe(df.head(30), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><h3>Colonnes numériques détectées</h3>', unsafe_allow_html=True)
    if colonnes_num:
        st.write(", ".join(colonnes_num))
    else:
        st.warning("Aucune colonne numérique n'a été détectée. Vérifie le séparateur décimal ou le format du fichier.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab_variables:
    st.markdown('<div class="card"><h3>Choisir les variables et les rattacher à des dimensions</h3>', unsafe_allow_html=True)
    st.write(
        "L'élève choisit ici les variables statistiques qu'il veut intégrer dans l'indicateur, "
        "puis indique leur dimension, leur sens et leur poids dans la dimension."
    )

    variables_possibles = [c for c in colonnes_num if c not in [col_lat, col_lon]]
    variables_defaut = [
        c for c in [
            "revenu_median",
            "taux_pauvrete",
            "rapport_d9_d1",
            "part_diplomes_superieur",
            "part_actifs_peu_diplomes",
            "taux_chomage",
            "part_logements_suroccupes",
        ]
        if c in variables_possibles
    ]
    if not variables_defaut:
        variables_defaut = variables_possibles[: min(5, len(variables_possibles))]

    variables_choisies = st.multiselect(
        "Variables retenues dans l'indicateur",
        variables_possibles,
        default=variables_defaut,
    )

    if not variables_choisies:
        st.warning("Choisis au moins une variable numérique pour calculer l'indicateur.")
        st.stop()

    lignes_config = []
    for var in variables_choisies:
        nom = str(var).lower()
        if "revenu" in nom or "diplome" in nom and "peu" not in nom:
            sens_defaut = "Favorable : une valeur élevée améliore le score"
        elif "pauvre" in nom or "chom" in nom or "d9" in nom or "inegal" in nom or "peu" in nom or "surocc" in nom:
            sens_defaut = "Défavorable : une valeur élevée dégrade le score"
        else:
            sens_defaut = "Favorable : une valeur élevée améliore le score"

        if "diplome" in nom:
            dim_defaut = next((d for d in dimensions if "éduc" in d.lower() or "educ" in d.lower()), dimensions[0])
        elif "chom" in nom or "emploi" in nom or "actif" in nom:
            dim_defaut = next((d for d in dimensions if "emploi" in d.lower()), dimensions[0])
        elif "logement" in nom or "surocc" in nom:
            dim_defaut = next((d for d in dimensions if "logement" in d.lower()), dimensions[0])
        else:
            dim_defaut = next((d for d in dimensions if "revenu" in d.lower() or "inégal" in d.lower() or "inegal" in d.lower()), dimensions[0])

        lignes_config.append(
            {
                "active": True,
                "variable": var,
                "libellé affiché": var,
                "dimension": dim_defaut,
                "sens": sens_defaut,
                "poids dans la dimension": 1.0,
            }
        )

    config_variables = pd.DataFrame(lignes_config)

    config_variables = st.data_editor(
        config_variables,
        use_container_width=True,
        hide_index=True,
        column_config={
            "active": st.column_config.CheckboxColumn("Active", help="Inclure ou exclure la variable."),
            "variable": st.column_config.TextColumn("Variable", disabled=True),
            "libellé affiché": st.column_config.TextColumn("Libellé affiché"),
            "dimension": st.column_config.SelectboxColumn("Dimension", options=dimensions, required=True),
            "sens": st.column_config.SelectboxColumn(
                "Sens de la variable",
                options=[
                    "Favorable : une valeur élevée améliore le score",
                    "Défavorable : une valeur élevée dégrade le score",
                ],
                required=True,
            ),
            "poids dans la dimension": st.column_config.NumberColumn(
                "Poids dans la dimension",
                min_value=0.0,
                step=0.5,
                format="%.1f",
            ),
        },
        key="editeur_variables",
    )

    st.markdown("</div>", unsafe_allow_html=True)

# On filtre les variables actives après l'éditeur.
config_actives = config_variables[config_variables["active"] == True].copy()  # noqa: E712
if config_actives.empty:
    st.warning("Aucune variable active : impossible de calculer l'indicateur.")
    st.stop()

# ------------------------------------------------------------
# Calcul des scores normalisés de variables et de dimensions
# ------------------------------------------------------------
df_scores = df.copy()
colonnes_scores_variables = []

for _, ligne in config_actives.iterrows():
    var = ligne["variable"]
    score_col = f"__score_var__{var}"
    df_scores[score_col] = normaliser_minmax(df_scores[var], ligne["sens"])
    colonnes_scores_variables.append(score_col)

# Score par dimension
score_dimensions = []
for dimension in dimensions:
    sous_config = config_actives[config_actives["dimension"] == dimension]
    if sous_config.empty:
        continue

    poids_vars = {}
    for _, ligne in sous_config.iterrows():
        var = ligne["variable"]
        score_col = f"__score_var__{var}"
        poids_vars[score_col] = float(ligne["poids dans la dimension"])

    poids_vars_norm = poids_normalises(poids_vars)
    col_score_dimension = f"score_dimension__{dimension}"
    df_scores[col_score_dimension] = moyenne_ponderee_ligne(df_scores, poids_vars_norm).round(1)
    score_dimensions.append(col_score_dimension)

# ------------------------------------------------------------
# Pondérations des dimensions
# ------------------------------------------------------------
with tab_ponderations:
    st.markdown('<div class="card"><h3>Pondérer les dimensions</h3>', unsafe_allow_html=True)
    st.write(
        "Les curseurs ci-dessous permettent de décider collectivement du poids de chaque dimension "
        "dans le score global. Les poids sont ensuite normalisés automatiquement pour totaliser 100 %."
    )

    poids_dimensions_bruts = {}
    cols = st.columns(min(4, len(dimensions)))
    for i, dimension in enumerate(dimensions):
        with cols[i % len(cols)]:
            poids_dimensions_bruts[dimension] = st.slider(
                dimension,
                min_value=0,
                max_value=10,
                value=5,
                key=f"poids_dimension_{dimension}",
            )

    poids_dimensions_norm = poids_normalises(poids_dimensions_bruts)

    recap_poids = pd.DataFrame(
        {
            "Dimension": list(poids_dimensions_norm.keys()),
            "Poids brut": [poids_dimensions_bruts[d] for d in poids_dimensions_norm],
            "Poids normalisé (%)": [round(poids_dimensions_norm[d] * 100, 1) for d in poids_dimensions_norm],
        }
    )
    st.dataframe(recap_poids, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><h3>Récapitulatif des variables actives</h3>', unsafe_allow_html=True)
    st.dataframe(config_actives, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Le dictionnaire de poids est créé ici aussi pour que l'onglet Résultats fonctionne
# même si l'utilisateur ne visite pas l'onglet Pondérations en premier.
poids_dimensions_bruts_global = {
    dimension: st.session_state.get(f"poids_dimension_{dimension}", 5) for dimension in dimensions
}
poids_dimensions_norm_global = poids_normalises(poids_dimensions_bruts_global)

poids_score_global = {}
for dimension, poids_dim in poids_dimensions_norm_global.items():
    col_score_dimension = f"score_dimension__{dimension}"
    if col_score_dimension in df_scores.columns:
        poids_score_global[col_score_dimension] = poids_dim

if poids_score_global:
    df_scores["score_global"] = moyenne_ponderee_ligne(df_scores, poids_score_global).round(1)
else:
    df_scores["score_global"] = pd.NA

# Rang : 1 = score le plus élevé
if df_scores["score_global"].notna().any():
    df_scores["rang"] = df_scores["score_global"].rank(ascending=False, method="min").astype("Int64")
else:
    df_scores["rang"] = pd.NA

# ------------------------------------------------------------
# Résultats et carte
# ------------------------------------------------------------
with tab_resultats:
    st.markdown('<div class="card"><h3>Choisir une commune et analyser son profil</h3>', unsafe_allow_html=True)

    communes_liste = df_scores[col_commune].astype(str).sort_values().unique().tolist()
    commune_choisie = st.selectbox("Commune / unité observée", communes_liste)
    selection = df_scores[df_scores[col_commune].astype(str) == str(commune_choisie)].iloc[0]

    score_global = selection.get("score_global", pd.NA)
    rang = selection.get("rang", pd.NA)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Commune", str(selection[col_commune]))
    if col_departement != option_aucune:
        c2.metric("Département", str(selection[col_departement]))
    else:
        c2.metric("Lignes comparées", len(df_scores))
    c3.metric("Score global", "Non disponible" if pd.isna(score_global) else f"{score_global}/100")
    c4.metric("Rang", "Non disponible" if pd.isna(rang) else f"{int(rang)} / {len(df_scores)}")

    classe_alerte, message_alerte = texte_alerte(None if pd.isna(score_global) else float(score_global))
    st.markdown(f'<div class="{classe_alerte}">{message_alerte}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    left, right = st.columns([1.65, 1], gap="large")

    with left:
        st.markdown('<div class="card"><h3>Carte des scores</h3>', unsafe_allow_html=True)
        carte_possible = col_lat != option_aucune and col_lon != option_aucune
        carte_possible = carte_possible and df_scores[col_lat].notna().any() and df_scores[col_lon].notna().any()

        if carte_possible:
            fig_map = px.scatter_mapbox(
                df_scores,
                lat=col_lat,
                lon=col_lon,
                hover_name=col_commune,
                hover_data={
                    "score_global": True,
                    "rang": True,
                    col_lat: False,
                    col_lon: False,
                },
                color="score_global",
                size="score_global",
                zoom=8,
                height=570,
                color_continuous_scale=["#b93838", "#c97822", "#2e7d61"],
                size_max=34,
            )
            fig_map.update_layout(
                mapbox_style="carto-positron",
                margin={"r": 0, "t": 0, "l": 0, "b": 0},
                coloraxis_colorbar=dict(title="Score"),
            )
            st.plotly_chart(fig_map, use_container_width=True)
            st.caption("La carte dépend des coordonnées latitude/longitude disponibles dans la base.")
        else:
            st.info(
                "Aucune latitude/longitude valide n'a été sélectionnée. "
                "La carte est remplacée par un classement des communes."
            )
            classement = df_scores[[col_commune, "score_global", "rang"]].sort_values("score_global", ascending=False)
            st.dataframe(classement, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card"><h3>Profil par dimension</h3>', unsafe_allow_html=True)

        radar_labels = []
        radar_values = []
        for dimension in dimensions:
            col_dim = f"score_dimension__{dimension}"
            if col_dim in df_scores.columns and pd.notna(selection[col_dim]):
                radar_labels.append(dimension)
                radar_values.append(float(selection[col_dim]))

        if radar_values:
            fig_radar = go.Figure()
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=radar_values + [radar_values[0]],
                    theta=radar_labels + [radar_labels[0]],
                    fill="toself",
                    name=str(selection[col_commune]),
                )
            )
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                height=380,
                margin=dict(l=20, r=20, t=30, b=20),
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.warning("Aucun score de dimension disponible.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><h3>Scores par variable pour la commune sélectionnée</h3>', unsafe_allow_html=True)
    lignes_variables = []
    for _, ligne in config_actives.iterrows():
        var = ligne["variable"]
        score_col = f"__score_var__{var}"
        lignes_variables.append(
            {
                "Variable": ligne["libellé affiché"],
                "Dimension": ligne["dimension"],
                "Valeur brute": selection[var],
                "Score normalisé": selection[score_col],
                "Sens": ligne["sens"].replace(" : ", "\n"),
                "Poids dans la dimension": ligne["poids dans la dimension"],
            }
        )
    table_variables = pd.DataFrame(lignes_variables)
    st.dataframe(table_variables, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><h3>Classement comparatif</h3>', unsafe_allow_html=True)
    colonnes_resultats = [col_commune]
    if col_code != option_aucune:
        colonnes_resultats.append(col_code)
    if col_departement != option_aucune:
        colonnes_resultats.append(col_departement)
    colonnes_resultats += ["score_global", "rang"] + score_dimensions

    classement = df_scores[colonnes_resultats].sort_values("score_global", ascending=False)
    st.dataframe(classement, use_container_width=True, hide_index=True)

    csv = classement.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Télécharger les résultats en CSV",
        data=csv,
        file_name="resultats_iss_communal_participatif.csv",
        mime="text/csv",
    )
    st.markdown("</div>", unsafe_allow_html=True)

with tab_methode:
    st.markdown('<div class="card"><h3>Méthode de calcul</h3>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="method-box">
        <strong>1. Choix des données :</strong> l'utilisateur sélectionne une base et les colonnes utiles.
        <br><br>
        <strong>2. Choix des variables :</strong> chaque variable peut être activée ou désactivée.
        Elle est rattachée à une dimension : revenus, éducation, emploi, logement, etc.
        <br><br>
        <strong>3. Sens de la variable :</strong>
        <ul>
            <li><em>Favorable</em> : plus la valeur est élevée, plus le score augmente.</li>
            <li><em>Défavorable</em> : plus la valeur est élevée, plus le score diminue.</li>
        </ul>
        <strong>4. Normalisation :</strong> chaque variable est transformée en score de 0 à 100 par min-max.
        Le minimum et le maximum sont calculés sur les communes présentes dans la base chargée.
        <br><br>
        <strong>5. Pondération :</strong> les variables sont pondérées à l'intérieur de chaque dimension,
        puis les dimensions sont pondérées pour obtenir le score global.
        <br><br>
        <strong>Point pédagogique central :</strong> le résultat n'est pas neutre. Il dépend des données choisies,
        des variables retenues, du sens donné aux variables, des bornes de normalisation et des pondérations.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><h3>Formule simplifiée</h3>', unsafe_allow_html=True)
    st.latex(r"Score\ variable = \frac{x - min(x)}{max(x)-min(x)} \times 100")
    st.write("Pour une variable défavorable, la formule est inversée :")
    st.latex(r"Score\ variable = \frac{max(x) - x}{max(x)-min(x)} \times 100")
    st.write("Puis :")
    st.latex(r"Score\ dimension = \sum_i poids_i \times Score\ variable_i")
    st.latex(r"Score\ global = \sum_j poids_j \times Score\ dimension_j")
    st.markdown("</div>", unsafe_allow_html=True)
