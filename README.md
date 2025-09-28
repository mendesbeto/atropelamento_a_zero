# Projeto: Do Dado à Pontuação
[Visualizar o projeto](https://atropelamento-a-zero.streamlit.app/)

Um pequeno projeto sobre a transformação de ideias em estrutura lógica, com o objetivo de calcular a redução de velocidade de um motorista ao receber um alerta e traduzir isso em uma **"pontuação de salva-vidas"**.

Para resolver este desafio, o projeto foi dividido em 5 etapas principais:

1.  **Definir** claramente o problema e as métricas.
2.  **Identificar** os dados necessários.
3.  **Calcular** a mudança de comportamento (a redução de velocidade).
4.  **Modelar** a tradução de velocidade em risco (o passo-chave).
5.  **Gerar** a pontuação de salva-vidas com base na redução de risco.

---

### Etapa 1: Definição do Problema e das Hipóteses (O "O Quê?")

Antes de qualquer cálculo, é preciso definir o que medir e por quê.

-   **Objetivo:** Quantificar o impacto positivo de um alerta de risco na mudança de comportamento do motorista e comunicar esse impacto de forma clara e motivadora.
-   **Hipótese Principal:** *"Motoristas que recebem um alerta de proximidade de 'km de risco' reduzem sua velocidade média dentro da zona de risco em comparação com sua velocidade antes da zona de risco."*
-   **Métrica de Sucesso Primária:** A magnitude da redução da velocidade (`ΔV`).
-   **Métrica de Sucesso Secundária:** Adoção e engajamento do usuário com a "pontuação de salva-vidas".

---

### Etapa 2: Coleta e Entendimento dos Dados (O "Com O Quê?")

> A pergunta fundamental: "Que dados são precisos para resolver esse desafio?".

São necessários dados de telemetria, que podem vir de um aplicativo de celular ou de um dispositivo no carro. Para cada viagem, precisaríamos de:

-   **ID do Veículo/Usuário:** Para analisar o comportamento individual.
-   **Timestamp:** Com precisão de segundos.
-   **Coordenadas GPS:** Para saber onde o carro está.
-   **Velocidade Instantânea:** A leitura de velocidade a cada poucos segundos.
-   **Dados do Alerta:** `ID_do_Alerta`, `Timestamp_do_Alerta`, `Localização_do_Alerta`.
-   **Dados da Zona de Risco:** Um mapa (polígono ou linha georreferenciada) definindo onde começa e termina cada "km de risco".

---

### Etapa 3: Engenharia de Features e Cálculo da Redução de Velocidade (A "Matemática")

Nesta fase, os dados brutos são transformados em métricas.

1.  **Definir as Zonas de Medição:**
    -   **Zona de Controle (Antes):** Um trecho antes do motorista entrar na zona de risco (ex: 500 metros antes).
    -   **Zona de Risco (Dentro):** O trecho do próprio "km de risco".

2.  **Calcular as Velocidades Médias:**
    -   `V_antes`: Velocidade média na Zona de Controle.
    -   `V_dentro`: Velocidade média na Zona de Risco.

3.  **Calcular a Redução (`ΔV`):**
    -   **Simples:** `ΔV = V_antes - V_dentro`
    -   **Percentual:** `ΔV% = ((V_antes - V_dentro) / V_antes) * 100`

> **Ponto de discussão:** E se houver trânsito ou paradas não relacionadas? Uma sugestão é excluir viagens onde a velocidade na zona de controle já é muito baixa (ex: < 30 km/h).

---

### Etapa 4: A "Ponte" - Da Velocidade à Probabilidade de Acidente

Esta é a parte mais criativa e crucial: como transformar `ΔV` em "vidas salvas"? A chave é usar uma **função de risco**.

-   **Conceito:** O risco de um acidente não aumenta linearmente com a velocidade, mas sim **exponencialmente**. Reduzir de 110 km/h para 90 km/h tem um impacto muito maior do que reduzir de 50 km/h para 30 km/h.
-   **Proposta:** Utilizar uma função baseada em estudos que relacione velocidade à probabilidade de um atropelamento ser fatal, `P_fatal(V)`.
-   **Exemplo de Modelo:** Como a energia cinética é `E = 1/2 * m * v²`, o risco pode ser modelado como proporcional ao quadrado da velocidade:
    ```
    Risco(V) = k * V²
    ```
    (Onde 'k' é uma constante de calibração).

---

### Etapa 5: O Cálculo da "Pontuação de Salvavidas"

Finalmente, unimos todos os cálculos para gerar a pontuação.

1.  **Calcular o Risco Evitado:**
    -   `R_antes = Risco(V_antes)`
    -   `R_dentro = Risco(V_dentro)`
    -   `ΔRisco = R_antes - R_dentro`

2.  **Converter em Pontuação:**
    -   **Normalização:** O `ΔRisco` pode ser normalizado em uma escala (ex: 0 a 100).
    -   **Gamificação:** Criar uma pontuação cumulativa onde o motorista acumula "Pontos de Salva-vidas".

> **Exemplo de Comunicação:** "Nesta viagem, ao reduzir a velocidade, você diminuiu o risco de um acidente fatal em 75%. Você ganhou **+50 Pontos de Salva-vidas**!"

---

### Desafios do Projeto

> "A qualidade dos dados de GPS, a latência na entrega dos alertas e, principalmente, validar a função que relaciona velocidade a risco. Seriam necessários dados históricos de acidentes para calibrar o modelo."
[Visualizar o projeto](https://atropelamento-a-zero.streamlit.app/)