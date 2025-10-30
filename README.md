# Sistema de Impressão Distribuído com Algoritmo de Ricart-Agrawala

Sistema distribuído de impressão onde múltiplos clientes coordenam o acesso a um servidor de impressão usando o algoritmo de exclusão mútua de Ricart-Agrawala e relógios lógicos de Lamport.

## Descrição

Este projeto implementa um sistema de impressão distribuído com:

- **Servidor de Impressão "Burro"** (porta 50051): Apenas recebe e processa requisições de impressão
- **Clientes Inteligentes** (portas 50052+): Implementam o algoritmo de Ricart-Agrawala para coordenação e exclusão mútua
- **Comunicação via gRPC**: Protocolo eficiente para comunicação entre processos
- **Relógios Lógicos de Lamport**: Ordenação de eventos em sistema distribuído
- **Execução em Rede**: Processos rodando em terminais diferentes se comunicando pela rede

## Arquitetura

### Servidor de Impressão (Burro)
- Porta: 50051
- Função: Receber, processar e confirmar impressões
- **NÃO** participa da exclusão mútua
- **NÃO** conhece os clientes

### Clientes Inteligentes
- Portas: 50052, 50053, 50054, ...
- Funções:
  - Implementam algoritmo de Ricart-Agrawala
  - Mantêm relógios lógicos de Lamport
  - Coordenam entre si para exclusão mútua
  - Geram requisições automáticas de impressão
  - Atuam como cliente E servidor gRPC

## Estrutura do Projeto

```
.
├── distributed_printing.proto    # Definição do protocolo gRPC
├── distributed_printing_pb2.py   # Código Python gerado (mensagens)
├── distributed_printing_pb2_grpc.py  # Código Python gerado (serviços)
├── lamport_clock.py              # Implementação do relógio de Lamport
├── print_server.py               # Servidor de impressão "burro"
├── client.py                     # Cliente inteligente com Ricart-Agrawala
├── test_system.py                # Script de teste automatizado
├── run_system.sh                 # Script auxiliar para execução
└── requirements.txt              # Dependências do projeto
```

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/fabioacandrade/network-load-balancer-ant-colony.git
cd network-load-balancer-ant-colony
```

2. Instale as dependências:
```bash
pip3 install -r requirements.txt
```

3. Gere o código gRPC (se necessário):
```bash
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. distributed_printing.proto
```

## Como Executar

### Opção 1: Manualmente em Terminais Separados

Abra 4 terminais e execute:

**Terminal 1 - Servidor de Impressão:**
```bash
python3 print_server.py
```

**Terminal 2 - Cliente 1:**
```bash
python3 client.py 1
```

**Terminal 3 - Cliente 2:**
```bash
python3 client.py 2
```

**Terminal 4 - Cliente 3:**
```bash
python3 client.py 3
```

### Opção 2: Script Auxiliar

```bash
./run_system.sh
```

Este script exibirá as instruções para executar o sistema.

## Algoritmo de Ricart-Agrawala

O algoritmo implementado segue os seguintes passos:

### 1. Requisição de Acesso
Quando um cliente quer imprimir:
1. Incrementa seu relógio de Lamport
2. Envia requisição a todos os outros clientes
3. Aguarda resposta de todos

### 2. Recebimento de Requisição
Quando um cliente recebe uma requisição:
1. Atualiza seu relógio de Lamport
2. Se NÃO está requisitando OU o requisitante tem maior prioridade:
   - Concede acesso imediatamente
3. Caso contrário:
   - Adia a requisição para responder depois

### 3. Entrada na Seção Crítica
Cliente entra após receber todas as respostas:
1. Envia documento ao servidor de impressão
2. Aguarda confirmação

### 4. Liberação
Após imprimir:
1. Envia notificação de liberação a todos
2. Concede acesso às requisições adiadas

## Prioridade de Requisições

A prioridade é determinada por:
1. **Timestamp de Lamport** (menor = maior prioridade)
2. **ID do Cliente** (em caso de empate, menor ID tem prioridade)

## Protocolo gRPC

### Serviço PrintingService (Servidor Burro)
```protobuf
service PrintingService {
  rpc SendToPrinter (PrintRequest) returns (PrintResponse);
}
```

### Serviço MutualExclusionService (Clientes)
```protobuf
service MutualExclusionService {
  rpc RequestAccess (AccessRequest) returns (AccessResponse);
  rpc ReleaseAccess (ReleaseMessage) returns (ReleaseResponse);
}
```

## Relógio Lógico de Lamport

Implementação das regras:
- **Evento Local**: incrementa relógio
- **Envio de Mensagem**: incrementa e anexa timestamp
- **Recebimento**: `tempo = max(tempo_local, tempo_recebido) + 1`

## Exemplo de Execução

### Servidor de Impressão
```
============================================================
PRINT SERVER (DUMB) - STARTED
============================================================
Listening on port: 50051
Waiting for print requests...
Press Ctrl+C to stop
============================================================

