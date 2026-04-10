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

ESTADO_COLORS = {"activo": VERDE, "en_riesgo": "#f39c12", "abandonado": ROJO}

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
    "Alimento Congelado": "Clientes enfocados en alimentos congelados. Compra concentrada en horario nocturno.",
    "Consumo en Local": "Priorizan la experiencia en la heladería: cucuruchos, batidos, sundaes. Perfil joven.",
    "Familia/Niños": "Familias que combinan productos infantiles con surtidos para adultos.",
    "Individual": "Consumidores de impulso con tickets pequeños: bombones, palitos, frutas bañadas.",
    "Social/Eventos": "Orientados a reuniones, celebraciones y consumo grupal. Tickets de mayor valor.",
    "Stock/Abastecimiento": "Compran pote y granel de forma planificada para consumo en el hogar.",
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

check_login()


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
    (b_data["estado"].isin(["en_riesgo", "abandonado"])).mean() * 100, 1
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


# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📍 Mapa de Clientes",
    "💓 Estado de Socios",
    "🎯 Ocasión de Consumo",
])


# ═══════════════════════════════════════════════
# TAB 1 — MAPA DE CLIENTES
# ═══════════════════════════════════════════════
with tab1:
    st.markdown("#### ¿Donde estan mis Socios?")

    col_filtros, col_map = st.columns([1, 3])

    with col_filtros:
        # Segment filter
        all_segments = sorted(b_data["Ocasion de consumo"].dropna().unique().tolist())
        seg_filter = st.multiselect(
            "Filtrar por segmento",
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

        # Apply filters
        filtered = b_data[
            (b_data["Ocasion de consumo"].isin(seg_filter))
            & (b_data["Kilos"] >= kg_range[0])
            & (b_data["Kilos"] <= kg_range[1])
        ]

        st.markdown(f"**{len(filtered)}** clientes filtrados")

        mostrar_leyenda_ocasiones(filtered)

    with col_map:
        def seg_to_rgb(seg_name):
            hex_c = SEGMENT_COLORS.get(seg_name, "#95a5a6")
            hex_c = hex_c.lstrip("#")
            return [int(hex_c[i:i+2], 16) for i in (0, 2, 4)]

        # Filter valid coordinates: not NaN and not (0,0)
        map_data = filtered.dropna(subset=["Latitud", "Longitud"]).copy()
        map_data["Kilos"] = map_data["Kilos"].round(2)
        map_data = map_data[(map_data["Latitud"] != 0) & (map_data["Longitud"] != 0)]

        # Risk categories and colors
        def get_riesgo(p):
            if p < 0.3:
                return "Alto"
            elif p <= 0.7:
                return "Medio"
            else:
                return "Bajo"

        RIESGO_COLORS = {"Alto": [231, 76, 60], "Medio": [241, 196, 15], "Bajo": [46, 204, 113]}

        map_data["riesgo_abandono"] = map_data["p_alive"].apply(get_riesgo)
        map_data["color_r"] = map_data["riesgo_abandono"].apply(lambda r: RIESGO_COLORS[r][0])
        map_data["color_g"] = map_data["riesgo_abandono"].apply(lambda r: RIESGO_COLORS[r][1])
        map_data["color_b"] = map_data["riesgo_abandono"].apply(lambda r: RIESGO_COLORS[r][2])

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
                        get_radius=60,
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
                            "<b style='color:#ec7e04;'>Cliente {DNI}</b><br>"
                            "📦 Kg comprados por año: <b>{Kilos}</b><br>"
                            "🔄 Compras por año: <b>{Cantidad de compras}</b><br>"
                            "📅 Última compra: hace <b>{Dias desde ultima compra}</b> días<br>"
                            "🎯 Ocasión de consumo: <b>{Ocasion de consumo}</b><br>"
                            "⚠️ Riesgo de abandono: <b>{riesgo_abandono}</b>"
                            "</div>"
                        ),
                        "style": {
                            "backgroundColor": "#0b1d42", "color": "#e8ecf4",
                            "border": "1px solid rgba(255,255,255,0.1)", "borderRadius": "8px",
                        },
                    }

            map_style_option = st.radio(
                        "Estilo de mapa",
                        ["Oscuro", "Calles", "Satélite", "Satélite + Calles"],
                        horizontal=True, key="map_style",
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


# ═══════════════════════════════════════════════
# TAB 2 — ESTADO DE SOCIOS (SUPERVIVENCIA)
# ═══════════════════════════════════════════════
with tab2:
    st.markdown("#### Estado de mis Socios")

    if n_total == 0:
        st.info("No hay socios para este punto de venta.")
    else:
        col_chart, col_detail = st.columns([1, 1])

        with col_chart:
            # Stacked bar — estado distribution
            estado_counts = b_data["estado"].value_counts().reindex(
                ["activo", "en_riesgo", "abandonado"], fill_value=0
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
                title=dict(text="Distribución por Estado", font=dict(size=14)),
            )
            st.plotly_chart(fig_estado, use_container_width=True)

            
            # # Survival curve (simulated from data)
            # st.markdown("##### Curva de Supervivencia Agregada")
            # days = np.arange(0, 365, 5)
            # median_recencia = b_data["recencia"].median()
            # lambda_param = 0.005 if median_recencia < 30 else 0.008
            # surv_curve = np.exp(-lambda_param * days) * 100

            # fig_surv = go.Figure()
            # fig_surv.add_trace(go.Scatter(
            #     x=days, y=surv_curve,
            #     mode="lines", fill="tozeroy",
            #     line=dict(color=CELESTE, width=2),
            #     fillcolor="rgba(73,195,251,0.1)",
            #     name="P(activo)",
            # ))
            # fig_surv.add_hline(y=50, line_dash="dash", line_color=NARANJA, annotation_text="Mediana")
            # fig_surv.update_layout(
            #     **PLOTLY_LAYOUT,
            #     height=280,
            #     xaxis_title="Días desde última compra",
            #     yaxis_title="% Prob. Activo",
            #     title=dict(text="Función de Supervivencia", font=dict(size=14)),
            # )
            # st.plotly_chart(fig_surv, use_container_width=True)

            # # P(alive) distribution histogram
            # st.markdown("##### Distribución de P(alive)")
            # fig_hist = go.Figure()
            # fig_hist.add_trace(go.Histogram(
            #     x=b_data["p_alive"],
            #     nbinsx=30,
            #     marker_color=NARANJA,
            #     opacity=0.8,
            # ))
            # fig_hist.add_vline(x=0.6, line_dash="dash", line_color=VERDE, annotation_text="Umbral activo")
            # fig_hist.add_vline(x=0.3, line_dash="dash", line_color=ROJO, annotation_text="Umbral abandono")
            # fig_hist.update_layout(
            #     **PLOTLY_LAYOUT,
            #     height=250,
            #     xaxis_title="P(alive)",
            #     yaxis_title="Cantidad de clientes",
            # )
            # st.plotly_chart(fig_hist, use_container_width=True)
            

        with col_detail:
            st.markdown("##### Clientes con Mayor Riesgo de Abandono")
            top_churn = (
                b_data.sort_values("p_alive", ascending=True)
                .head(20)
                [[ "DNI",  "Dias desde ultima compra",
                  "frecuencia", "estado", "Ocasion de consumo"]]
                .copy()
            )
            top_churn.rename(columns={
                "DNI": "Cliente",
                "Dias desde ultima compra": "Días s/ compra",
                "frecuencia": "Frecuencia",
                "estado": "Estado",
                "Ocasion de consumo": "Ocasión",
            }, inplace=True)
            top_churn["Días s/ compra"] = top_churn["Días s/ compra"].apply(lambda x: f"{x:.0f}")

            st.dataframe(
                top_churn,
                hide_index=True,
                use_container_width=True,
                height=600,
            )

            # Summary metrics
            st.markdown("##### Resumen del Punto de Venta")
            col_s1, col_s2= st.columns(2)
            col_s1.metric("Promedio riesgo de abandono", f"{b_data['p_alive'].mean():.1%}")
            col_s2.metric("Dias desde ultima compra promedio", f"{b_data['recencia'].mean():.0f} días")
            #col_s3.metric("Compras Esperadas", f"{b_data['expected_purchases'].mean():.1f}")




# ═══════════════════════════════════════════════
# TAB 3 — SEGMENTACIÓN POR OCASIÓN DE CONSUMO
# ═══════════════════════════════════════════════
with tab3:
    st.markdown("#### Segmentación por Ocasión de Consumo")

    if n_total == 0:
        st.info("No hay socios para este punto de venta.")
    else:
        col_donut, col_table = st.columns([1, 1])

        with col_donut:
            seg_dist = b_data["Ocasion de consumo"].value_counts()
            colors_ordered = [SEGMENT_COLORS.get(s, GRIS) for s in seg_dist.index]

            fig_donut = go.Figure(data=[go.Pie(
                labels=seg_dist.index,
                values=seg_dist.values,
                hole=0.55,
                marker=dict(colors=colors_ordered, line=dict(color=AZUL_OSCURO, width=2)),
                textinfo="percent+label",
                textfont=dict(size=12),
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

            # Bar chart: avg kilos per segment
            st.markdown("##### Kg Promedio por Segmento")
            seg_kg = b_data.groupby("Ocasion de consumo")["Kilos"].mean().sort_values(ascending=True)
            fig_kg = go.Figure(data=[go.Bar(
                y=seg_kg.index,
                x=seg_kg.values.round(1),
                orientation="h",
                marker_color=[SEGMENT_COLORS.get(s, GRIS) for s in seg_kg.index],
                text=seg_kg.values.round(1),
                textposition="outside",
                textfont=dict(size=12, color="#e8ecf4"),
            )])
            fig_kg.update_layout(
                **PLOTLY_LAYOUT,
                height=250,
                xaxis_title="Kg promedio",
                title=dict(text="Consumo Promedio por Ocasión", font=dict(size=14)),
            )
            st.plotly_chart(fig_kg, use_container_width=True)

        with col_table:
            st.markdown("##### Métricas por Segmento")
            seg_summary = (
                b_data.groupby("Ocasion de consumo")
                .agg(
                    Clientes=("CustomerId", "count"),
                    Kg_Promedio=("Kilos", "mean"),
                    Compras_Promedio=("Cantidad de compras", "mean"),
                    Valor_Promedio=("monetary_value", "mean"),
                    P_alive_Promedio=("p_alive", "mean"),
                )
                .sort_values("Clientes", ascending=False)
                .reset_index()
                .rename(columns={"Ocasion de consumo": "Segmento"})
            )
            seg_summary["Kg_Promedio"] = seg_summary["Kg_Promedio"].round(2)
            seg_summary["Compras_Promedio"] = seg_summary["Compras_Promedio"].round(1)
            seg_summary["Valor_Promedio"] = seg_summary["Valor_Promedio"].apply(lambda x: f"${x:,.0f}")
            seg_summary["P_alive_Promedio"] = seg_summary["P_alive_Promedio"].apply(lambda x: f"{x:.1%}")

            st.dataframe(seg_summary[['Segmento','Clientes','Kg_Promedio','Compras_Promedio','Valor_Promedio','P_alive_Promedio']], hide_index=True, use_container_width=True)

            # Segment descriptions
            st.markdown("##### Descripción de Segmentos")
            descriptions = {
                "Consumo Familiar": "Compras de pote 1kg+ orientadas al consumo hogareño, frecuencia regular.",
                "Antojo Individual": "Cucuruchos, palitos y vasitos. Compras impulsivas de bajo ticket.",
                "Celebracion": "Postres, tortas heladas y pedidos para eventos o reuniones especiales.",
                "Merienda Social": "Compras en grupo, cuartos variados. Contexto social/amigos.",
                "Regalo/Ocasional": "Compras esporádicas en fechas especiales o como regalo.",
            }
            for seg_name in seg_dist.index:
                desc = descriptions.get(seg_name, "")
                color = SEGMENT_COLORS.get(seg_name, GRIS)
                cnt = int((b_data["Ocasion de consumo"] == seg_name).sum())
                st.markdown(
                    f"<span style='color:{color};font-size:14px;'>●</span> "
                    f"**{seg_name}** ({cnt}) — {desc}",
                    unsafe_allow_html=True,
                )

            # Estado breakdown per segment
            st.markdown("##### Estado por Segmento")
            cross = pd.crosstab(
                b_data["Ocasion de consumo"],
                b_data["estado"],
                normalize="index",
            ).reindex(columns=["activo", "en_riesgo", "abandonado"], fill_value=0) * 100

            fig_cross = go.Figure()
            for estado in ["activo", "en_riesgo", "abandonado"]:
                if estado in cross.columns:
                    fig_cross.add_trace(go.Bar(
                        y=cross.index,
                        x=cross[estado].round(1),
                        name=estado.replace("_", " ").title(),
                        orientation="h",
                        marker_color=ESTADO_COLORS.get(estado, GRIS),
                        text=cross[estado].apply(lambda x: f"{x:.0f}%"),
                        textposition="inside",
                        textfont=dict(size=11, color="white"),
                    ))
            fig_cross.update_layout(
                **PLOTLY_LAYOUT,
                barmode="stack",
                height=250,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                xaxis_title="% de clientes",
                title=dict(text="Estado de Socios por Ocasión", font=dict(size=14)),
            )
            st.plotly_chart(fig_cross, use_container_width=True)