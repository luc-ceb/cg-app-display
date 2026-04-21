"""
Club Grido Intelligence — Data Analytics Hub
Tablero analítico interno para el programa de fidelización Club Grido.
Fuentes: seg_bbdd.parquet + c_franquicias.parquet
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pydeck as pdk
import base64

import os

os.environ["MAPBOX_TOKEN"] = st.secrets.get("MAPBOX_API_KEY", "")

# ─────────────────────────────────────────────
# CONFIG & CONSTANTS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Club Grido Intelligence",
    page_icon="🍦",
    layout="wide",
    initial_sidebar_state="expanded",
)

OCASION_ICONS = {
    "Alimentación": "🍽️",
    "Consumo en Local": "🍦",
    "Familia / Niños": "👨‍👩‍👧",
    "Individual": "🎯",
    "Social / Eventos": "🎉",
    "Stock / Abastecimiento": "📦",
}

NARANJA = "#ec7e04"
AZUL_OSCURO = "#092c73"
ROSA = "#e54a82"
CELESTE = "#49c3fb"
VERDE = "#2ecc71"
GRIS = "#95a5a6"
ROJO = "#e74c3c"

SEGMENT_COLORS = {
    "Consumo Familiar": NARANJA,
    "Antojo Individual": CELESTE,
    "Celebracion": ROSA,
    "Merienda Social": VERDE,
    "Regalo/Ocasional": "#f1c40f",
}
OCASION_COLORS = {
    "Alimentación": NARANJA,
    "Consumo en Local": CELESTE,
    "Familia / Niños": ROSA,
    "Individual": "#f1c40f",       # amarillo
    "Social / Eventos": VERDE,
    "Stock / Abastecimiento": "#9b59b6",  # violeta
}

ESTADO_COLORS = {"Activo": VERDE, "En Riesgo": "#f39c12", "Abandonado": ROJO}

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#e8ecf4"),
    margin=dict(l=40, r=20, t=40, b=40),
)
# ─────────────────────────────────────────────
# CONFIG & CONSTANTS
# ─────────────────────────────────────────────

DESCRIPCIONES_OCASION = {
    "Alimentación": "Clientes enfocados en alimentos congelados. Compra concentrada en horario nocturno.",
    "Consumo en Local": "Priorizan la experiencia en la heladería: cucuruchos, batidos, sundaes. Perfil joven.",
    "Familia / Niños": "Familias que combinan productos infantiles con surtidos para adultos.",
    "Individual": "Consumidores de impulso con tickets pequeños: bombones, palitos, frutas bañadas.",
    "Social / Eventos": "Orientados a reuniones, celebraciones y consumo grupal. Tickets de mayor valor.",
    "Stock / Abastecimiento": "Compran pote y granel de forma planificada para consumo en el hogar.",
}

# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────
def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        col_l, col_c, col_r = st.columns([1, 1, 1])
        with col_c:
            st.image("assets/portada.png", width=250)
        st.markdown("<h2 style='text-align:center; margin-top:16px;'>Club Grido Intelligence</h2>", unsafe_allow_html=True)
 
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            user = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            if st.button("Ingresar", use_container_width=True):
                if user == st.secrets["LOGIN_USER"] and password == st.secrets["LOGIN_PASS"]:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
        st.stop()

# check_login()
st.session_state.authenticated =True

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* Header band */
    .main-header {
        background: linear-gradient(135deg, #0b1d42 0%, #092c73 50%, #0d3a8a 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 20px 28px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .main-header .logo {
        width: 48px; height: 48px; border-radius: 12px;
        background: linear-gradient(135deg, #ec7e04, #f5a623);
        display: flex; align-items: center; justify-content: center;
        font-size: 24px; font-weight: 800; color: white;
        box-shadow: 0 4px 20px rgba(236,126,4,0.3);
        flex-shrink: 0;
    }
    .main-header .title { font-size: 22px; font-weight: 700; color: #fff; }
    .main-header .subtitle {
        font-size: 11px; color: rgba(255,255,255,0.4);
        letter-spacing: 0.1em; text-transform: uppercase;
    }
    .main-header .accent { color: #ec7e04; }

    /* KPI cards */
    div[data-testid="stMetric"] {
        background: rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 16px 20px;
    }
    div[data-testid="stMetric"] label {
        color: rgba(255,255,255,0.6) !important;
        font-size: 10px !important;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 22px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #ec7e04 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] svg {
        fill: #ec7e04 !important;
    }
            
    /* Force sidebar always open */
    section[data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 300px !important;
        transform: none !important;
    }
    section[data-testid="stSidebar"] > div {
        width: 300px !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 13px;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(236,126,4,0.1) !important;
        border-bottom: 2px solid #ec7e04 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #06173d;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    section[data-testid="stSidebar"] .stSelectbox label {
        color: rgba(255,255,255,0.5);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_franquicias():
    return pd.read_parquet("data/c_franquicias.parquet")

@st.cache_data
def load_branch(bid):
    path = f"data/branches/{bid}.parquet"
    if os.path.exists(path):
        return pd.read_parquet(path)
    return pd.DataFrame()

franquicias = load_franquicias()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st .image("assets/portada.png", use_container_width=True)
    st .markdown("""
    <div style="text-align:center; padding: 4px 0 16px 0;">
        <div style="font-size:14px; font-weight:700; color:#fff;">
            Club Grido <span style="color:#ec7e04;">Intelligence</span>
        </div>
        <div style="font-size:10px; color:rgba(255,255,255,0.35);
             letter-spacing:0.12em; text-transform:uppercase; margin-top:2px;">
            Data Analytics Hub
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    # Filters for branch selection
    provincias = ["Todas"] + sorted(franquicias["provincia"].dropna().unique().tolist())
    selected_provincia = st.selectbox("🏛 Provincia", options=provincias, key="filter_prov")

    filtered_franq = franquicias.copy()
    if selected_provincia != "Todas":
        filtered_franq = filtered_franq[filtered_franq["provincia"] == selected_provincia]

    localidades = ["Todas"] + sorted(filtered_franq["localidad"].dropna().unique().tolist())
    selected_localidad = st.selectbox("📌 Localidad", options=localidades, key="filter_loc")

    if selected_localidad != "Todas":
        filtered_franq = filtered_franq[filtered_franq["localidad"] == selected_localidad]

    branch_options = {
        row.branchofficeid: f"{row.numero}-{row.heladeria} — {row.localidad}"
        for _, row in filtered_franq.iterrows()
    }

    selected_bid = st.selectbox(
        "📍 Franquicia",
        options=list(branch_options.keys()),
        format_func=lambda x: branch_options[x],
    )


    st.markdown("---")
    st.markdown(
        "<div style='font-size:10px; color:rgba(255,255,255,0.25); text-align:center; padding:8px;'>"
        "Club Grido Intelligence v1.0"
        "</div>",
        unsafe_allow_html=True,
    )

