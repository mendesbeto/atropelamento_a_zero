import streamlit as st
import numpy as np
from database import generate_mock_data
from model import load_model, predict_risk

# --- Configuração da Página ---
st.set_page_config(
    page_title="Atropelamento a Zero",
    page_icon="🚗",
    layout="wide"
)

# --- Carregar Modelo de ML (Cacheado) ---
@st.cache_resource
def load_ml_model():
    """Carrega o modelo de machine learning uma vez e o mantém em cache."""
    return load_model()

model_bundle = load_ml_model()

# --- Título e Introdução ---
st.title("Projeto: Atropelamento a Zero")
st.markdown("""
Este painel analisa o comportamento de motoristas ao se aproximarem de zonas de risco de atropelamento de animais, 
calculando uma **'Pontuação de Salva-vidas'** baseada na redução de velocidade e no risco previsto por um modelo de Machine Learning.
""")

# --- Barra Lateral (Sidebar) ---
with st.sidebar:
    st.header("Análise de Viagens")
    
    # Gera e cacheia os dados simulados
    @st.cache_data
    def get_data():
        return generate_mock_data(num_trips=50)
    
    df = get_data()
    
    # Seletor de viagem
    trip_ids = df["trip_id"].unique()
    selected_trip = st.selectbox("Selecione uma Viagem:", trip_ids)
    
    st.info(f"Você está analisando a viagem **{selected_trip}**.")

# Filtra o dataframe para a viagem selecionada
trip_data = df[df["trip_id"] == selected_trip].copy()

# --- Análise da Viagem Selecionada ---
st.header(f"🗺️ Detalhes da Viagem: {selected_trip}")

with st.container(border=True):
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📊 Dados da Viagem")
        st.dataframe(
            trip_data.style.background_gradient(cmap='Reds', subset=['speed_kmh'])
            .apply(lambda x: ['background-color: #FFADAD' if v == 'Risk' else 'background-color: #B5EAD7' for v in x], subset=['zone']),
            hide_index=True, 
            use_container_width=True
        )

    with col2:
        st.subheader("📉 Variação de Velocidade")
        st.line_chart(
            trip_data, 
            x="timestamp", 
            y="speed_kmh", 
            color="zone",
            x_label="Tempo",
            y_label="Velocidade (km/h)"
        )

# --- Cálculo da Pontuação ---
st.header("🏆 Pontuação de Salva-vidas")

with st.container(border=True):
    # 1. Calcular Velocidades Médias e obter contexto
    control_data = trip_data[trip_data["zone"] == "Control"]
    v_antes = control_data["speed_kmh"].mean() if not control_data.empty else 0

    risk_data = trip_data[trip_data["zone"] == "Risk"]
    v_dentro = risk_data["speed_kmh"].mean() if not risk_data.empty else 0

    # Pega o contexto da viagem
    context_hora = trip_data['hora_do_dia'].iloc[0] if not trip_data.empty else "Dia"
    context_clima = trip_data['clima'].iloc[0] if not trip_data.empty else "Limpo"

    # 2. Prever o Risco com o Modelo de ML
    r_antes_prob = predict_risk(model_bundle, v_antes, context_hora, context_clima)
    r_dentro_prob = predict_risk(model_bundle, v_dentro, context_hora, context_clima)

    # 3. Calcular Redução de Risco
    delta_risco = r_antes_prob - r_dentro_prob
    percent_reduction = (delta_risco / r_antes_prob) * 100 if r_antes_prob > 0 else 0
    
    # 4. Calcular Pontuação Final
    pontuacao = max(0, percent_reduction * 10) # Garante que a pontuação não seja negativa

    # 5. Exibir Resultados
    score_col, metrics_col = st.columns([1, 2])

    with score_col:
        st.subheader("Sua Pontuação")
        st.markdown(f"<h1 style='text-align: center; color: #2A9D8F;'>{pontuacao:.0f}</h1>", unsafe_allow_html=True)
        st.progress(int(pontuacao / 1000) if pontuacao > 0 else 0) # Ajuste da escala da barra
        
        if delta_risco > 0:
            st.success("**Ótimo!** Você reduziu a velocidade e o risco.")
        else:
            st.warning("**Atenção!** A velocidade na zona de risco não foi reduzida.")

    with metrics_col:
        st.subheader("Métricas de Risco")
        calc_col1, calc_col2, calc_col3 = st.columns(3)
        with calc_col1:
            st.metric("Risco Previsto (Antes)", f"{r_antes_prob:.2%}")
        with calc_col2:
            st.metric("Risco Previsto (Dentro)", f"{r_dentro_prob:.2%}", f"{delta_risco*100:+.1f} pts")
        with calc_col3:
            st.metric("Redução de Risco", f"{percent_reduction:.1f}%")

# --- Dados Brutos ---
with st.expander("🔬 Ver todos os dados brutos gerados"):
    st.dataframe(
        df.style.background_gradient(cmap='Reds', subset=['speed_kmh'])
        .apply(lambda x: ['background-color: #FFADAD' if v == 'Risk' else 'background-color: #B5EAD7' for v in x], subset=['zone']),
        hide_index=True
    )