============================================================
[TS: 15] [Local Time: 14:32:18]
CLIENTE 1 (Request #1):
  Relatório financeiro do mês
============================================================
Printing... (simulating 2.34s delay)
✓ Print completed! Total prints: 1
```

### Cliente
```
============================================================
INTELLIGENT CLIENT 1 - STARTING
============================================================
Client Port: 50052
Print Server: localhost:50051
Other Clients: 2
============================================================

[14:32:10.123] [Client 1] [LT: 1] Started gRPC server on port 50052
[14:32:12.456] [Client 1] [LT: 2] Next request in 8.3s...
[14:32:20.789] [Client 1] [LT: 3] === Initiating print request ===
[14:32:20.790] [Client 1] [LT: 4] Requesting critical section (Request #1, TS: 4)
[14:32:20.812] [Client 1] [LT: 6] Received GRANT from Client 2 (1/2)
[14:32:20.815] [Client 1] [LT: 8] Received GRANT from Client 3 (2/2)
[14:32:20.816] [Client 1] [LT: 9] ✓ Received all replies, entering critical section
[14:32:20.817] [Client 1] [LT: 10] Sending to print server: 'Relatório financeiro do mês'
[14:32:23.234] [Client 1] [LT: 16] ✓ Print confirmed: Print completed for client 1
[14:32:23.235] [Client 1] [LT: 17] Releasing critical section (TS: 17)
[14:32:23.240] [Client 1] [LT: 17] === Print request completed (Total: 1) ===
```

## Cenários de Teste

### Cenário 1: Sem Concorrência
1. Cliente A solicita acesso
2. Outros clientes concedem imediatamente
3. Cliente A imprime e libera
4. **Resultado**: Impressão bem-sucedida sem espera

### Cenário 2: Com Concorrência
1. Cliente A e B solicitam simultaneamente enquanto C imprime
2. C termina e libera
3. A ou B imprime (menor timestamp)
4. O outro aguarda e imprime depois
5. **Resultado**: Ordem correta baseada em timestamps

### Cenário 3: Múltiplas Requisições
1. Três clientes solicitam em sequência rápida
2. Algoritmo ordena por timestamps
3. Cada um imprime na ordem correta
4. **Resultado**: Exclusão mútua garantida

## Configuração para Rede Distribuída

Para executar em máquinas diferentes:

1. **Edite `client.py`** e substitua `'localhost'` pelos IPs reais:
```python
print_server = '192.168.1.100:50051'  # IP do servidor
other_clients = [
    (2, '192.168.1.101:50053'),  # IP do cliente 2
    (3, '192.168.1.102:50054')   # IP do cliente 3
]
```

2. Configure firewall para permitir as portas (50051-50054)

3. Execute cada processo na máquina correspondente

## Características Técnicas

- **Linguagem**: Python 3.8+
- **Framework RPC**: gRPC
- **Concorrência**: Threading
- **Sincronização**: Locks e contadores
- **Ordenação**: Relógios de Lamport
- **Exclusão Mútua**: Ricart-Agrawala

## Vantagens do Sistema

1. **Descentralizado**: Não há ponto único de falha na coordenação
2. **Justo**: Ordem de acesso baseada em timestamps lógicos
3. **Eficiente**: Comunicação direta entre clientes
4. **Escalável**: Adicionar novos clientes é simples
5. **Tolerante**: Continua funcionando se clientes falharem

## Observações Importantes

- O servidor de impressão é completamente independente da coordenação
- Toda lógica de exclusão mútua está nos clientes
- Timestamps de Lamport garantem ordenação consistente
- Sistema funciona em rede local ou distribuída

## Implementação Anterior (ACO)

A implementação anterior do algoritmo de colônia de formigas para balanceamento de carga está disponível no diretório `old_aco_implementation/`. Para mais informações, consulte o README naquele diretório.

## Licença

Este projeto está licenciado sob a licença MIT.

## Autor

Fabio Andrade

## Referências

- Ricart, G., & Agrawala, A. K. (1981). An optimal algorithm for mutual exclusion in computer networks.
- Lamport, L. (1978). Time, clocks, and the ordering of events in a distributed system.
- gRPC Documentation: https://grpc.io/
