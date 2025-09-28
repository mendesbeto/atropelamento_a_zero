import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

from database import generate_mock_data

MODEL_PATH = "risk_model.pkl"

def ground_truth_risk_function(df):
    """
    Cria uma variável alvo (target) simulada para o risco de acidente.
    Esta é a nossa "verdade fundamental" para o treinamento.
    O risco é maior para velocidades altas, à noite e com tempo ruim.
    """
    # Normaliza a velocidade para uma escala de 0 a 1
    speed_normalized = df['speed_kmh'] / 150 # Assumindo 150 km/h como velocidade máxima
    
    # Fatores de risco
    risk_score = speed_normalized ** 2 # Risco base da velocidade
    risk_score[df['hora_do_dia'] == 'noite'] *= 1.5
    risk_score[df['hora_do_dia'] == 'crepusculo'] *= 1.2
    risk_score[df['clima'] == 'chuva'] *= 1.4
    risk_score[df['clima'] == 'neblina'] *= 1.8

    # Converte o score de risco em uma probabilidade (0 a 1) usando uma função sigmoide
    probability = 1 / (1 + np.exp(-risk_score * 5 + 2)) # Ajuste da curva sigmoide
    return (probability > 0.5).astype(int) # Retorna 1 se a prob > 0.5 (acidente), senão 0

def train_and_save_model():
    """
    Treina um modelo LightGBM com os dados simulados e o salva em um arquivo.
    """
    print("Gerando dados para treinamento...")
    df = generate_mock_data(num_trips=1000) # Gera uma grande base de dados
    
    # Cria a variável alvo
    df['acidente'] = ground_truth_risk_function(df)
    
    # Prepara os dados para o modelo
    features = ['speed_kmh', 'hora_do_dia', 'clima']
    target = 'acidente'
    
    # Codifica variáveis categóricas
    encoders = {}
    for col in ['hora_do_dia', 'clima']:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le
        
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Treinando o modelo LightGBM...")
    model = lgb.LGBMClassifier(random_state=42)
    model.fit(X_train, y_train)
    
    print(f"Acurácia do modelo: {model.score(X_test, y_test):.2f}")
    
    # Salva o modelo e os encoders
    joblib.dump({'model': model, 'encoders': encoders}, MODEL_PATH)
    print(f"Modelo salvo em {MODEL_PATH}")
    
    return {'model': model, 'encoders': encoders}

def load_model():
    """
    Carrega o modelo do arquivo. Se não existir, treina um novo.
    """
    if not os.path.exists(MODEL_PATH):
        print("Modelo não encontrado. Treinando um novo...")
        return train_and_save_model()
    else:
        print("Carregando modelo existente...")
        return joblib.load(MODEL_PATH)

def predict_risk(model_bundle, speed, hora_do_dia, clima):
    """
    Usa o modelo carregado para prever a probabilidade de risco.
    """
    model = model_bundle['model']
    encoders = model_bundle['encoders']
    
    # Cria um DataFrame com os dados de entrada
    data = pd.DataFrame([{
        'speed_kmh': speed,
        'hora_do_dia': hora_do_dia,
        'clima': clima
    }])
    
    # Codifica as variáveis categóricas com os encoders salvos
    for col, encoder in encoders.items():
        # Usa uma classe desconhecida se o valor não foi visto no treino
        data[col] = data[col].apply(lambda x: x if x in encoder.classes_ else 'unknown')
        encoder_classes = encoder.classes_.tolist()
        if 'unknown' not in encoder_classes:
            encoder.classes_ = np.append(encoder.classes_, 'unknown')
        data[col] = encoder.transform(data[col])

    # Retorna a probabilidade da classe 1 (acidente)
    return model.predict_proba(data)[:, 1][0]

if __name__ == "__main__":
    # Treina e salva o modelo se o arquivo for executado diretamente
    train_and_save_model()
