import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

st.set_page_config(
    page_title="ContaLab — Simulador contable PGC",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PRIMARY = "#8A6A3F"
ACCENT = "#B08D57"
BG = "#F6F1E7"
CARD = "#FBF7F0"
BORDER = "#D8CCBA"
TEXT = "#2F2418"
MUTED = "#7A6A57"
SUCCESS = "#3E6B48"
DANGER = "#9B4B4B"

st.markdown(
    f"""
    <style>
    :root {{
        --bg: {BG};
        --card: {CARD};
        --border: {BORDER};
        --text: {TEXT};
        --muted: {MUTED};
        --primary: {PRIMARY};
        --accent: {ACCENT};
        --success: {SUCCESS};
        --danger: {DANGER};
    }}
    .stApp {{
        background: linear-gradient(180deg, #f8f3ea 0%, #f3ede3 100%);
        color: var(--text);
    }}
    .block-container {{
        padding-top: 1.4rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }}
    h1, h2, h3, h4 {{ color: var(--text); }}
    div[data-baseweb="input"], div[data-baseweb="select"], textarea, .stDateInput > div > div {{
        background: #fffaf3 !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 0.4rem; }}
    .stTabs [data-baseweb="tab"] {{
        background: #efe6d8;
        border-radius: 12px;
        padding: 0.5rem 0.9rem;
        color: var(--text);
        border: 1px solid var(--border);
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #b08d57 0%, #8a6a3f 100%);
        color: white;
        border-color: #8a6a3f;
    }}
    div.stButton > button {{
        background: linear-gradient(135deg, #b08d57 0%, #8a6a3f 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.55rem 1rem;
        font-weight: 600;
    }}
    div.stDownloadButton > button {{
        background: #efe6d8;
        color: var(--text);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.55rem 1rem;
        font-weight: 600;
    }}
    .hero-card, .soft-card {{
        background: rgba(251,247,240,0.92);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 8px 24px rgba(138,106,63,0.08);
    }}
    .metric-card {{
        background: rgba(251,247,240,0.98);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1rem;
        box-shadow: 0 8px 22px rgba(138,106,63,0.06);
        min-height: 112px;
    }}
    .metric-label {{
        font-size: 0.86rem;
        color: var(--muted);
        margin-bottom: 0.35rem;
    }}
    .metric-value {{
        font-size: 1.55rem;
        font-weight: 700;
        color: var(--text);
        line-height: 1.15;
    }}
    .metric-sub {{
        font-size: 0.85rem;
        color: var(--muted);
        margin-top: 0.35rem;
    }}
    .small-note {{
        color: var(--muted);
        font-size: 0.92rem;
    }}
    .status-ok {{ color: var(--success); font-weight: 700; }}
    .status-bad {{ color: var(--danger); font-weight: 700; }}
    .pgc-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.94rem;
        background: rgba(251,247,240,0.98);
        border-radius: 14px;
        overflow: hidden;
    }}
    .pgc-table th {{
        background: #efe6d8;
        padding: 0.45rem 0.7rem;
        text-align: left;
        border-bottom: 1px solid {BORDER};
    }}
    .pgc-table td {{
        padding: 0.35rem 0.7rem;
        border-bottom: 1px solid #e4d8c7;
    }}
    .pgc-title-row td {{
        background: #f0e4d1;
        font-weight: 700;
        border-top: 1px solid {BORDER};
    }}
    .pgc-subtotal td {{
        font-weight: 700;
    }}
    .amount-pos {{
        color: {SUCCESS};
        font-weight: 600;
    }}
    .amount-neg {{
        color: {DANGER};
        font-weight: 600;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------
# Catálogo de cuentas PGC (resumido para docencia)
# --------------------------------------------------------------------
ACCOUNT_CATALOG = [
    # Activo no corriente
    {"codigo": "200", "cuenta": "Propiedad industrial", "tipo": "Activo no corriente", "estado": "Balance"},
    {"codigo": "210", "cuenta": "Inmovilizado material", "tipo": "Activo no corriente", "estado": "Balance"},
    {"codigo": "281", "cuenta": "Amortización acumulada del inmovilizado", "tipo": "Activo no corriente (-)", "estado": "Balance"},

    # Activo corriente
    {"codigo": "300", "cuenta": "Mercaderías", "tipo": "Activo corriente", "estado": "Balance"},
    {"codigo": "430", "cuenta": "Clientes", "tipo": "Activo corriente", "estado": "Balance"},
    {"codigo": "436", "cuenta": "Clientes, efectos comerciales a cobrar", "tipo": "Activo corriente", "estado": "Balance"},
    {"codigo": "570", "cuenta": "Caja", "tipo": "Activo corriente", "estado": "Balance"},
    {"codigo": "572", "cuenta": "Bancos c/c", "tipo": "Activo corriente", "estado": "Balance"},

    # Patrimonio neto
    {"codigo": "100", "cuenta": "Capital social", "tipo": "Patrimonio neto", "estado": "Balance"},
    {"codigo": "113", "cuenta": "Reservas voluntarias", "tipo": "Patrimonio neto", "estado": "Balance"},
    {"codigo": "120", "cuenta": "Resultados de ejercicios anteriores", "tipo": "Patrimonio neto", "estado": "Balance"},
    {"codigo": "129", "cuenta": "Resultado del ejercicio", "tipo": "Patrimonio neto", "estado": "Balance"},

    # Pasivo no corriente
    {"codigo": "170", "cuenta": "Deudas a largo plazo con entidades de crédito", "tipo": "Pasivo no corriente", "estado": "Balance"},

    # Pasivo corriente
    {"codigo": "400", "cuenta": "Proveedores", "tipo": "Pasivo corriente", "estado": "Balance"},
    {"codigo": "410", "cuenta": "Acreedores por prestaciones de servicios", "tipo": "Pasivo corriente", "estado": "Balance"},
    {"codigo": "520", "cuenta": "Deudas a corto plazo con entidades de crédito", "tipo": "Pasivo corriente", "estado": "Balance"},

    # Grupo 6 – Compras y gastos (PyG)
    {"codigo": "600", "cuenta": "Compras de mercaderías", "tipo": "Gasto", "estado": "PyG"},
    {"codigo": "610", "cuenta": "Variación de existencias de mercaderías", "tipo": "Gasto", "estado": "PyG"},
    {"codigo": "621", "cuenta": "Arrendamientos y cánones", "tipo": "Gasto", "estado": "PyG"},
    {"codigo": "628", "cuenta": "Suministros", "tipo": "Gasto", "estado": "PyG"},
    {"codigo": "640", "cuenta": "Sueldos y salarios", "tipo": "Gasto", "estado": "PyG"},
    {"codigo": "642", "cuenta": "Seguridad Social a cargo de la empresa", "tipo": "Gasto", "estado": "PyG"},
    {"codigo": "662", "cuenta": "Intereses de deudas", "tipo": "Gasto", "estado": "PyG"},
    {"codigo": "681", "cuenta": "Amortización del inmovilizado", "tipo": "Gasto", "estado": "PyG"},
    {"codigo": "630", "cuenta": "Impuesto sobre beneficios", "tipo": "Gasto", "estado": "PyG"},

    # Grupo 7 – Ventas e ingresos (PyG)
    {"codigo": "700", "cuenta": "Ventas de mercaderías", "tipo": "Ingreso", "estado": "PyG"},
    {"codigo": "705", "cuenta": "Prestaciones de servicios", "tipo": "Ingreso", "estado": "PyG"},
    {"codigo": "752", "cuenta": "Ingresos por arrendamientos", "tipo": "Ingreso", "estado": "PyG"},
    {"codigo": "759", "cuenta": "Otros ingresos de gestión", "tipo": "Ingreso", "estado": "PyG"},
    {"codigo": "769", "cuenta": "Otros ingresos financieros", "tipo": "Ingreso", "estado": "PyG"},
]

CATALOG_DF = pd.DataFrame(ACCOUNT_CATALOG)
ACCOUNT_OPTIONS = {f"{r['codigo']} — {r['cuenta']}": r['codigo'] for _, r in CATALOG_DF.iterrows()}
CODE_TO_NAME = dict(zip(CATALOG_DF["codigo"], CATALOG_DF["cuenta"]))
CODE_TO_TYPE = dict(zip(CATALOG_DF["codigo"], CATALOG_DF["tipo"]))
CODE_TO_STATE = dict(zip(CATALOG_DF["codigo"], CATALOG_DF["estado"]))

# --------------------------------------------------------------------
# Plantillas PGC
# --------------------------------------------------------------------

BALANCE_TEMPLATE = [
    ("ACTIVO NO CORRIENTE", "", ""),
    ("ANC1", "Inmovilizado intangible", "ANint"),
    ("ANC2", "Inmovilizado material", "ANmat"),
    ("ANC3", "Amortización acumulada inmovilizado", "ANamort"),

    ("ACTIVO CORRIENTE", "", ""),
    ("AC1", "Existencias", "ACexis"),
    ("AC2", "Deudores comerciales y otras cuentas a cobrar", "ACdeu"),
    ("AC3", "Efectivo y otros activos líquidos equivalentes", "ACefec"),

    ("PATRIMONIO NETO", "", ""),
    ("PN1", "Capital", "PNcap"),
    ("PN2", "Reservas", "PNres"),
    ("PN3", "Resultados de ejercicios anteriores", "PNrea"),
    ("PN4", "Resultado del ejercicio", "PNre"),

    ("PASIVO NO CORRIENTE", "", ""),
    ("PNC1", "Deudas a largo plazo", "PNCdeu"),

    ("PASIVO CORRIENTE", "", ""),
    ("PC1", "Proveedores y otras cuentas a pagar", "PCprov"),
    ("PC2", "Deudas a corto plazo", "PCdeuc"),
]

ACCOUNT_TO_BALANCE_EPIG = {
    "200": "ANC1",
    "210": "ANC2",
    "281": "ANC3",
    "300": "AC1",
    "430": "AC2",
    "436": "AC2",
    "570": "AC3",
    "572": "AC3",
    "100": "PN1",
    "113": "PN2",
    "120": "PN3",
    "129": "PN4",
    "170": "PNC1",
    "400": "PC1",
    "410": "PC1",
    "520": "PC2",
}

PYG_TEMPLATE = [
    ("1", "Importe neto de la cifra de negocios"),
    ("2", "Aprovisionamientos"),
    ("3", "Otros ingresos de explotación"),
    ("4", "Gastos de personal"),
    ("5", "Otros gastos de explotación"),
    ("6", "Amortización del inmovilizado"),
    ("7", "Resultado de explotación"),
    ("8", "Ingresos financieros"),
    ("9", "Gastos financieros"),
    ("10", "Resultado financiero"),
    ("11", "Resultado antes de impuestos"),
    ("12", "Impuesto sobre beneficios"),
    ("13", "Resultado del ejercicio"),
]

ACCOUNT_TO_PYG_LINE = {
    "700": "1",
    "705": "1",
    "600": "2",
    "610": "2",
    "752": "3",
    "759": "3",
    "640": "4",
    "642": "4",
    "621": "5",
    "628": "5",
    "681": "6",
    "769": "8",
    "662": "9",
    "630": "12",
}

EXERCISES = [
    {
        "titulo": "Aportación inicial de socios",
        "descripcion": "La sociedad se constituye con 20.000 € ingresados en la cuenta bancaria.",
        "fecha": date(2026, 1, 2),
        "lineas": [("572", 20000.0, 0.0), ("100", 0.0, 20000.0)],
        "explicacion": "Aumenta el activo (bancos) y también el patrimonio neto (capital social).",
    },
    {
        "titulo": "Compra de mercaderías al contado",
        "descripcion": "Se compran mercaderías por 2.500 € que se pagan por banco.",
        "fecha": date(2026, 1, 5),
        "lineas": [("300", 2500.0, 0.0), ("572", 0.0, 2500.0)],
        "explicacion": "Suben existencias y baja la tesorería (banco).",
    },
    {
        "titulo": "Venta de mercaderías a crédito",
        "descripcion": "Se venden mercaderías por 4.000 € a clientes, pendiente de cobro.",
        "fecha": date(2026, 1, 10),
        "lineas": [("430", 4000.0, 0.0), ("700", 0.0, 4000.0)],
        "explicacion": "Sube el crédito a clientes y se reconoce un ingreso de explotación.",
    },
    {
        "titulo": "Registro de nóminas",
        "descripcion": "Nóminas del mes por 1.200 € pagadas por banco.",
        "fecha": date(2026, 1, 31),
        "lineas": [("640", 1200.0, 0.0), ("572", 0.0, 1200.0)],
        "explicacion": "Gasto de personal que reduce el resultado y la tesorería.",
    },
]

# --------------------------------------------------------------------
# Funciones generales
# --------------------------------------------------------------------


def init_state():
    if "journal" not in st.session_state:
        st.session_state.journal = []
    if "entry_lines" not in st.session_state:
        st.session_state.entry_lines = [blank_line(), blank_line()]


def blank_line():
    return {"cuenta": list(ACCOUNT_OPTIONS.keys())[0], "debe": 0.0, "haber": 0.0}


def metric_card(label, value, sub=""):
    st.markdown(
        f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-sub'>{sub}</div></div>",
        unsafe_allow_html=True,
    )


def amount_fmt(x):
    return f"{x:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def build_journal_df(entries):
    rows = []
    for asiento in entries:
        for linea in asiento["lineas"]:
            rows.append(
                {
                    "Asiento": asiento["id"],
                    "Fecha": asiento["fecha"],
                    "Concepto": asiento["concepto"],
                    "Código": linea["codigo"],
                    "Cuenta": CODE_TO_NAME.get(linea["codigo"], linea["codigo"]),
                    "Debe": linea["debe"],
                    "Haber": linea["haber"],
                }
            )
    if not rows:
        return pd.DataFrame(columns=["Asiento", "Fecha", "Concepto", "Código", "Cuenta", "Debe", "Haber"])
    return pd.DataFrame(rows)


def compute_trial_balance(journal_df):
    if journal_df.empty:
        df = CATALOG_DF.copy()
        df["Debe acumulado"] = 0.0
        df["Haber acumulado"] = 0.0
        df["Saldo deudor"] = 0.0
        df["Saldo acreedor"] = 0.0
        return df[["codigo", "cuenta", "tipo", "estado", "Debe acumulado", "Haber acumulado", "Saldo deudor", "Saldo acreedor"]].rename(
            columns={"codigo": "Código", "cuenta": "Cuenta", "tipo": "Tipo", "estado": "Estado"}
        )

    agg = journal_df.groupby(["Código", "Cuenta"], as_index=False)[["Debe", "Haber"]].sum()
    agg["Saldo neto"] = agg["Debe"] - agg["Haber"]
    agg["Saldo deudor"] = agg["Saldo neto"].clip(lower=0)
    agg["Saldo acreedor"] = (-agg["Saldo neto"]).clip(lower=0)
    agg["Tipo"] = agg["Código"].map(CODE_TO_TYPE)
    agg["Estado"] = agg["Código"].map(CODE_TO_STATE)
    return agg.rename(columns={"Debe": "Debe acumulado", "Haber": "Haber acumulado"})[
        ["Código", "Cuenta", "Tipo", "Estado", "Debe acumulado", "Haber acumulado", "Saldo deudor", "Saldo acreedor"]
    ]


def compute_balance_pgc(trial_df):
    if trial_df.empty:
        trial_df = compute_trial_balance(pd.DataFrame())

    df = trial_df.copy()
    df["Saldo"] = df["Saldo deudor"] - df["Saldo acreedor"]
    epig_importes = {code: 0.0 for code, _, _ in BALANCE_TEMPLATE}

    for _, row in df.iterrows():
        codigo = row["Código"]
        saldo = row["Saldo"]
        epig = ACCOUNT_TO_BALANCE_EPIG.get(codigo)
        if not epig:
            continue
        if row["Tipo"] in ["Activo corriente", "Activo no corriente", "Activo no corriente (-)"]:
            importe = saldo
        else:
            importe = -saldo
        epig_importes[epig] += importe

    rows = []
    for code, label, internal in BALANCE_TEMPLATE:
        if code in ["ACTIVO NO CORRIENTE", "ACTIVO CORRIENTE", "PATRIMONIO NETO", "PASIVO NO CORRIENTE", "PASIVO CORRIENTE"]:
            rows.append({"Clave": code, "Epígrafe": label, "Importe": None})
        else:
            imp = epig_importes.get(code, 0.0)
            rows.append({"Clave": code, "Epígrafe": label, "Importe": imp})

    balance_pgc = pd.DataFrame(rows)
    activo_total = balance_pgc.loc[
        balance_pgc["Clave"].str.startswith("AC") | balance_pgc["Clave"].str.startswith("ANC"),
        "Importe",
    ].sum()
    pn_total = balance_pgc.loc[balance_pgc["Clave"].str.startswith("PN"), "Importe"].sum()
    pasivo_total = balance_pgc.loc[
        balance_pgc["Clave"].str.startswith("PNC") | balance_pgc["Clave"].str.startswith("PC"),
        "Importe",
    ].sum()
    return balance_pgc, activo_total, pn_total + pasivo_total, df


def compute_pyg_pgc(trial_df):
    if trial_df.empty:
        trial_df = compute_trial_balance(pd.DataFrame())

    df = trial_df.copy()
    df["Saldo"] = df["Saldo deudor"] - df["Saldo acreedor"]
    pyg_accounts = df[df["Estado"] == "PyG"].copy()

    line_importes = {code: 0.0 for code, _ in PYG_TEMPLATE}

    for _, row in pyg_accounts.iterrows():
        codigo = row["Código"]
        saldo = row["Saldo"]
        line_key = ACCOUNT_TO_PYG_LINE.get(codigo)
        if not line_key:
            continue
        if row["Tipo"] == "Ingreso":
            importe = -saldo
        else:
            importe = saldo
        line_importes[line_key] += importe

    importe_neto_ventas = line_importes["1"]
    aprovisionamientos = line_importes["2"]
    otros_ingresos_expl = line_importes["3"]
    gastos_personal = line_importes["4"]
    otros_gastos_expl = line_importes["5"]
    amortizacion = line_importes["6"]

    resultado_explotacion = (
        importe_neto_ventas
        + otros_ingresos_expl
        - aprovisionamientos
        - gastos_personal
        - otros_gastos_expl
        - amortizacion
    )

    ingresos_financieros = line_importes["8"]
    gastos_financieros = line_importes["9"]
    resultado_financiero = ingresos_financieros - gastos_financieros
    resultado_antes_impuestos = resultado_explotacion + resultado_financiero
    impuesto = line_importes["12"]
    resultado_ejercicio = resultado_antes_impuestos - impuesto

    rows = []
    for code, label in PYG_TEMPLATE:
        if code == "7":
            imp = resultado_explotacion
        elif code == "10":
            imp = resultado_financiero
        elif code == "11":
            imp = resultado_antes_impuestos
        elif code == "13":
            imp = resultado_ejercicio
        else:
            imp = line_importes.get(code, 0.0)
        rows.append({"Clave": code, "Epígrafe": label, "Importe": imp})

    pyg_pgc = pd.DataFrame(rows)
    return pyg_pgc, resultado_ejercicio


def compute_ratios(balance_pgc, pyg_pgc):
    def get_importe(clave):
        v = pyg_pgc.loc[pyg_pgc["Clave"] == clave, "Importe"]
        return float(v.iloc[0]) if not v.empty else 0.0

    activo_corriente = balance_pgc.loc[
        balance_pgc["Clave"].isin(["AC1", "AC2", "AC3"]), "Importe"
    ].sum()
    pasivo_corriente = balance_pgc.loc[
        balance_pgc["Clave"].isin(["PC1", "PC2"]), "Importe"
    ].sum()
    existencias = balance_pgc.loc[balance_pgc["Clave"] == "AC1", "Importe"].sum()
    bancos_caja = balance_pgc.loc[balance_pgc["Clave"] == "AC3", "Importe"].sum()
    pn_total = balance_pgc.loc[balance_pgc["Clave"].str.startswith("PN"), "Importe"].sum()
    pasivo_total = balance_pgc.loc[
        balance_pgc["Clave"].str.startswith("PNC") | balance_pgc["Clave"].str.startswith("PC"),
        "Importe",
    ].sum()
    activo_total = balance_pgc.loc[
        balance_pgc["Clave"].str.startswith("AC") | balance_pgc["Clave"].str.startswith("ANC"),
        "Importe",
    ].sum()

    resultado_ejercicio = get_importe("13")
    ingresos_explotacion = get_importe("1") + get_importe("3")

    def safe_div(a, b):
        return a / b if b not in [0, 0.0, None] else np.nan

    ratios = pd.DataFrame(
        [
            {"Ratio": "Liquidez corriente", "Fórmula": "Activo corriente ÷ Pasivo corriente", "Valor": safe_div(activo_corriente, pasivo_corriente)},
            {"Ratio": "Prueba ácida", "Fórmula": "(AC corr. − Existencias) ÷ Pasivo corriente", "Valor": safe_div(activo_corriente - existencias, pasivo_corriente)},
            {"Ratio": "Tesorería", "Fórmula": "Efectivo ÷ Pasivo corriente", "Valor": safe_div(bancos_caja, pasivo_corriente)},
            {"Ratio": "Endeudamiento", "Fórmula": "Pasivo total ÷ Patrimonio neto", "Valor": safe_div(pasivo_total, pn_total)},
            {"Ratio": "ROA", "Fórmula": "Resultado ejercicio ÷ Activo total", "Valor": safe_div(resultado_ejercicio, activo_total)},
            {"Ratio": "Margen neto", "Fórmula": "Resultado ejercicio ÷ Ingresos de explotación", "Valor": safe_div(resultado_ejercicio, ingresos_explotacion)},
        ]
    )
    return ratios


def compute_cash_flow(journal_df):
    if journal_df.empty:
        return pd.DataFrame(
            [
                {"Actividad": "Explotación", "Flujo": 0.0},
                {"Actividad": "Inversión", "Flujo": 0.0},
                {"Actividad": "Financiación", "Flujo": 0.0},
                {"Actividad": "Flujo neto", "Flujo": 0.0},
            ]
        )

    flow = {"Explotación": 0.0, "Inversión": 0.0, "Financiación": 0.0}
    for asiento_id, grp in journal_df.groupby("Asiento"):
        cash_codes = {"570", "572"}
        touch_cash = grp[grp["Código"].isin(cash_codes)]
        if touch_cash.empty:
            continue
        cash_effect = touch_cash["Debe"].sum() - touch_cash["Haber"].sum()
        other_codes = set(grp[~grp["Código"].isin(cash_codes)]["Código"].tolist())

        if other_codes & {"210", "281"}:
            flow["Inversión"] += cash_effect
        elif other_codes & {"100", "113", "170", "520", "662"}:
            flow["Financiación"] += cash_effect
        else:
            flow["Explotación"] += cash_effect

    data = [{"Actividad": k, "Flujo": v} for k, v in flow.items()]
    data.append({"Actividad": "Flujo neto", "Flujo": sum(flow.values())})
    return pd.DataFrame(data)

# --------------------------------------------------------------------
# Amortizaciones: métodos lineal, porcentaje constante y unidades
# --------------------------------------------------------------------


def amortizacion_lineal(coste, valor_residual, vida):
    base = coste - valor_residual
    if vida <= 0 or base <= 0:
        return pd.DataFrame(columns=["Año", "Cuota", "Amortización acumulada", "Valor neto"])

    cuota = base / vida
    rows = []
    acum = 0.0
    valor = coste
    for year in range(1, vida + 1):
        if year == vida:
            cuota_year = valor - valor_residual
        else:
            cuota_year = cuota
        acum += cuota_year
        valor -= cuota_year
        rows.append(
            {
                "Año": year,
                "Cuota": cuota_year,
                "Amortización acumulada": acum,
                "Valor neto": valor,
            }
        )
    return pd.DataFrame(rows)


def amortizacion_porcentaje_constante(coste, valor_residual, vida, porcentaje):
    if porcentaje <= 0 or porcentaje >= 1:
        return pd.DataFrame(columns=["Año", "Cuota", "Amortización acumulada", "Valor neto"])

    rows = []
    acum = 0.0
    valor = coste
    year = 1
    while valor > valor_residual and year <= vida:
        cuota = (valor - valor_residual) * porcentaje
        if valor - cuota < valor_residual:
            cuota = valor - valor_residual
        acum += cuota
        valor -= cuota
        rows.append(
            {
                "Año": year,
                "Cuota": cuota,
                "Amortización acumulada": acum,
                "Valor neto": valor,
            }
        )
        year += 1
    return pd.DataFrame(rows)


def amortizacion_unidades_produccion(coste, valor_residual, unidades_totales, unidades_por_anio):
    base = coste - valor_residual
    if unidades_totales <= 0 or base <= 0:
        return pd.DataFrame(columns=["Año", "Cuota", "Amortización acumulada", "Valor neto"])

    rows = []
    acum = 0.0
    valor = coste
    for i, uds in enumerate(unidades_por_anio, start=1):
        cuota = base * (uds / unidades_totales)
        if valor - cuota < valor_residual:
            cuota = valor - valor_residual
        acum += cuota
        valor -= cuota
        rows.append(
            {
                "Año": i,
                "Cuota": cuota,
                "Amortización acumulada": acum,
                "Valor neto": valor,
            }
        )
        if valor <= valor_residual:
            break

    return pd.DataFrame(rows)

# --------------------------------------------------------------------
# Gestión de asientos
# --------------------------------------------------------------------


def add_entry(fecha, concepto, lineas):
    new_id = len(st.session_state.journal) + 1
    payload = {
        "id": new_id,
        "fecha": pd.to_datetime(fecha).date(),
        "concepto": concepto.strip() if concepto.strip() else f"Asiento {new_id}",
        "lineas": lineas,
    }
    st.session_state.journal.append(payload)


def reset_all():
    st.session_state.journal = []
    st.session_state.entry_lines = [blank_line(), blank_line()]


def exercise_to_entry(ex):
    return {
        "fecha": ex["fecha"],
        "concepto": ex["titulo"],
        "lineas": [{"codigo": c, "debe": d, "haber": h} for c, d, h in ex["lineas"]],
    }


# --------------------------------------------------------------------
# UI principal
# --------------------------------------------------------------------

init_state()

st.markdown(
    """
    <div class='hero-card'>
        <h1 style='margin-bottom:0.35rem;'>ContaLab — simulador contable PGC</h1>
        <div class='small-note'>
        Introduce asientos con cuentas PGC reales y observa al instante el impacto en el libro diario, el mayor, el balance de comprobación, 
        el balance en formato PGC y la cuenta de pérdidas y ganancias oficial.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("Guía rápida", expanded=False):
    st.markdown(
        """
- Usa cuentas como 570 Caja, 572 Bancos, 430 Clientes, 400 Proveedores, 600 Compras, 700 Ventas, etc.
- Guarda el asiento y revisa el impacto en el balance y la PyG en formato PGC.
- Los estados se muestran siempre completos (todas las líneas) aunque no tengan importe.
        """
    )

left, right = st.columns([1.2, 1])
with left:
    st.markdown("### Nuevo asiento")
    fecha = st.date_input("Fecha", value=date.today())
    concepto = st.text_input("Concepto", value="")

    top_actions = st.columns([1, 1, 1])
    if top_actions[0].button("Añadir línea"):
        st.session_state.entry_lines.append(blank_line())
    if top_actions[1].button("Quitar última línea"):
        if len(st.session_state.entry_lines) > 2:
            st.session_state.entry_lines.pop()
    if top_actions[2].button("Vaciar borrador"):
        st.session_state.entry_lines = [blank_line(), blank_line()]

    draft_lines = []
    for i, line in enumerate(st.session_state.entry_lines):
        c1, c2, c3 = st.columns([2.3, 1, 1])
        cuenta_opt = c1.selectbox(
            f"Cuenta línea {i+1}",
            options=list(ACCOUNT_OPTIONS.keys()),
            index=list(ACCOUNT_OPTIONS.keys()).index(line["cuenta"]) if line["cuenta"] in ACCOUNT_OPTIONS else 0,
            key=f"cuenta_{i}",
        )
        debe_val = c2.number_input(
            f"Debe {i+1}",
            min_value=0.0,
            step=10.0,
            value=float(line["debe"]),
            key=f"debe_{i}",
        )
        haber_val = c3.number_input(
            f"Haber {i+1}",
            min_value=0.0,
            step=10.0,
            value=float(line["haber"]),
            key=f"haber_{i}",
        )
        st.session_state.entry_lines[i] = {"cuenta": cuenta_opt, "debe": debe_val, "haber": haber_val}
        draft_lines.append({"codigo": ACCOUNT_OPTIONS[cuenta_opt], "debe": debe_val, "haber": haber_val})

    total_debe = sum(x["debe"] for x in draft_lines)
    total_haber = sum(x["haber"] for x in draft_lines)
    diff = total_debe - total_haber

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Debe borrador", amount_fmt(total_debe), "Suma del Debe")
    with c2:
        metric_card("Haber borrador", amount_fmt(total_haber), "Suma del Haber")
    with c3:
        estado_txt = "Cuadrado" if abs(diff) < 0.005 and total_debe > 0 else "No cuadrado"
        sub = "Listo para guardar" if estado_txt == "Cuadrado" else f"Diferencia: {amount_fmt(diff)}"
        metric_card("Estado del asiento", estado_txt, sub)

    valid_lines = [x for x in draft_lines if (x["debe"] > 0 or x["haber"] > 0)]
    if st.button("Guardar asiento"):
        invalid_both = any(x["debe"] > 0 and x["haber"] > 0 for x in valid_lines)
        invalid_empty = len(valid_lines) < 2
        if invalid_empty:
            st.error("Debes introducir al menos dos líneas con importe.")
        elif invalid_both:
            st.error("Una misma línea no puede tener importe simultáneo en Debe y Haber.")
        elif abs(diff) >= 0.005:
            st.error("El asiento no cuadra: el Debe y el Haber no coinciden.")
        else:
            add_entry(fecha, concepto, valid_lines)
            st.success("Asiento guardado correctamente.")
            st.session_state.entry_lines = [blank_line(), blank_line()]
            st.rerun()

with right:
    st.markdown("### Ejercicios guiados")
    st.markdown(
        "<div class='soft-card'>Selecciona un caso y cárgalo como asiento modelo o añádelo directamente al diario.</div>",
        unsafe_allow_html=True,
    )
    selected_ex = st.selectbox("Caso práctico", options=[ex["titulo"] for ex in EXERCISES])
    ex_obj = next(ex for ex in EXERCISES if ex["titulo"] == selected_ex)
    st.info(ex_obj["descripcion"])
    st.caption(ex_obj["explicacion"])

    action1, action2 = st.columns(2)
    if action1.button("Cargar al borrador"):
        st.session_state.entry_lines = []
        for codigo, debe, haber in ex_obj["lineas"]:
            st.session_state.entry_lines.append(
                {
                    "cuenta": next(k for k, v in ACCOUNT_OPTIONS.items() if v == codigo),
                    "debe": float(debe),
                    "haber": float(haber),
                }
            )
        st.rerun()
    if action2.button("Añadir directo al diario"):
        add_entry(
            ex_obj["fecha"],
            ex_obj["titulo"],
            [{"codigo": c, "debe": d, "haber": h} for c, d, h in ex_obj["lineas"]],
        )
        st.success("Ejercicio añadido al diario.")
        st.rerun()

    st.markdown("### Control del proyecto")
    ctrl1, ctrl2 = st.columns(2)
    if ctrl1.button("Cargar demo inicial"):
        reset_all()
        for ex in EXERCISES[:3]:
            add_entry(
                ex["fecha"],
                ex["titulo"],
                [{"codigo": c, "debe": d, "haber": h} for c, d, h in ex["lineas"]],
            )
        st.rerun()
    if ctrl2.button("Reiniciar todo"):
        reset_all()
        st.rerun()

journal_df = build_journal_df(st.session_state.journal)
trial_df = compute_trial_balance(journal_df)

balance_pgc, activo_total, pn_pasivo_total, balance_raw_df = compute_balance_pgc(trial_df)
pyg_pgc, resultado = compute_pyg_pgc(trial_df)
ratios_df = compute_ratios(balance_pgc, pyg_pgc)
cf_df = compute_cash_flow(journal_df)

entries_count = len(st.session_state.journal)
cuadra_global = journal_df["Debe"].sum() == journal_df["Haber"].sum() if not journal_df.empty else True

m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("Asientos registrados", str(entries_count), "Libro diario activo")
with m2:
    metric_card("Resultado del ejercicio", amount_fmt(resultado), "Según PyG PGC")
with m3:
    metric_card("Activo total", amount_fmt(activo_total), "Balance PGC")
with m4:
    metric_card("Balance cuadrado", "Sí" if cuadra_global else "No", amount_fmt(activo_total - pn_pasivo_total))

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
    [
        "Libro diario",
        "Libro mayor",
        "Balance comprobación",
        "Balance PGC",
        "PyG PGC",
        "Ratios",
        "Flujo efectivo",
        "Amortizaciones",
    ]
)

with tab1:
    st.markdown("### Libro diario")
    if journal_df.empty:
        st.warning("Todavía no hay asientos registrados.")
    else:
        diario_show = journal_df.copy()
        diario_show["Debe"] = diario_show["Debe"].map(amount_fmt)
        diario_show["Haber"] = diario_show["Haber"].map(amount_fmt)
        st.dataframe(diario_show, use_container_width=True, hide_index=True)
        st.download_button(
            "Descargar diario en CSV",
            data=journal_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="libro_diario_contalab.csv",
            mime="text/csv",
        )

with tab2:
    st.markdown("### Libro mayor")
    if journal_df.empty:
        st.info("Añade asientos para ver movimientos por cuenta.")
    else:
        for codigo, grp in journal_df.groupby("Código"):
            with st.expander(f"{codigo} — {CODE_TO_NAME.get(codigo, codigo)}"):
                g = grp[["Fecha", "Concepto", "Debe", "Haber"]].copy()
                g["Debe"] = g["Debe"].map(amount_fmt)
                g["Haber"] = g["Haber"].map(amount_fmt)
                st.dataframe(g, use_container_width=True, hide_index=True)
                saldo = grp["Debe"].sum() - grp["Haber"].sum()
                st.caption(f"Saldo neto: {amount_fmt(saldo)}")

with tab3:
    st.markdown("### Balance de comprobación")
    bc = trial_df.copy()
    if not bc.empty:
        for col in ["Debe acumulado", "Haber acumulado", "Saldo deudor", "Saldo acreedor"]:
            bc[col] = bc[col].map(amount_fmt)
    st.dataframe(bc, use_container_width=True, hide_index=True)
    total_debe = trial_df["Debe acumulado"].sum() if not trial_df.empty else 0.0
    total_haber = trial_df["Haber acumulado"].sum() if not trial_df.empty else 0.0
    if abs(total_debe - total_haber) < 0.005:
        st.markdown(
            "<span class='status-ok'>✓ El balance de comprobación cuadra.</span>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<span class='status-bad'>✗ El balance de comprobación no cuadra.</span>",
            unsafe_allow_html=True,
        )

with tab4:
    st.markdown("### Balance en formato PGC (simplificado)")

    bal_show = balance_pgc.copy()

    def format_balance_label(row):
        code = row["Clave"]
        label = row["Epígrafe"]
        if code in ["ACTIVO NO CORRIENTE", "ACTIVO CORRIENTE", "PATRIMONIO NETO", "PASIVO NO CORRIENTE", "PASIVO CORRIENTE"]:
            return f"<strong>{label}</strong>"
        else:
            return f"&nbsp;&nbsp;&nbsp;{label}"

    def format_balance_importe(val):
        if val is None:
            return ""
        css_class = "amount-pos" if val >= 0 else "amount-neg"
        return f"<span class='{css_class}'>{amount_fmt(val)}</span>"

    bal_show["Etiqueta"] = bal_show.apply(format_balance_label, axis=1)
    bal_show["ValorFmt"] = bal_show["Importe"].apply(format_balance_importe)

    col_activo, col_pn_pasivo = st.columns(2)

    with col_activo:
        st.markdown("#### Activo")
        activo_df = bal_show[
            bal_show["Clave"].str.startswith("AC")
            | bal_show["Clave"].str.startswith("ANC")
            | (bal_show["Clave"] == "ACTIVO NO CORRIENTE")
            | (bal_show["Clave"] == "ACTIVO CORRIENTE")
        ].copy()
        activo_df = activo_df[["Etiqueta", "ValorFmt"]]
        html_activo = activo_df.to_html(
            escape=False,
            index=False,
            header=["Epígrafe", "Importe"],
            classes="pgc-table",
        )
        st.markdown(html_activo, unsafe_allow_html=True)

    with col_pn_pasivo:
        st.markdown("#### Patrimonio neto y Pasivo")
        pn_pasivo_df = bal_show[
            ~(bal_show["Clave"].str.startswith("AC") | bal_show["Clave"].str.startswith("ANC"))
        ].copy()
        pn_pasivo_df = pn_pasivo_df[["Etiqueta", "ValorFmt"]]
        html_pn = pn_pasivo_df.to_html(
            escape=False,
            index=False,
            header=["Epígrafe", "Importe"],
            classes="pgc-table",
        )
        st.markdown(html_pn, unsafe_allow_html=True)

    st.caption(
        f"Activo total: {amount_fmt(activo_total)} | Patrimonio neto + Pasivo: {amount_fmt(pn_pasivo_total)}"
    )

    st.markdown("#### Detalle de cuentas de balance")
    if balance_raw_df.empty:
        st.info("Sin movimientos de balance todavía.")
    else:
        detail = balance_raw_df.copy()
        detail["Saldo"] = detail["Saldo deudor"] - detail["Saldo acreedor"]
        detail["Epígrafe PGC"] = detail["Código"].map(ACCOUNT_TO_BALANCE_EPIG).fillna("—")
        detail_show = detail[["Epígrafe PGC", "Código", "Cuenta", "Tipo", "Saldo"]].copy()
        detail_show["Saldo"] = detail_show["Saldo"].map(amount_fmt)
        st.dataframe(detail_show, use_container_width=True, hide_index=True)
        st.caption(
            "Esta tabla muestra todas las cuentas de balance y el epígrafe PGC en el que se integran "
            "(por ejemplo, las deudas con entidades de crédito: 170 a largo plazo, 520 a corto plazo)."
        )

with tab5:
    st.markdown("### Cuenta de pérdidas y ganancias (formato PGC)")

    pyg_show = pyg_pgc.copy()

    def format_pyg_label(row):
        clave = row["Clave"]
        label = row["Epígrafe"]
        if clave in ["7", "10", "11", "13"]:
            return f"<strong>{label}</strong>"
        else:
            return f"&nbsp;&nbsp;&nbsp;{label}"

    def format_pyg_importe(row):
        val = row["Importe"]
        css_class = "amount-pos" if val >= 0 else "amount-neg"
        return f"<span class='{css_class}'>{amount_fmt(val)}</span>"

    pyg_show["Etiqueta"] = pyg_show.apply(format_pyg_label, axis=1)
    pyg_show["ValorFmt"] = pyg_show.apply(format_pyg_importe, axis=1)

    html_pyg = pyg_show[["Etiqueta", "ValorFmt"]].to_html(
        escape=False,
        index=False,
        header=["Epígrafe", "Importe"],
        classes="pgc-table",
    )
    st.markdown(html_pyg, unsafe_allow_html=True)

    st.caption(
        "Estructura docente basada en el modelo normal del PGC: resultado de explotación, "
        "resultado financiero y resultado antes de impuestos hasta el resultado del ejercicio."
    )

with tab6:
    st.markdown("### Ratios")
    ratios_show = ratios_df.copy()
    ratios_show["Valor"] = ratios_show["Valor"].apply(
        lambda x: "—" if pd.isna(x) else f"{x:.2f}x"
    )
    st.dataframe(ratios_show, use_container_width=True, hide_index=True)

with tab7:
    st.markdown("### Estado de flujos de efectivo simplificado")
    cf_show = cf_df.copy()
    cf_show["Flujo"] = cf_show["Flujo"].map(amount_fmt)
    st.dataframe(cf_show, use_container_width=True, hide_index=True)
    st.caption("Clasificación orientativa para uso didáctico: explotación, inversión y financiación.")

with tab8:
    st.markdown("### Calculadora de amortizaciones")

    st.markdown(
        "<div class='soft-card'>Elige el método de amortización y los parámetros del activo para ver el cuadro año a año.</div>",
        unsafe_allow_html=True,
    )

    metodo = st.selectbox(
        "Método de amortización",
        options=["Lineal", "Porcentaje constante (degresivo)", "Unidades de producción"],
    )

    col1, col2 = st.columns(2)
    with col1:
        coste = st.number_input("Coste de adquisición", min_value=0.0, value=10000.0, step=500.0)
        valor_residual = st.number_input("Valor residual", min_value=0.0, value=0.0, step=100.0)
    with col2:
        vida_util = st.number_input("Vida útil (años)", min_value=1, value=5, step=1)

    df_amort = pd.DataFrame()

    if metodo == "Lineal":
        df_amort = amortizacion_lineal(coste, valor_residual, int(vida_util))

    elif metodo == "Porcentaje constante (degresivo)":
        porcentaje_anual = st.slider("Porcentaje anual", min_value=5, max_value=50, value=20, step=1)
        df_amort = amortizacion_porcentaje_constante(
            coste,
            valor_residual,
            int(vida_util),
            porcentaje_anual / 100.0,
        )

    else:  # Unidades de producción
        unidades_totales = st.number_input("Unidades totales previstas", min_value=1.0, value=100000.0, step=1000.0)
        st.caption("Introduce las unidades por año (separadas por comas): por ejemplo 20000, 25000, 30000, 15000, 10000.")
        unidades_str = st.text_input("Unidades por año", value="20000, 25000, 30000, 15000, 10000")
        try:
            unidades_lista = [float(x.strip()) for x in unidades_str.split(",") if x.strip() != ""]
        except ValueError:
            unidades_lista = []
            st.error("Revisa el formato de las unidades por año (usa solo números y comas).")

        if unidades_lista:
            df_amort = amortizacion_unidades_produccion(
                coste,
                valor_residual,
                unidades_totales,
                unidades_lista,
            )

    if df_amort is not None and not df_amort.empty:
        df_show = df_amort.copy()
        for col in ["Cuota", "Amortización acumulada", "Valor neto"]:
            df_show[col] = df_show[col].map(amount_fmt)

        st.markdown("#### Cuadro de amortización")
        st.dataframe(df_show, use_container_width=True, hide_index=True)

        st.download_button(
            "Descargar cuadro en CSV",
            data=df_amort.to_csv(index=False).encode("utf-8-sig"),
            file_name="cuadro_amortizacion_contalab.csv",
            mime="text/csv",
        )
    else:
        st.info("Introduce parámetros válidos para ver el cuadro de amortización.")
