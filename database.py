
import pandas as pd
import numpy as np

# --- Dados Simulados ---

# Definição da Zona de Risco (ex: um polígono ou um trecho de estrada)
# Para simplificar, vamos definir como um intervalo de coordenadas.
RISK_ZONE = {
    "id": "ZR-001",
    "description": "KM 123 da BR-101, área de travessia de capivaras",
    "start_lat": -23.55,
    "end_lat": -23.56
}

def generate_mock_data(num_trips=50):
    """
    Gera dados simulados mais realistas para treinar um modelo de ML.
    Inclui fatores como hora do dia e clima.
    """
    all_trips_data = []
    
    for i in range(1, num_trips + 1):
        # Fatores contextuais
        hora_do_dia = np.random.choice(['dia', 'noite', 'crepusculo'], p=[0.6, 0.3, 0.1])
        clima = np.random.choice(['limpo', 'chuva', 'neblina'], p=[0.7, 0.2, 0.1])
        
        # A velocidade inicial é influenciada pelo contexto
        if hora_do_dia == 'noite' or clima == 'chuva':
            speed_before = np.random.uniform(70, 100)
        else:
            speed_before = np.random.uniform(90, 120)

        # A probabilidade de reagir ao alerta também muda
        react_prob = 0.7
        if hora_do_dia == 'noite': react_prob += 0.1 # Mais cauteloso à noite
        if clima == 'chuva': react_prob -= 0.1 # Menos visibilidade, talvez menos reação
        
        reacted_to_alert = np.random.choice([True, False], p=[min(react_prob, 1.0), 1 - min(react_prob, 1.0)])
        
        if reacted_to_alert:
            speed_inside = speed_before * np.random.uniform(0.6, 0.85)
        else:
            speed_inside = speed_before * np.random.uniform(0.98, 1.05)
            
        # Geração dos pontos de dados
        for zone, speed, num_points in [("Control", speed_before, 5), ("Risk", speed_inside, 10)]:
            for j in range(num_points):
                all_trips_data.append({
                    "trip_id": f"trip_{i}",
                    "user_id": f"user_{i}",
                    "timestamp": pd.to_datetime("2025-09-26 10:00:00") + pd.Timedelta(seconds=(j*2 if zone == 'Control' else 10 + j*2)),
                    "latitude": RISK_ZONE["start_lat"] + (0.0001 * j if zone == 'Control' else -0.0001 * j),
                    "longitude": -46.63,
                    "speed_kmh": np.random.normal(speed, 5),
                    "zone": zone,
                    "hora_do_dia": hora_do_dia,
                    "clima": clima
                })

    df = pd.DataFrame(all_trips_data)
    df['speed_kmh'] = df['speed_kmh'].clip(lower=0)
    
    return df

if __name__ == "__main__":
    # Para testar o módulo, você pode executar `python database.py`
    mock_data = generate_mock_data(100)
    print("Dados de Amostra Gerados (Enriquecidos):")
    print(mock_data.head())
    print("\n...\n")
    print(mock_data.tail())
    print(f"\nTotal de registros: {len(mock_data)}")
    print(f"Viagens únicas: {mock_data['trip_id'].unique()}")
    print(f"\nValores de 'hora_do_dia': {mock_data['hora_do_dia'].unique()}")
    print(f"Valores de 'clima': {mock_data['clima'].unique()}")
