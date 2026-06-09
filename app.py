import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN Y CSS (Adaptativo)
st.set_page_config(page_title="Dashboard Premier League", layout="wide")

st.markdown("""
    <style>
    [data-testid="stToolbar"] {visibility: hidden !important;}
    footer {visibility: hidden !important;}

    /* FIX 1: padding-top aumentado de 1rem → 3rem para que el título no quede
       tapado por el banner del navegador en modo pantalla completa */
    .block-container { padding-top: 3rem; padding-bottom: 2rem; max-width: 95%; }

    .titulo-dashboard { text-align: center; font-size: 2.2rem; font-weight: bold; color: var(--text-color); margin-bottom: 0.5rem; }

    .kpi-card { background-color: var(--secondary-background-color); border-radius: 10px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: space-between; height: 100%; }
    .kpi-info { display: flex; flex-direction: column; }
    .kpi-title { font-size: 0.95rem; font-weight: 600; margin-bottom: 5px; color: var(--text-color); opacity: 0.8; }
    .kpi-value { font-size: 2rem; font-weight: bold; color: var(--text-color); line-height: 1.2; }
    .kpi-logo { height: 60px; width: auto; object-fit: contain; }

    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { font-size: 1.2rem !important; font-weight: 600 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS Y COLORES
@st.cache_data
def cargar_datos():
    df = pd.read_csv("premier_data.csv")
    df['valor_millones_eur'] = pd.to_numeric(df['valor_millones_eur'], errors='coerce')
    df['puntos'] = pd.to_numeric(df['puntos'], errors='coerce')
    df['costo_por_punto'] = (df['valor_millones_eur'] / df['puntos']).round(2)

    def asignar_color(squad):
        if squad == 'Liverpool FC': return '#2A9D8F'
        elif squad == 'Manchester United': return '#E63946'
        elif squad in ['Nottingham Forest', 'Fulham FC']: return '#0077B6'
        elif squad in ['Manchester City', 'Arsenal FC']: return '#8c8c8c'
        else: return '#e0e0e0'

    df['color_punto'] = df['squad'].apply(asignar_color)
    return df

df_base = cargar_datos()

# 3. INTERFAZ Y FILTRO CENTRAL
st.markdown("<div class='titulo-dashboard'>Análisis Táctico de Eficiencia Financiera: Premier League</div>", unsafe_allow_html=True)
st.write("---")

st.markdown("<h4 style='text-align:center; color: var(--text-color); opacity: 0.9;'>🎛️ Filtrar Equipos por Rango de Presupuesto (€ Millones)</h4>", unsafe_allow_html=True)
col_vacia1, col_slider, col_vacia2 = st.columns([1, 2, 1])
with col_slider:
    min_val = float(df_base['valor_millones_eur'].min())
    max_val = float(df_base['valor_millones_eur'].max())
    rango_presupuesto = st.slider(
        "Presupuesto", min_value=min_val, max_value=max_val, value=(min_val, max_val), step=10.0, label_visibility="collapsed"
    )

df_filtrado = df_base[
    (df_base['valor_millones_eur'] >= rango_presupuesto[0]) &
    (df_base['valor_millones_eur'] <= rango_presupuesto[1])
]
st.write("---")

# 4. TARJETAS KPI
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="kpi-card" style="border-top: 4px solid #2A9D8F;"><div class="kpi-info"><span class="kpi-title">🏆 Referencia: Campeón Eficiente</span><span class="kpi-value">84 Pts</span><span style="color: #2A9D8F; font-weight: bold;">€951M Presupuesto</span></div><img class="kpi-logo" src="https://a.espncdn.com/i/teamlogos/soccer/500/364.png"></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="kpi-card" style="border-top: 4px solid #E63946;"><div class="kpi-info"><span class="kpi-title">📉 Referencia: Fracaso Financiero</span><span class="kpi-value">42 Pts</span><span style="color: #E63946; font-weight: bold;">€825M Presupuesto</span></div><img class="kpi-logo" src="https://a.espncdn.com/i/teamlogos/soccer/500/360.png"></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="kpi-card" style="border-top: 4px solid #0077B6;"><div class="kpi-info"><span class="kpi-title">📈 Referencia: Alta Eficiencia</span><span class="kpi-value">65 Pts</span><span style="color: #0077B6; font-weight: bold;">€481M Presupuesto</span></div><img class="kpi-logo" src="https://a.espncdn.com/i/teamlogos/soccer/500/393.png"></div>', unsafe_allow_html=True)

st.write("")

# 5. PESTAÑAS
tab1, tab2 = st.tabs(["📊 Análisis Exploratorio: Relación Inversión vs Rendimiento", "💸 Ranking Definitivo: Costo Económico por Punto"])

# Constante compartida: ambos gráficos usan exactamente la misma altura.
# Cambiar este único valor afecta a los dos de forma simétrica.
ALTO_GRAFICO = 600
ALTO_IFRAME  = ALTO_GRAFICO + 100   # buffer para bordes, padding y scroll del iframe

with tab1:
    if df_filtrado.empty:
        st.warning("No hay clubes en este rango.")
    else:
        fig_scatter = go.Figure()
        fig_scatter.add_trace(go.Scatter(
            x=df_filtrado['valor_millones_eur'], y=df_filtrado['puntos'], mode='markers',
            marker=dict(color=df_filtrado['color_punto'], size=16, line=dict(width=1, color='white')),
            text=df_filtrado['squad'], customdata=df_filtrado['costo_por_punto'],
            hovertemplate="<b>%{text}</b><br>Presupuesto: €%{x}M<br>Puntos: %{y}<br>Costo por Punto: €%{customdata}M<extra></extra>"
        ))

        equipos_a_etiquetar = ['Liverpool FC', 'Manchester United', 'Nottingham Forest', 'Fulham FC', 'Manchester City', 'Arsenal FC']
        for i, row in df_filtrado.iterrows():
            if row['squad'] in equipos_a_etiquetar:
                fig_scatter.add_annotation(
                    x=row['valor_millones_eur'], y=row['puntos'], text=f"<b>{row['squad']}</b>",
                    showarrow=False, yshift=16, font=dict(size=13, color=row['color_punto'])
                )

        fig_scatter.update_layout(
            title=dict(text="<b>El triunfo de los clubes inteligentes:</b> el dinero no siempre consigue el éxito", font=dict(size=20), y=0.95),
            plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
            xaxis=dict(title=dict(text='<b>Valor Total del Plantel</b> (Millones de Euros)', font=dict(size=15)), showgrid=False, zeroline=False),
            yaxis=dict(title=dict(text='<b>Puntos Obtenidos</b> (Fin de Temporada)', font=dict(size=15)), showgrid=True, gridcolor='#f0f0f0', zeroline=False),
            showlegend=False,
            height=ALTO_GRAFICO,
            margin=dict(t=80, b=90, l=90, r=40)
        )
        html_scatter = fig_scatter.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
        html_wrapper = f'<div style="background-color: #ffffff; border-radius: 12px; overflow: hidden; padding: 10px;">{html_scatter}</div>'
        components.html(html_wrapper, height=ALTO_IFRAME, scrolling=False)

with tab2:
    if df_filtrado.empty:
        st.warning("No hay clubes en este rango.")
    else:
        df_barras = df_filtrado.sort_values(by='costo_por_punto', ascending=True)

        # Espacio a la derecha para que las etiquetas de valor no queden cortadas
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
            title=dict(text="<b>El precio de la ineficiencia:</b> ¿Cuántos millones costó cada punto obtenido?", font=dict(size=19), y=0.97),
            plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
            xaxis=dict(range=[0, max_x], title='', showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(title='', showgrid=False, tickfont=dict(size=13, color='#333333')),
            height=ALTO_GRAFICO,
            margin=dict(t=80, b=40, l=220, r=70)
        )
        html_barras = fig_barras.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
        html_wrapper2 = f'<div style="background-color: #ffffff; border-radius: 12px; overflow: hidden; padding: 10px;">{html_barras}</div>'
        components.html(html_wrapper2, height=ALTO_IFRAME, scrolling=False)