import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

st.set_page_config(
    page_title="ContaLab — Simulador contable",
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
    table {{ border-collapse: collapse; }}
    thead tr th {{
        background: #efe6d8 !important;
        color: var(--text) !important;
    }}
    tbody tr:nth-child(even) {{ background: rgba(239,230,216,0.35); }}
    .status-ok {{ color: var(--success); font-weight: 700; }}
    .status-bad {{ color: var(--danger); font-weight: 700; }}
    </style>
    """,
    unsafe_allow_html=True,
)

ACCOUNT_CATALOG = [
    {"codigo": "100", "cuenta": "Caja", "tipo": "Activo corriente", "estado": "Balance"},
    {"codigo": "101", "cuenta": "Bancos", "tipo": "Activo corriente", "estado": "Balance"},
    {"codigo": "110", "cuenta": "Clientes", "tipo": "Activo corriente", "estado": "Balance"},
    {"codigo": "120", "cuenta": "Existencias", "tipo": "Activo corriente", "estado": "Balance"},
    {"codigo": "150", "cuenta": "Inmovilizado material", "tipo": "Activo no corriente", "estado": "Balance"},
    {"codigo": "159", "cuenta": "Amortización acumulada inmovilizado", "tipo": "Activo no corriente (-)", "estado": "Balance"},
    {"codigo": "170", "cuenta": "HP IVA soportado", "tipo": "Activo corriente", "estado": "Balance"},
    {"codigo": "180", "cuenta": "Gastos anticipados", "tipo": "Activo corriente", "estado": "Balance"},
    {"codigo": "200", "cuenta": "Capital social", "tipo": "Patrimonio neto", "estado": "Balance"},
    {"codigo": "210", "cuenta": "Reservas", "tipo": "Patrimonio neto", "estado": "Balance"},
    {"codigo": "220", "cuenta": "Resultado del ejercicio", "tipo": "Patrimonio neto", "estado": "Balance"},
    {"codigo": "300", "cuenta": "Proveedores", "tipo": "Pasivo corriente", "estado": "Balance"},
    {"codigo": "310", "cuenta": "Deudas a corto plazo", "tipo": "Pasivo corriente", "estado": "Balance"},
    {"codigo": "320", "cuenta": "Deudas a largo plazo", "tipo": "Pasivo no corriente", "estado": "Balance"},
    {"codigo": "330", "cuenta": "HP IVA repercutido", "tipo": "Pasivo corriente", "estado": "Balance"},
    {"codigo": "400", "cuenta": "Ventas", "tipo": "Ingreso", "estado": "PyG"},
    {"codigo": "401", "cuenta": "Otros ingresos", "tipo": "Ingreso", "estado": "PyG"},
    {"codigo": "500", "cuenta": "Compras", "tipo": "Gasto", "estado": "PyG"},
    {"codigo": "510", "cuenta": "Sueldos y salarios", "tipo": "Gasto", "estado": "PyG"},
    {"codigo": "520", "cuenta": "Alquileres", "tipo": "Gasto", "estado": "PyG"},
    {"codigo": "530", "cuenta": "Suministros", "tipo": "Gasto", "estado": "PyG"},
    {"codigo": "540", "cuenta": "Amortización del inmovilizado", "tipo": "Gasto", "estado": "PyG"},
    {"codigo": "550", "cuenta": "Gastos financieros", "tipo": "Gasto", "estado": "PyG"},
    {"codigo": "560", "cuenta": "Impuesto sobre beneficios", "tipo": "Gasto", "estado": "PyG"},
]

CATALOG_DF = pd.DataFrame(ACCOUNT_CATALOG)
ACCOUNT_OPTIONS = {f"{r['codigo']} — {r['cuenta']}": r['codigo'] for _, r in CATALOG_DF.iterrows()}
CODE_TO_NAME = dict(zip(CATALOG_DF["codigo"], CATALOG_DF["cuenta"]))
CODE_TO_TYPE = dict(zip(CATALOG_DF["codigo"], CATALOG_DF["tipo"]))
CODE_TO_STATE = dict(zip(CATALOG_DF["codigo"], CATALOG_DF["estado"]))

EXERCISES = [
    {
        "titulo": "Aportación inicial de socios",
        "descripcion": "La empresa recibe 20.000 € en banco como aportación inicial de capital.",
        "fecha": date(2026, 1, 2),
        "lineas": [("101", 20000.0, 0.0), ("200", 0.0, 20000.0)],
        "explicacion": "Aumenta el activo (bancos) y también el patrimonio neto (capital social).",
    },
    {
        "titulo": "Compra de mercaderías al contado",
        "descripcion": "Se compran existencias por 2.500 € y se pagan por banco.",
        "fecha": date(2026, 1, 5),
        "lineas": [("120", 2500.0, 0.0), ("101", 0.0, 2500.0)],
        "explicacion": "No cambia el total del activo, solo su composición: suben existencias y baja banco.",
    },
    {
        "titulo": "Venta a crédito",
        "descripcion": "Se venden mercaderías por 4.000 € a clientes pendientes de cobro.",
        "fecha": date(2026, 1, 10),
        "lineas": [("110", 4000.0, 0.0), ("400", 0.0, 4000.0)],
        "explicacion": "Sube clientes en el activo y aparece un ingreso que mejora el resultado.",
    },
    {
        "titulo": "Registro de nóminas",
        "descripcion": "Se pagan salarios por 1.200 € desde banco.",
        "fecha": date(2026, 1, 31),
        "lineas": [("510", 1200.0, 0.0), ("101", 0.0, 1200.0)],
        "explicacion": "El gasto reduce el resultado del ejercicio y baja la tesorería.",
    },
]


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


def compute_balance_and_pyg(trial_df):
    if trial_df.empty:
        trial_df = compute_trial_balance(pd.DataFrame())

    balance_df = trial_df.copy()
    balance_df["Saldo"] = balance_df["Saldo deudor"] - balance_df["Saldo acreedor"]

    income_total = balance_df.loc[balance_df["Estado"] == "PyG", :].copy()
    ingresos = income_total.loc[income_total["Tipo"] == "Ingreso", "Saldo"].sum() * -1
    gastos = income_total.loc[income_total["Tipo"] == "Gasto", "Saldo"].sum()
    resultado = ingresos - gastos

    balance_rows = []
    for _, row in balance_df.iterrows():
        if row["Estado"] == "Balance":
            saldo = row["Saldo"]
            if row["Tipo"] == "Activo no corriente (-)":
                saldo = saldo
            balance_rows.append({"Tipo": row["Tipo"], "Cuenta": row["Cuenta"], "Saldo": saldo})

    balance_out = pd.DataFrame(balance_rows)
    if balance_out.empty:
        balance_out = pd.DataFrame(columns=["Tipo", "Cuenta", "Saldo"])

    if not balance_out.empty:
        balance_out = pd.concat(
            [
                balance_out,
                pd.DataFrame(
                    [{"Tipo": "Patrimonio neto", "Cuenta": "Resultado del ejercicio", "Saldo": -resultado}]
                ),
            ],
            ignore_index=True,
        )

    pyg_out = pd.DataFrame(
        [
            {"Concepto": "Ingresos", "Importe": ingresos},
            {"Concepto": "Gastos", "Importe": gastos},
            {"Concepto": "Resultado del ejercicio", "Importe": resultado},
        ]
    )
    return balance_out, pyg_out, resultado


def compute_ratios(balance_df, pyg_df):
    def sum_type(tipo):
        if balance_df.empty:
            return 0.0
        return balance_df.loc[balance_df["Tipo"] == tipo, "Saldo"].sum()

    activo_corriente = sum_type("Activo corriente")
    activo_no_corriente = sum_type("Activo no corriente") + sum_type("Activo no corriente (-)")
    patrimonio = sum_type("Patrimonio neto") * -1
    pasivo_corriente = sum_type("Pasivo corriente") * -1
    pasivo_no_corriente = sum_type("Pasivo no corriente") * -1
    existencias = (
        balance_df.loc[balance_df["Cuenta"] == "Existencias", "Saldo"].sum() if not balance_df.empty else 0.0
    )
    bancos = (
        balance_df.loc[balance_df["Cuenta"].isin(["Caja", "Bancos"]), "Saldo"].sum()
        if not balance_df.empty
        else 0.0
    )
    activo_total = activo_corriente + activo_no_corriente
    ingresos = pyg_df.loc[pyg_df["Concepto"] == "Ingresos", "Importe"].sum()
    resultado = pyg_df.loc[pyg_df["Concepto"] == "Resultado del ejercicio", "Importe"].sum()

    def safe_div(a, b):
        return a / b if b not in [0, 0.0, None] else np.nan

    ratios = pd.DataFrame(
        [
            {"Ratio": "Liquidez corriente", "Fórmula": "Activo corriente ÷ Pasivo corriente", "Valor": safe_div(activo_corriente, pasivo_corriente)},
            {"Ratio": "Prueba ácida", "Fórmula": "(Activo corriente − Existencias) ÷ Pasivo corriente", "Valor": safe_div(activo_corriente - existencias, pasivo_corriente)},
            {"Ratio": "Tesorería", "Fórmula": "(Caja + Bancos) ÷ Pasivo corriente", "Valor": safe_div(bancos, pasivo_corriente)},
            {"Ratio": "Endeudamiento", "Fórmula": "Pasivo total ÷ Patrimonio neto", "Valor": safe_div(pasivo_corriente + pasivo_no_corriente, patrimonio)},
            {"Ratio": "ROA", "Fórmula": "Resultado ÷ Activo total", "Valor": safe_div(resultado, activo_total)},
            {"Ratio": "Margen neto", "Fórmula": "Resultado ÷ Ingresos", "Valor": safe_div(resultado, ingresos)},
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
        cash_codes = {"100", "101"}
        touch_cash = grp[grp["Código"].isin(cash_codes)]
        if touch_cash.empty:
            continue
        cash_effect = touch_cash["Debe"].sum() - touch_cash["Haber"].sum()
        other_codes = set(grp[~grp["Código"].isin(cash_codes)]["Código"].tolist())

        if other_codes & {"150", "159"}:
            flow["Inversión"] += cash_effect
        elif other_codes & {"200", "210", "310", "320", "550"}:
            flow["Financiación"] += cash_effect
        else:
            flow["Explotación"] += cash_effect

    data = [{"Actividad": k, "Flujo": v} for k, v in flow.items()]
    data.append({"Actividad": "Flujo neto", "Flujo": sum(flow.values())})
    return pd.DataFrame(data)


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


init_state()

st.markdown(
    """
    <div class='hero-card'>
        <h1 style='margin-bottom:0.35rem;'>ContaLab — simulador contable para estudiantes</h1>
        <div class='small-note'>Introduce asientos y observa al instante cómo cambian el libro diario, el mayor, el balance de comprobación, el balance, la cuenta de pérdidas y ganancias, el flujo de efectivo y los ratios.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("Guía rápida", expanded=False):
    st.markdown(
        """
- Añade líneas al asiento y comprueba que el total del Debe coincide con el Haber.
- Guarda el asiento y revisa el impacto en las pestañas de estados contables.
- Usa los ejercicios guiados para cargar casos base y estudiar su efecto.
- Descarga los asientos en CSV si quieres guardarlos o reutilizarlos.
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
        "<div class='soft-card'>Selecciona un caso y cárgalo como asiento modelo o úsalo para practicar manualmente.</div>",
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
balance_df, pyg_df, resultado = compute_balance_and_pyg(trial_df)
ratios_df = compute_ratios(balance_df, pyg_df)
cf_df = compute_cash_flow(journal_df)

entries_count = len(st.session_state.journal)
cuadra_global = journal_df["Debe"].sum() == journal_df["Haber"].sum() if not journal_df.empty else True
activo_total = (
    balance_df.loc[balance_df["Tipo"].str.contains("Activo", na=False), "Saldo"].sum()
    if not balance_df.empty
    else 0.0
)
pasivo_pn_total = (
    balance_df.loc[
        balance_df["Tipo"].isin(["Pasivo corriente", "Pasivo no corriente", "Patrimonio neto"]),
        "Saldo",
    ].sum()
    * -1
    if not balance_df.empty
    else 0.0
)

m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("Asientos registrados", str(entries_count), "Libro diario activo")
with m2:
    metric_card("Resultado del ejercicio", amount_fmt(resultado), "Según PyG actual")
with m3:
    metric_card("Activo total", amount_fmt(activo_total), "Balance actual")
with m4:
    metric_card("Balance cuadrado", "Sí" if cuadra_global else "No", amount_fmt(activo_total - pasivo_pn_total))

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "Libro diario",
        "Libro mayor",
        "Balance comprobación",
        "Balance",
        "PyG",
        "Ratios",
        "Flujo efectivo",
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
    st.markdown("### Balance de situación")
    if balance_df.empty:
        st.info("Sin movimientos todavía.")
    else:
        sections = [
            "Activo corriente",
            "Activo no corriente",
            "Activo no corriente (-)",
            "Patrimonio neto",
            "Pasivo no corriente",
            "Pasivo corriente",
        ]
        for sec in sections:
            sec_df = balance_df[balance_df["Tipo"] == sec].copy()
            if not sec_df.empty:
                st.markdown(f"#### {sec}")
                show_df = sec_df.copy()
                show_df["Saldo"] = show_df["Saldo"].map(amount_fmt)
                st.dataframe(show_df[["Cuenta", "Saldo"]], use_container_width=True, hide_index=True)
        st.caption(
            f"Activo total: {amount_fmt(activo_total)} | Patrimonio neto + Pasivo: {amount_fmt(pasivo_pn_total)}"
        )

with tab5:
    st.markdown("### Cuenta de pérdidas y ganancias")
    pyg_show = pyg_df.copy()
    pyg_show["Importe"] = pyg_show["Importe"].map(amount_fmt)
    st.dataframe(pyg_show, use_container_width=True, hide_index=True)
    st.caption(
        "Los ingresos se generan a partir de cuentas de tipo ingreso y los gastos a partir de cuentas de tipo gasto."
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