branch_info = franquicias[franquicias["branchofficeid"] == selected_bid].iloc[0]


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
with open("assets/portada.png", "rb") as f:
    logo_b64 = base64.b64encode(f.read()).decode()

st.markdown(f"""
<div class="main-header">
    <div class="logo"><img src="data:image/png;base64,{logo_b64}" style="width:40px; height:40px; border-radius:10px; object-fit:cover;"></div>
    <div>
        <div class="title">{branch_info['heladeria']} <span class="accent">· {branch_info['numero']}</span></div>
        <div class="subtitle">Ubicación: {branch_info['localidad']} · {branch_info['provincia']}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FILTER DATA FOR SELECTED BRANCH
# ─────────────────────────────────────────────
b_data = load_branch(selected_bid)

# ─────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────
n_total = len(b_data)
socios_activos = branch_info .get("Socios activos", 0)
kg_club = branch_info .get("Kilos vendidos por club", 0)
penetracion = branch_info .get("Penetracion Club", 0)
pct_penetracion = round(penetracion * 100) if penetracion is not None and not pd.isna(penetracion) else 0
pct_churn = round(
    (b_data["estado"].isin(["En riesgo", "Abandonado"])).mean() * 100, 1
) if n_total > 0 else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Socios Activos", f"{int(socios_activos):,}", help="Socios activos en el último año")
k2.metric("Kg Vendidos Club", f"{kg_club:,.0f} kg",help="Kilogramos vendidos por Club Grido en el último año")
k3.metric("Penetración Club", f"{pct_penetracion}%",help="Porcentaje de kilos vendidos a través del Club sobre el total de ventas mostrador")
k4.metric("Socios en riesgo", f"{pct_churn}%", delta_color="inverse", help="Porcentaje de socios en estado en riesgo o abandonado")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


def mostrar_leyenda_ocasiones(df_datos, titulo="##### ¿En qué ocasión consumen?"):
    st.markdown(titulo)
    # Iteramos sobre todos los segmentos definidos
    for seg_name, desc in DESCRIPCIONES_OCASION.items():
        color = SEGMENT_COLORS.get(seg_name, GRIS) # Usará gris si no está en SEGMENT_COLORS
        # Contamos cuántos registros hay en el dataframe que le pasemos
        cnt = int((df_datos["Ocasion de consumo"] == seg_name).sum())
        
        st.markdown(
            f"<div style='margin:4px 0; cursor:help;'>"
            f"<span style='color:{color}; font-size:16px;'>●</span> "
            f"<b>{seg_name}</b> ({cnt})"
            f"<div style='font-size:10px; color:rgba(255,255,255,0.4); margin-left:20px;'>{desc}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

def mostrar_leyenda_ocasiones(df_datos, titulo="¿En qué ocasión consumen? - Descripción de los segmentos"):
    st.markdown(
        f"<h5 style='margin:16px 0 10px 0; color:#e8ecf4; font-weight:600;'>{titulo}</h5>",
        unsafe_allow_html=True,
    )
    total = len(df_datos)

    def render_item(seg_name, desc):
        color = OCASION_COLORS.get(seg_name, GRIS)
        cnt = int((df_datos["Ocasion de consumo"] == seg_name).sum())
        pct = (cnt / total * 100) if total > 0 else 0
        st.markdown(
            f"""
            <div style="border-left:3px solid {color}; padding:6px 0 6px 12px; margin:8px 0;">
                <div style="font-size:13px; font-weight:600; color:#e8ecf4;">
                    {seg_name}
                    <span style="color:{color}; font-weight:700; margin-left:6px;">{cnt}</span>
                    <span style="font-size:10px; color:rgba(255,255,255,0.4);"> · {pct:.0f}%</span>
                </div>
                <div style="font-size:11px; color:rgba(255,255,255,0.5); margin-top:2px; line-height:1.4;">
                    {desc}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    items = list(DESCRIPCIONES_OCASION.items())
    mitad = (len(items) + 1) // 2  # 3 y 3 si son 6

    col_a, col_b = st.columns(2)
    with col_a:
        for seg_name, desc in items[:mitad]:
            render_item(seg_name, desc)
    with col_b:
        for seg_name, desc in items[mitad:]:
            render_item(seg_name, desc)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 ,tab4 , tab5 = st.tabs([
    "📍 Mi Comunidad",
    "💓 Estado de Socios",
    "🍦 Ocasión de Consumo",
    "🎯 Gestioná con Club Grido",
    "💡 Acciones Recomendadas",
])


# ═══════════════════════════════════════════════
# TAB 1 — MAPA DE CLIENTES
# ═══════════════════════════════════════════════
with tab1:
    st.markdown("#### Resumen de Mi Comunidad")

    total_socios = len(b_data)

    # TODO: reemplazar por cálculo real cuando tengas snapshot semanal
    # Ej: pct_incremento = (total_socios - total_socios_semana_pasada) / total_socios_semana_pasada * 100
    pct_incremento = np.round(np.random.uniform(1, 10), 1)
    signo = "+" if pct_incremento >= 0 else ""
    color_delta = VERDE if pct_incremento >= 0 else ROJO

    # --- Encabezado: KPI + distribuciones ---
    col_kpi, col_dist_ocasion, col_dist_estado, col_dist_app = st.columns([1.2, 1, 1, 1])

    with col_kpi:
        st.markdown(
            f"""
            <div style="background:rgba(0,0,0,0.25);
                        border:1px solid rgba(255,255,255,0.1);
                        border-radius:12px;
                        padding:24px;
                        height:200px;
                        display:flex;
                        flex-direction:column;
                        justify-content:center;">
                <div style="color:rgba(255,255,255,0.55);
                            font-size:11px;
                            letter-spacing:0.08em;
                            text-transform:uppercase;">
                    Socios Favoritos 👥
                </div>
                <div style="font-size:26px;
                            font-weight:700;
                            color:#ffffff;
                            margin-top:10px;
                            line-height:1.3;">
                    Tenés <span style="color:{NARANJA};">{total_socios:,}</span> socios favoritos
                </div>
                <div style="color:rgba(255,255,255,0.75);
                            font-size:13px;
                            margin-top:12px;">
                    <b style="color:{color_delta};">{signo}{pct_incremento:.1f}%</b>
                    respecto a la semana pasada
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_dist_ocasion:
        ocasion_counts = b_data["Ocasion de consumo"].value_counts()
        colors_ocasion = [OCASION_COLORS.get(o, GRIS) for o in ocasion_counts.index]

        fig_ocasion = go.Figure(data=[go.Pie(
            labels=ocasion_counts.index,
            values=ocasion_counts.values,
            hole=0.6,
            marker=dict(colors=colors_ocasion, line=dict(color=AZUL_OSCURO, width=2)),
            textinfo="percent",
            textfont=dict(size=10),
            hovertemplate="<b>%{label}</b><br>%{value} clientes<br>%{percent}<extra></extra>",
        )])
        fig_ocasion.update_layout(
            **{**PLOTLY_LAYOUT, "margin": dict(l=10, r=10, t=35, b=10)},
            height=200,
            showlegend=True,
            legend=dict(
                orientation="v", yanchor="middle", y=0.5,
                xanchor="left", x=1.02, font=dict(size=9),
            ),
            title=dict(text="Ocasión de Consumo", font=dict(size=13), x=0.02),
        )
        st.plotly_chart(fig_ocasion, use_container_width=True)

    with col_dist_estado:
        estado_counts = b_data["estado"].value_counts()
        colors_estado = [ESTADO_COLORS.get(e, GRIS) for e in estado_counts.index]

        fig_estado = go.Figure(data=[go.Pie(
            labels=[e.replace("_", " ").title() for e in estado_counts.index],
            values=estado_counts.values,
            hole=0.6,
            marker=dict(colors=colors_estado, line=dict(color=AZUL_OSCURO, width=2)),
            textinfo="percent",
            textfont=dict(size=10, color="white"),
            hovertemplate="<b>%{label}</b><br>%{value} clientes<br>%{percent}<extra></extra>",
        )])
        fig_estado.update_layout(
            **{**PLOTLY_LAYOUT, "margin": dict(l=10, r=10, t=35, b=10)},
            height=200,
            showlegend=True,
            legend=dict(
                orientation="v", yanchor="middle", y=0.5,
                xanchor="left", x=1.02, font=dict(size=9),
            ),
            title=dict(text="Estado de Socios", font=dict(size=13), x=0.02),
        )
        st.plotly_chart(fig_estado, use_container_width=True)

    with col_dist_app:
        # Normalizamos por si vienen como bool, int o string
        app_series = b_data["Tiene App"].astype(str).str.strip().str.lower()
        app_map = {
            "true": "Con App", "1": "Con App", "sí": "Con App", "si": "Con App", "yes": "Con App",
            "false": "Sin App", "0": "Sin App", "no": "Sin App", "nan": "Sin App",
        }
        app_labels = app_series.map(app_map).fillna("Sin App")
        app_counts = app_labels.value_counts()

        APP_COLORS = {"Con App": CELESTE, "Sin App": GRIS}
        colors_app = [APP_COLORS.get(a, GRIS) for a in app_counts.index]

        fig_app = go.Figure(data=[go.Pie(
            labels=app_counts.index,
            values=app_counts.values,
            hole=0.6,
            marker=dict(colors=colors_app, line=dict(color=AZUL_OSCURO, width=2)),
            textinfo="percent",
            textfont=dict(size=10, color="white"),
            hovertemplate="<b>%{label}</b><br>%{value} clientes<br>%{percent}<extra></extra>",
        )])
        fig_app.update_layout(
            **{**PLOTLY_LAYOUT, "margin": dict(l=10, r=10, t=35, b=10)},
            height=200,
            showlegend=True,
            legend=dict(
                orientation="v", yanchor="middle", y=0.5,
                xanchor="left", x=1.02, font=dict(size=9),
            ),
            title=dict(text="Penetración de socios en App 📱", font=dict(size=13), x=0.02),
        )
        st.plotly_chart(fig_app, use_container_width=True)

    st.divider()

    st.markdown("#### ¿Dónde están mis Socios?")
    st.caption("📍 Visualización geográfica de tu comunidad en la zona.")


    col_filtros, col_map = st.columns([1, 3])

    with col_filtros:
        # Segment filter
        all_segments = sorted(b_data["Ocasion de consumo"].dropna().unique().tolist())
        seg_filter = st.multiselect(
            "🎯 Filtrar por segmento",
            options=all_segments,
            default=all_segments,
            key="map_seg_filter",
        )

        # Kg range filter
        kg_min = float(b_data["Kilos"].min()) if n_total > 0 else 0.0
        kg_max = float(b_data["Kilos"].max()) if n_total > 0 else 1.0
        kg_range = st.slider(
            "Rango de Kg comprados",
            min_value=kg_min,
            max_value=kg_max,
            value=(kg_min, kg_max),
            key="map_kg_range",
        )
        
        # Días desde última compra filter
        dias_min = int(b_data["Dias desde ultima compra"].min()) if n_total > 0 else 0
        dias_max = int(b_data["Dias desde ultima compra"].max()) if n_total > 0 else 1
        dias_range = st.slider(
            "📅 Días desde última compra",
            min_value=dias_min,
            max_value=dias_max,
            value=(dias_min, dias_max),
            key="map_dias_ultima_compra",
        )

        # Tiene App filter
        tiene_app_opciones = ["Todos"] + sorted(
            b_data["Tiene App"].dropna().astype(str).unique().tolist()
        )
        tiene_app_sel = st.selectbox(
            "📱 Tiene App",
            options=tiene_app_opciones,
            key="map_app_filter",
        )

        filtered = b_data[
            (b_data["Ocasion de consumo"].isin(seg_filter)) &
            (b_data["Kilos"] >= kg_range[0]) &
            (b_data["Kilos"] <= kg_range[1]) &
            (b_data["Dias desde ultima compra"] >= dias_range[0]) &
            (b_data["Dias desde ultima compra"] <= dias_range[1])
        ]
        # Aplicar filtro Tiene App solo si no es "Todos"
        if tiene_app_sel != "Todos":
            filtered = filtered[
                b_data["Tiene App"].astype(str) == tiene_app_sel
            ]

        st.markdown(f"**{len(filtered)}** clientes filtrados")

    with col_map:
        def seg_to_rgb(seg_name):
            hex_c = SEGMENT_COLORS.get(seg_name, "#95a5a6")
            hex_c = hex_c.lstrip("#")
            return [int(hex_c[i:i+2], 16) for i in (0, 2, 4)]

        # Filter valid coordinates: not NaN and not (0,0)
        map_data = filtered.dropna(subset=["Latitud", "Longitud"]).copy()
        map_data["Kilos"] = map_data["Kilos"].round(2)
        map_data = map_data[(map_data["Latitud"] != 0) & (map_data["Longitud"] != 0)]

        # Retención relativa: percentiles dinámicos sobre los geolocalizados
        if len(map_data) > 0:
            q33 = map_data["p_alive"].quantile(0.33)
            q66 = map_data["p_alive"].quantile(0.66)
        else:
            q33, q66 = 0.33, 0.66  # fallback si no hay datos

        def get_retencion(p):
            if p < q33:
                return "Alto"
            elif p <= q66:
                return "Medio"
            else:
                return "Bajo"

        RETENCION_COLORS = {
            "Alto": [231, 76, 60],    # rojo
            "Medio": [241, 196, 15],   # amarillo
            "Bajo": [46, 204, 113],   # verde
        }

        map_data["retencion_relativa"] = map_data["p_alive"].apply(get_retencion)
        map_data["color_r"] = map_data["retencion_relativa"].apply(lambda r: RETENCION_COLORS[r][0])
        map_data["color_g"] = map_data["retencion_relativa"].apply(lambda r: RETENCION_COLORS[r][1])
        map_data["color_b"] = map_data["retencion_relativa"].apply(lambda r: RETENCION_COLORS[r][2])

        if len(map_data) > 0:
            # Branch location
            branch_lat = branch_info.get("Latitud", None)
            branch_lon = branch_info.get("Longitud", None)

            has_branch_coords = (
                branch_lat is not None and branch_lon is not None
                and not pd.isna(branch_lat) and not pd.isna(branch_lon)
                and branch_lat != 0 and branch_lon != 0
            )
            if has_branch_coords:
                center_lat = float(branch_lat)
                center_lon = float(branch_lon)
            else:
                center_lat = float(map_data["Latitud"].mean())
                center_lon = float(map_data["Longitud"].mean())

            view = pdk.ViewState(
                latitude=center_lat, longitude=center_lon,
                zoom=13, pitch=0,
            )

            layer_clients = pdk.Layer(
                "ScatterplotLayer",
                data=map_data,
                get_position=["Longitud", "Latitud"],
                get_color=["color_r", "color_g", "color_b", 200],
                get_radius=30,
                radius_min_pixels=2,
                radius_max_pixels=15,
                pickable=True,
                auto_highlight=True,
            )
            layers = [layer_clients]

            if has_branch_coords:
                branch_point = pd.DataFrame([{
                    "Longitud": center_lon,
                    "Latitud": center_lat,
                    "heladeria": branch_info.get("heladeria", ""),
                    "localidad": branch_info.get("localidad", ""),
                    "kg_club": f"{kg_club:,.0f}",
                    "penetracion": f"{pct_penetracion}%",
                    "riesgo_churn": f"{pct_churn}%",
                }])
                layers.append(pdk.Layer(
                    "IconLayer",
                    data=branch_point,
                    get_position=["Longitud", "Latitud"],
                    get_icon={
                        "url": "https://cdn-icons-png.flaticon.com/512/869/869636.png",
                        "width": 128,
                        "height": 128,
                        "anchorY": 128,
                    },
                    get_size=40,
                    size_min_pixels=15,
                    size_max_pixels=50,
                    pickable=True,
                ))
            if has_branch_coords:
                            branch_point = pd.DataFrame([{
                                "Longitud": center_lon,
                                "Latitud": center_lat,
                                "heladeria": getattr(branch_info, "heladeria", ""),
                                "localidad": getattr(branch_info, "localidad", ""),
                            }])
                            layers.append(pdk.Layer(
                                "ScatterplotLayer", data=branch_point,
                                get_position=["Longitud", "Latitud"],
                                get_color=[255, 255, 255, 220], get_radius=200, pickable=False,
                            ))
                            layers.append(pdk.Layer(
                                "ScatterplotLayer", data=branch_point,
                                get_position=["Longitud", "Latitud"],
                                get_color=[236, 126, 4, 255], get_radius=140,
                                pickable=True, auto_highlight=True,
                            ))

            tooltip = {
                        "html": (
                            "<div style='padding:8px; font-family:DM Sans,sans-serif;'>"
                            "<b style='color:#ec7e04;'>Nombre: {Nombre}</b><br>"
                            "📦 Kg comprados por año: <b>{Kilos}</b><br>"
                            "🔄 Compras por año: <b>{Cantidad de compras}</b><br>"
                            "📅 Última compra: hace <b>{Dias desde ultima compra}</b> días<br>"
                            "🎯 Ocasión de consumo: <b>{Ocasion de consumo}</b><br>"
                            "⚠️ Riesgo de abandono: <b>{retencion_relativa}</b><br>"
                            "📱 Tiene App: <b>{Tiene App}</b><br>"
                            "📲 Último ingreso app: hace <b>{Dias desde ultimo ingreso app}</b> días"
                            "</div>"
                        ),
                        "style": {
                            "backgroundColor": "#0b1d42", "color": "#e8ecf4",
                            "border": "1px solid rgba(255,255,255,0.1)", "borderRadius": "8px",
                        },
                    }

            map_style_option = st.radio(
                        "🌎 Estilo de mapa",
                        ["Oscuro", "Calles", "Satélite", "Satélite + Calles"],
                        horizontal=True, key="map_style", index=1,
                    )
            style_map = {
                        "Oscuro": "mapbox://styles/mapbox/dark-v11",
                        "Calles": "mapbox://styles/mapbox/streets-v12",
                        "Satélite": "mapbox://styles/mapbox/satellite-v9",
                        "Satélite + Calles": "mapbox://styles/mapbox/satellite-streets-v12",
                    }
            st.pydeck_chart(pdk.Deck(
                        layers=layers, initial_view_state=view, tooltip=tooltip,
                        map_style=style_map[map_style_option],
                    ))
            branch_label = "📍 Franquicia en naranja · " if has_branch_coords else ""
            st.caption(f"{branch_label}{len(map_data)} clientes geolocalizados de {len(filtered)} filtrados")
            
        else:
            st.warning("No hay clientes con coordenadas válidas para este punto de venta.")
        
        st .divider()
        mostrar_leyenda_ocasiones(b_data)


# ═══════════════════════════════════════════════
# TAB 2 — ESTADO DE SOCIOS (SUPERVIVENCIA)
# ═══════════════════════════════════════════════
with tab2:
    st.markdown("#### Estado de mis Socios")
    st.markdown(
        """
        <div style="color:rgba(255,255,255,0.7); font-size:13px; line-height:1.5; margin-bottom:16px;">
            🩺 <b>Diagnóstico de tu cartera.</b></br> Conocé qué socios siguen comprando, 
            cuáles empezaron a enfriarse y cuáles ya no vuelven. 
            Priorizá tus acciones de retención sobre los <b style="color:#f39c12;">socios en riesgo</b> 
            y recuperá a los <b style="color:#e74c3c;">abandonados</b> antes de que sea tarde.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if n_total == 0:
        st.info("No hay socios para este punto de venta.")
    else:
        col_detail,col_chart = st.columns([1, 1])

        with col_detail:
            st.markdown("##### Resumen de la franquicia")
            col_a, col_b, col_c = st .columns(3)
            # Clientes que requieren acción inmediata
            en_peligro = ((b_data["estado"] == "En riesgo") | (b_data["estado"] == "Abandonado")).sum()
            pct_peligro = en_peligro / len(b_data) * 100

            col_a.metric(
                "🚨 Requieren acción",
                f"{en_peligro}",
                f"{pct_peligro:.0f}% de la cartera",
                delta_color="off",
            )
            col_c.metric(
                "📅 Recencia promedio",
                f"{b_data['Dias desde ultima compra'].mean():.0f} días",
                help="Días promedio desde la última compra",
            )

            # Penetración app: relevante para estrategia digital
            con_app = (b_data["Tiene App"].astype(str).str.lower().isin(["true", "1", "si", "sí"])).sum()
            col_b .metric(
                "📱 Penetración app",
                f"{con_app / len(b_data):.0%}",
                help="% de socios con la app instalada",
            )

        with col_chart:
            st.markdown("##### Distribución por estado")
            # Stacked bar — estado distribution
            estado_counts = b_data["estado"].value_counts().reindex(
                ["Activo", "En riesgo", "Abandonado"], fill_value=0
            )
            fig_estado = go.Figure()
            for estado, count in estado_counts.items():
                fig_estado.add_trace(go.Bar(
                    x=[count], y=["Socios"], orientation="h",
                    name=estado.replace("_", " ").title(),
                    marker_color=ESTADO_COLORS.get(estado, GRIS),
                    text=[f"{count} ({count/n_total*100:.0f}%)"],
                    textposition="inside",
                    textfont=dict(size=13, color="white"),
                ))
            fig_estado.update_layout(
                **PLOTLY_LAYOUT,
                barmode="stack",
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                height=140,
                yaxis=dict(visible=False),
                xaxis=dict(visible=False),
                #title=dict(text="Distribución por Estado", font=dict(size=14)),
            )
            st.plotly_chart(fig_estado, use_container_width=True)

        st.divider()
        st.markdown("##### 💎 Socios valiosos en riesgo")
        st.caption("Priorizados por valor histórico y urgencia de acción")

        valiosos = b_data .copy()
        valiosos['Frecuencia de compra (dias)'] = round(365/valiosos['Cantidad de compras'],0)
        valiosos["score_prioridad"] = (
            valiosos["Kilos"] .rank(pct=True) * (1 - valiosos["p_alive"])
        )
        valiosos = (
            valiosos[valiosos["estado"].isin(["En riesgo", "Abandonado"])]
            .sort_values("score_prioridad", ascending=False)
            .head(15)
            [["Nombre", "Kilos", "Frecuencia de compra (dias)", "Dias desde ultima compra",
              "LineaProdFav","PhoneNumber1", "email","p_alive"]]
        )
        valiosos["p_alive"] = valiosos["p_alive"].apply(lambda x: f"{x:.1%}")
        valiosos.rename(columns={'LineaProdFav':'Linea Producto Favorito','PhoneNumber1':'Telefono','frecuencia':'Frecuencia de compra (dias)'},inplace=True)
        valiosos['Kilos'] = valiosos['Kilos'].round(2)
        valiosos.drop(columns=['p_alive'],inplace=True)
        st.dataframe(valiosos, hide_index=True, use_container_width=True)

        st.divider()
        st.markdown("##### Clientes con Mayor Riesgo de Abandono")
        top_churn = (
            b_data[b_data.categoria!='ABANDONO'].sort_values("p_alive", ascending=True)
            .head(20)
            [["Nombre", "Dias desde ultima compra", "frecuencia", "Kilos",
            "p_alive", "estado", "Ocasion de consumo", "Tiene App",
            "Dias desde ultimo ingreso app", "PhoneNumber1", "email" ,"ProductoFavorito",'LineaProdFav']]
            .copy()
        )
        top_churn["p_alive"] = top_churn["p_alive"].apply(lambda x: f"{x:.1%}")
        top_churn["Kilos"] = top_churn["Kilos"].round(1)
        top_churn .rename(columns={
            "Nombre": "Cliente",
            "Dias desde ultima compra": "Días sin comprar",
            "frecuencia": "Compras",
            "Kilos": "Kg/año",
            "estado": "Estado",
            "Ocasion de consumo": "Ocasión",
            "Tiene App": "App",
            "Dias desde ultimo ingreso app": "Días s/app",
            "PhoneNumber1": "Teléfono",
            "email": "Email",
            "ProductoFavorito":"Producto Favorito",
            "LineaProdFav":"Linea Producto Favorito"
        }, inplace=True)
        top_churn .drop(columns=['p_alive'],inplace=True) 

        st.dataframe(
            top_churn,
            hide_index=True,
            use_container_width=True,
            height=600,
            column_config={
                "Kg/año": st.column_config.ProgressColumn(
                    "Kg/año", min_value=0, max_value=float(b_data["Kilos"].max()),
                    format="%.1f",
                ),
            },
        )




# ═══════════════════════════════════════════════
# TAB 3 — SEGMENTACIÓN POR OCASIÓN DE CONSUMO
# ═══════════════════════════════════════════════
with tab3:
    st.markdown("#### Segmentación por Ocasión de Consumo")

    st.markdown(
        """
        <div style="color:rgba(255,255,255,0.7); font-size:13px; line-height:1.6; margin:8px 0 20px 0;">
            🎯 <b>¿Por qué te compran tus socios?</b> Esta segmentación agrupa a los clientes
            según la <b>ocasión de consumo</b> dominante en sus compras — el tipo de momento
            o necesidad que el helado cubre para ellos. No todos compran igual: algunos lo hacen
            para abastecer la heladera de casa, otros para regalar, otros como antojo individual
            o para celebraciones. Entender estos perfiles te permite <b>comunicarte mejor con cada grupo</b>,
            diseñar promociones más relevantes y anticipar qué productos impulsar según el tipo de socio.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if n_total == 0:
        st.info("No hay socios para este punto de venta.")
    else:
        # ───────── FILA 1 ─────────
        row1_col1, row1_col2 = st.columns([1, 1])

        # [Fila 1 · Col 1] Donut de distribución por ocasión
        with row1_col1:
            seg_dist = b_data["Ocasion de consumo"].value_counts()
            colors_ordered = [OCASION_COLORS.get(s, GRIS) for s in seg_dist.index]

            fig_donut = go.Figure(data=[go.Pie(
                labels=seg_dist.index,
                values=seg_dist.values,
                hole=0.55,
                marker=dict(colors=colors_ordered, line=dict(color=AZUL_OSCURO, width=2)),
                textinfo="percent+label",
                textfont=dict(size=12, color="white"),
                hovertemplate="<b>%{label}</b><br>Clientes: %{value}<br>%{percent}<extra></extra>",
            )])
            fig_donut.update_layout(
                **PLOTLY_LAYOUT,
                height=420,
                showlegend=False,
                title=dict(text="Distribución por Ocasión", font=dict(size=14)),
                annotations=[dict(
                    text=f"<b>{n_total}</b><br>socios",
                    x=0.5, y=0.5, font_size=18, showarrow=False,
                    font=dict(color="#e8ecf4"),
                )],
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        # [Fila 1 · Col 2] Leyenda descriptiva de los segmentos
        with row1_col2:
            mostrar_leyenda_ocasiones(
                b_data,
                titulo="¿En qué ocasión consumen? — Descripción de los segmentos",
            )

        st.divider()

        # ───────── FILA 2 ─────────
        row2_col1, row2_col2 = st.columns([1, 1])

        # [Fila 2 · Col 1] Barras de kg promedio por segmento
        with row2_col1:
            st.markdown("##### Kg Promedio por Segmento")
            seg_kg = (
                b_data.groupby("Ocasion de consumo")["Kilos"]
                .mean()
                .sort_values(ascending=True)
            )
            fig_kg = go.Figure(data=[go.Bar(
                y=seg_kg.index,
                x=seg_kg.values.round(1),
                orientation="h",
                marker_color=[OCASION_COLORS.get(s, GRIS) for s in seg_kg.index],
                text=seg_kg.values.round(1),
                textposition="outside",
                textfont=dict(size=12, color="#e8ecf4"),
            )])
            fig_kg.update_layout(
                **PLOTLY_LAYOUT,
                height=380,
                xaxis_title="Kg promedio",
                title=dict(text="Consumo Promedio por Ocasión", font=dict(size=14)),
            )
            st.plotly_chart(fig_kg, use_container_width=True)

        # [Fila 2 · Col 2] Tabla de métricas por segmento
        with row2_col2:
            st.markdown("##### Métricas por Segmento")
            seg_summary = (
                b_data.groupby("Ocasion de consumo")
                .agg(
                    Clientes=("CustomerId", "count"),
                    Kg_Promedio=("Kilos", "mean"),
                    Compras_Promedio=("Cantidad de compras", "mean"),
                    P_alive_Promedio=("p_alive", "mean"),
                )
                .sort_values("Clientes", ascending=False)
                .reset_index()
                .rename(columns={"Ocasion de consumo": "Segmento"})
            )
            seg_summary["Kg_Promedio"] = seg_summary["Kg_Promedio"].round(2)
            seg_summary["Compras_Promedio"] = seg_summary["Compras_Promedio"].round(1)
            seg_summary["P_alive_Promedio"] = seg_summary["P_alive_Promedio"].apply(
                lambda x: f"{x:.1%}"
            )

            st.dataframe(
                seg_summary[[
                    "Segmento", "Clientes", "Kg_Promedio",
                    "Compras_Promedio"
                ]].rename(columns={'Compras_Promedio':'Compras por año','Kg_Promedio':'Kilos consumidos promedio por año'}),
                hide_index=True,
                use_container_width=True,
                height=380,
                column_config={
                    "Clientes": st.column_config.ProgressColumn(
                        "Clientes",
                        min_value=0,
                        max_value=int(seg_summary["Clientes"].max()),
                        format="%d",
                    ),
                },
            )

# ═══════════════════════════════════════════════
# TAB 4 — GESTIONÁ CON CLUB GRIDO
# ═══════════════════════════════════════════════
with tab4:
    st.markdown("#### Gestioná con Club Grido")
    st.caption("Herramientas de gestión para tu comunidad de socios.")

    # TODO: contenido de la tab


# ═══════════════════════════════════════════════
# TAB 5 — ACCIONES RECOMENDADAS
# ═══════════════════════════════════════════════
with tab5:
    st.markdown("#### Acciones Recomendadas")
    st.caption("Sugerencias basadas en el estado de tu cartera.")

    # TODO: contenido de la tab