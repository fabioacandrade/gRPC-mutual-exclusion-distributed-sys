# Network Load Balancer - Ant Colony Optimization

O projeto consiste em desenvolver uma simulação simples do algoritmo de colônia de formigas (Ant Colony Optimization) aplicado ao problema de balanceamento de carga em redes de computadores.

## Descrição

Este projeto implementa um balanceador de carga de rede usando o algoritmo de Otimização por Colônia de Formigas (ACO - Ant Colony Optimization). O algoritmo é inspirado no comportamento cooperativo das formigas para encontrar caminhos ótimos e distribui requisições de forma eficiente entre diferentes servidores, reduzindo gargalos e equilibrando a carga.

## Características

- **Algoritmo ACO**: Implementação completa do algoritmo de colônia de formigas para balanceamento de carga
- **Distribuição Inteligente**: Distribui requisições considerando capacidade e carga atual dos servidores
- **Otimização de Feromônios**: Usa feromônios virtuais para convergir para soluções ótimas
- **Visualização em Tempo Real**: Exibe o status de cada servidor com barras de progresso
- **Comparação de Desempenho**: Compara ACO com atribuição aleatória de requisições

## Estrutura do Projeto

```
.
├── server.py          # Representação de servidores
├── request.py         # Representação de requisições
├── ant_colony.py      # Implementação do algoritmo ACO
├── load_balancer.py   # Classe principal do balanceador de carga
├── main.py            # Script de simulação e demonstração
├── examples.py        # Exemplos de uso diversos
└── requirements.txt   # Dependências do projeto
```

## Como Funciona

### Algoritmo de Colônia de Formigas (ACO)

1. **Inicialização**: Cria formigas artificiais e inicializa feromônios em todos os caminhos (requisição → servidor)
2. **Construção de Soluções**: Cada formiga constrói uma solução completa, selecionando servidores para cada requisição baseado em:
   - **Feromônios** (α): Experiência acumulada de soluções anteriores
   - **Heurística** (β): Atratividade baseada na carga atual do servidor
3. **Avaliação**: Calcula o custo de cada solução (desvio padrão de carga + penalidade por sobrecarga)
4. **Atualização de Feromônios**:
   - **Evaporação**: Reduz feromônios existentes
   - **Depósito**: Melhores soluções depositam mais feromônios
5. **Iteração**: Repete o processo por N iterações, convergindo para uma solução ótima

## Instalação

```bash
git clone https://github.com/fabioacandrade/network-load-balancer-ant-colony.git
cd network-load-balancer-ant-colony
```

Não há dependências externas necessárias. O projeto usa apenas a biblioteca padrão do Python.

## Uso

### Executar a Simulação Principal

```bash
python3 main.py
```

Isso executará:
1. Uma simulação completa com 5 servidores e 50 requisições
2. Uma comparação entre ACO e atribuição aleatória

### Executar Exemplos Diversos

```bash
python3 examples.py
```

Isso demonstrará:
1. Uso básico com poucos servidores e requisições
2. Cenário de carga pesada
3. Ajuste de parâmetros e seus efeitos
4. Servidores com capacidades diferentes

### Uso Programático

```python
from load_balancer import LoadBalancer
from request import Request

# Criar balanceador de carga
lb = LoadBalancer(
    num_servers=5,
    server_capacity=100.0,
    num_ants=20,
    num_iterations=100
)

# Gerar requisições
requests = [Request(i, load=5.0) for i in range(50)]

# Balancear carga
stats = lb.balance_load(requests)

# Exibir status
lb.print_status()
```

## Parâmetros Configuráveis

### LoadBalancer

- `num_servers`: Número de servidores na rede (padrão: 5)
- `server_capacity`: Capacidade de cada servidor (padrão: 100.0)
- `num_ants`: Número de formigas na colônia (padrão: 10)
- `num_iterations`: Número de iterações do ACO (padrão: 50)
- `alpha`: Importância dos feromônios (padrão: 1.0)
- `beta`: Importância da heurística (padrão: 2.0)
- `evaporation_rate`: Taxa de evaporação de feromônios (padrão: 0.5)

## Exemplo de Saída

```
============================================================
LOAD BALANCER STATUS
============================================================
Server 0: 50.04/100.00 (50.0%) [████████████████████░░░░░░░░░░░░░░░░░░░░] 9 requests
Server 1: 50.15/100.00 (50.1%) [████████████████████░░░░░░░░░░░░░░░░░░░░] 10 requests
Server 2: 52.02/100.00 (52.0%) [████████████████████░░░░░░░░░░░░░░░░░░░░] 10 requests
Server 3: 49.63/100.00 (49.6%) [███████████████████░░░░░░░░░░░░░░░░░░░░░] 12 requests
Server 4: 50.97/100.00 (51.0%) [████████████████████░░░░░░░░░░░░░░░░░░░░] 9 requests
============================================================

3. Improvement with ACO:
   Std Dev Reduction: 95.9%
   Max Load Reduction: 35.4%
```

## Resultados

O algoritmo ACO demonstra melhorias significativas em relação à atribuição aleatória:

- **Redução de Desvio Padrão**: ~95% (distribuição mais equilibrada)
- **Redução de Carga Máxima**: ~35% (evita sobrecarga de servidores)
- **Convergência**: Encontra soluções próximas ao ótimo em poucas iterações

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Autor

Fabio Andrade

## Referências

- Dorigo, M., & Stützle, T. (2004). Ant Colony Optimization. MIT Press.
- Colorni, A., Dorigo, M., & Maniezzo, V. (1991). Distributed Optimization by Ant Colonies.
