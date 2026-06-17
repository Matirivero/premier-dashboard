import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN Y CSS
st.set_page_config(page_title="Dashboard Premier League", layout="wide")

st.markdown("""
    <style>
    /* Ocultar elementos nativos y marcas de agua de Streamlit */
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stHeader"] {visibility: hidden !important;}
    [data-testid="stDeployButton"] {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .viewerBadge_container {display: none !important;}
    .viewerBadge_link {display: none !important;}
    
    /* Aprovechamiento máximo del lienzo */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 98%; }
    
    .titulo-dashboard { text-align: center; font-size: 2.2rem; font-weight: bold; color: var(--text-color); margin-bottom: 1.5rem; }
    
    .kpi-card { background-color: var(--secondary-background-color); border-radius: 10px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: space-between; height: 100%; }
    .kpi-info { display: flex; flex-direction: column; }
    .kpi-title { font-size: 0.95rem; font-weight: 600; margin-bottom: 5px; color: var(--text-color); opacity: 0.8; }
    .kpi-value { font-size: 2rem; font-weight: bold; color: var(--text-color); line-height: 1.2; }
    .kpi-logo { height: 60px; width: auto; object-fit: contain; }
    
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { font-size: 1.2rem !important; font-weight: 600 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE REGLAS NARRATIVAS
DICT_NARRATIVO = {
    '2024/2025': {
        'campeon': {'equipo': 'Liverpool FC', 'logo': 'https://a.espncdn.com/i/teamlogos/soccer/500/364.png'},
        'fracaso': {'equipo': 'Manchester United', 'logo': 'https://a.espncdn.com/i/teamlogos/soccer/500/360.png'},
        'sorpresa': {'equipo': 'Nottingham Forest', 'logo': 'https://a.espncdn.com/i/teamlogos/soccer/500/393.png'},
        'contexto': ['Manchester City', 'Arsenal FC', 'Chelsea FC']
    },
    '2023/2024': {
        'campeon': {'equipo': 'Manchester City', 'logo': 'https://a.espncdn.com/i/teamlogos/soccer/500/382.png'},
        'fracaso': {'equipo': 'Chelsea FC', 'logo': 'https://a.espncdn.com/i/teamlogos/soccer/500/363.png'},
        'sorpresa': {'equipo': 'Aston Villa', 'logo': 'https://a.espncdn.com/i/teamlogos/soccer/500/362.png'},
        'contexto': ['Arsenal FC', 'Liverpool FC', 'Manchester United']
    },
    '2022/2023': {
        'campeon': {'equipo': 'Manchester City', 'logo': 'https://a.espncdn.com/i/teamlogos/soccer/500/382.png'},
        'fracaso': {'equipo': 'Chelsea FC', 'logo': 'https://a.espncdn.com/i/teamlogos/soccer/500/363.png'},
        'sorpresa': {'equipo': 'Newcastle United', 'logo': 'https://a.espncdn.com/i/teamlogos/soccer/500/361.png'},
        'contexto': ['Arsenal FC', 'Manchester United', 'Brighton & Hove Albion']
    }
}

# 3. CARGA DE DATOS MULTIDIMENSIONAL
@st.cache_data
def cargar_datos():
    df = pd.read_csv("premier_data.csv")
    df['valor_millones_eur'] = pd.to_numeric(df['valor_millones_eur'], errors='coerce')
    df['puntos'] = pd.to_numeric(df['puntos'], errors='coerce')
    df['costo_por_punto'] = (df['valor_millones_eur'] / df['puntos']).round(2)

    def asignar_color_dinamico(row):
        temp = row['temporada']
        equipo = row['squad']
        if temp not in DICT_NARRATIVO: return '#8c8c8c'
        roles = DICT_NARRATIVO[temp]
        if equipo == roles['campeon']['equipo']: return '#2A9D8F'
        elif equipo == roles['fracaso']['equipo']: return '#E63946'
        elif equipo == roles['sorpresa']['equipo']: return '#0077B6'
        elif equipo in roles['contexto']: return '#8c8c8c'
        else: return '#e0e0e0'

    df['color_punto'] = df.apply(asignar_color_dinamico, axis=1)
    return df

df_base = cargar_datos()

# TÍTULO SUPERIOR CENTRADO
st.markdown("<div class='titulo-dashboard'>Análisis táctico de eficiencia financiera: Premier League</div>", unsafe_allow_html=True)
st.write("---")

# 4. LA ARQUITECTURA MAESTRA: División 25% / 75%
col_panel, col_principal = st.columns([1, 3.5], gap="large")

with col_panel:
    st.markdown("<h3 style='margin-top:0; color: var(--text-color);'>🎛️ Parámetros</h3>", unsafe_allow_html=True)
    st.write("---") 
    
    st.write("📅 **Seleccionar Temporada**")
    opciones_temporada = sorted(df_base['temporada'].dropna().unique(), reverse=True)
    temporada_seleccionada = st.selectbox("", opciones_temporada, label_visibility="collapsed")
    
    st.write("")
    st.write("")
    
    df_anio_actual = df_base[df_base['temporada'] == temporada_seleccionada]
    min_val = float(df_anio_actual['valor_millones_eur'].min()) if not df_anio_actual.empty else 0.0
    max_val = float(df_anio_actual['valor_millones_eur'].max()) if not df_anio_actual.empty else 1500.0
    
    st.markdown("💰 **Inversión en Plantel (€M)**")
    rango_presupuesto = st.slider("", min_value=min_val, max_value=max_val, value=(min_val, max_val), step=10.0, label_visibility="collapsed")
    
    st.write("---")
    st.info("💡 **Tip:** Ajuste los filtros para evaluar la eficiencia histórica por segmentos.")

df_filtrado = df_base[
    (df_base['temporada'] == temporada_seleccionada) &
    (df_base['valor_millones_eur'] >= rango_presupuesto[0]) &
    (df_base['valor_millones_eur'] <= rango_presupuesto[1])
]

with col_principal:
    
    def generar_kpi_html(rol_key, titulo_base, color_hex):
        if temporada_seleccionada not in DICT_NARRATIVO: return ""
        config_rol = DICT_NARRATIVO[temporada_seleccionada][rol_key]
        equipo = config_rol['equipo']
        logo_url = config_rol['logo']
        
        match = df_anio_actual[df_anio_actual['squad'] == equipo]
        if not match.empty:
            pts = f"{int(match['puntos'].values[0])} Pts"
            pres = f"€{int(match['valor_millones_eur'].values[0])}M"
        else:
            pts, pres = "N/A", "N/A"
            
        return f'''
        <div class="kpi-card" style="border-top: 4px solid {color_hex};">
            <div class="kpi-info">
                <span class="kpi-title">{titulo_base}: <b>{equipo}</b></span>
                <span class="kpi-value">{pts}</span>
                <span style="color: {color_hex}; font-weight: bold;">{pres} Inversión</span>
            </div>
            <img class="kpi-logo" src="{logo_url}">
        </div>'''

    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(generar_kpi_html('campeon', '🏆 Referencia', '#2A9D8F'), unsafe_allow_html=True)
    with col2: st.markdown(generar_kpi_html('fracaso', '📉 Fracaso', '#E63946'), unsafe_allow_html=True)
    with col3: st.markdown(generar_kpi_html('sorpresa', '📈 Alta Eficiencia', '#0077B6'), unsafe_allow_html=True)

    st.write("")

    tab1, tab2 = st.tabs(["📊 Análisis Exploratorio: Inversión vs Rendimiento", "💸 Ranking Definitivo: Costo por Punto"])

    ALTO_GRAFICO = 720  
    ALTO_IFRAME   = ALTO_GRAFICO + 80

    with tab1:
        if df_filtrado.empty:
            st.warning("No hay clubes en este rango.")
        else:
            fig_scatter = go.Figure()
            fig_scatter.add_trace(go.Scatter(
                x=df_filtrado['valor_millones_eur'], y=df_filtrado['puntos'], mode='markers',
                marker=dict(color=df_filtrado['color_punto'], size=16, line=dict(width=1, color='white')),
                text=df_filtrado['squad'], customdata=df_filtrado['costo_por_punto'],
                hovertemplate="<b>%{text}</b><br>Inversión: €%{x}M<br>Puntos: %{y}<br>Costo por Punto: €%{customdata}M<extra></extra>"
            ))

            equipos_narrativa = []
            if temporada_seleccionada in DICT_NARRATIVO:
                roles = DICT_NARRATIVO[temporada_seleccionada]
                equipos_narrativa = [roles['campeon']['equipo'], roles['fracaso']['equipo'], roles['sorpresa']['equipo']] + roles['contexto']

            for i, row in df_filtrado.iterrows():
                if row['squad'] in equipos_narrativa:
                    fig_scatter.add_annotation(
                        x=row['valor_millones_eur'], y=row['puntos'], text=f"<b>{row['squad']}</b>",
                        showarrow=False, yshift=16, font=dict(size=13, color=row['color_punto'])
                    )

            fig_scatter.update_layout(
                title=dict(text="<b>El triunfo de los clubes inteligentes:</b> el dinero no siempre consigue el éxito", font=dict(size=18), y=0.95),
                plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
                xaxis=dict(title=dict(text='<b>Valor total del plantel</b> (millones de euros)', font=dict(size=14)), showgrid=False, zeroline=False, dtick=50),
                yaxis=dict(title=dict(text='<b>Puntos obtenidos</b>', font=dict(size=14)), showgrid=True, gridcolor='#f0f0f0', zeroline=False, range=[0, 100], dtick=10),
                showlegend=False, height=ALTO_GRAFICO, margin=dict(t=80, b=80, l=80, r=30) 
            )
            html_scatter = fig_scatter.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
            components.html(f'<div style="background-color: #ffffff; border-radius: 12px; overflow: hidden; padding: 10px;">{html_scatter}</div>', height=ALTO_IFRAME, scrolling=False)

    with tab2:
        if df_filtrado.empty:
            st.warning("No hay clubes en este rango.")
        else:
            df_barras = df_filtrado.sort_values(by='costo_por_punto', ascending=False)
            max_x = df_barras['costo_por_punto'].max() * 1.25 if not df_barras.empty else 1

            fig_barras = go.Figure()
            fig_barras.add_trace(go.Bar(
                y=df_barras['squad'], x=df_barras['costo_por_punto'], orientation='h',
                marker_color=df_barras['color_punto'], showlegend=False,
                hovertemplate="<b>%{y}</b><br>Costo por Punto: €%{x} Millones<extra></extra>"
            ))

            textos_formateados = ["€" + str(val) + "M" for val in df_barras['costo_por_punto']]
            fig_barras.add_trace(go.Scatter(
                x=df_barras['costo_por_punto'], y=df_barras['squad'], mode='text',
                text=textos_formateados, textposition='middle right',
                textfont=dict(size=13, color='#333333'), hoverinfo='skip', showlegend=False
            ))

            fig_barras.update_layout(
                title=dict(text="<b>El precio de la ineficiencia:</b> costo económico por punto", font=dict(size=18), y=0.97),
                plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
                xaxis=dict(range=[0, max_x], title='', showticklabels=False, showgrid=False, zeroline=False), 
                yaxis=dict(title='', showgrid=False, tickfont=dict(size=13, color='#333333')),
                height=ALTO_GRAFICO, margin=dict(t=80, b=40, l=190, r=60)
            )
            html_barras = fig_barras.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
            components.html(f'<div style="background-color: #ffffff; border-radius: 12px; overflow: hidden; padding: 10px;">{html_barras}</div>', height=ALTO_IFRAME, scrolling=False)

    # El pie de página ahora vive DENTRO de la columna derecha, alineado bajo los gráficos.
    st.write("")
    st.caption("📌 **Fuente de datos:** FBref / Transfermarkt. Nota: Los clubes en gris representan la media general de la Premier League como contexto visual.")
