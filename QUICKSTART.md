# Quick Start Guide

## Sistema de Impressão Distribuído com Ricart-Agrawala

Este guia rápido mostra como executar o sistema em poucos minutos.

## Pré-requisitos

- Python 3.8 ou superior
- pip3

## Instalação (1 minuto)

```bash
# Clone o repositório
git clone https://github.com/fabioacandrade/network-load-balancer-ant-colony.git
cd network-load-balancer-ant-colony

# Instale as dependências
pip3 install -r requirements.txt
```

## Execução (Opção Simples)

### Abra 4 terminais e execute:

**Terminal 1:**
```bash
python3 print_server.py
```

**Terminal 2:**
```bash
python3 client.py 1
```

**Terminal 3:**
```bash
python3 client.py 2
```

**Terminal 4:**
```bash
python3 client.py 3
```

## O que Observar

### No Servidor de Impressão (Terminal 1):
- Aguarda passivamente por requisições
- Imprime documentos com delay de 2-3s
- Mostra timestamp de Lamport e ID do cliente

### Nos Clientes (Terminais 2, 3, 4):
- Cada cliente:
  - Coordena com outros clientes usando Ricart-Agrawala
  - Gera requisições automáticas a cada 5-15 segundos
  - Mostra logs detalhados com timestamps lógicos
  - Exibe quando concede/adia acesso
  - Mostra quando entra/sai da seção crítica

## Comportamento Esperado

1. **Sem Concorrência**: Quando apenas um cliente quer imprimir, obtém acesso imediatamente

2. **Com Concorrência**: Quando múltiplos clientes querem imprimir simultaneamente:
   - Coordenam usando timestamps de Lamport
   - Cliente com menor timestamp tem prioridade
   - Outros aguardam sua vez
   - Exclusão mútua garantida

## Logs Típicos

### Cliente requisitando acesso:
```
[14:32:20.789] [Client 1] [LT: 3] === Initiating print request ===
[14:32:20.790] [Client 1] [LT: 4] Requesting critical section (Request #1, TS: 4)
[14:32:20.812] [Client 1] [LT: 6] Received GRANT from Client 2 (1/2)
[14:32:20.815] [Client 1] [LT: 8] Received GRANT from Client 3 (2/2)
[14:32:20.816] [Client 1] [LT: 9] ✓ Received all replies, entering critical section
```

### Servidor imprimindo:
```
============================================================
[TS: 15] [Local Time: 14:32:18]
CLIENTE 1 (Request #1):
  Relatório financeiro do mês
============================================================
Printing... (simulating 2.34s delay)
✓ Print completed! Total prints: 1
```

## Parando o Sistema

Pressione `Ctrl+C` em cada terminal para parar os processos.

## Resolução de Problemas

### Erro: "Address already in use"
- Certifique-se de que nenhum outro processo está usando as portas 50051-50054
- Mate processos anteriores: `pkill -f "python3 print_server.py"`

### Erro: "No module named 'grpc'"
- Execute: `pip3 install -r requirements.txt`

### Clientes não se conectam
- Certifique-se de que o servidor está rodando primeiro
- Aguarde 2-3 segundos após iniciar o servidor antes de iniciar os clientes

## Próximos Passos

- Consulte o [README.md](README.md) para documentação completa
- Modifique os endereços IP em `client.py` para executar em rede distribuída
- Ajuste os intervalos de geração de requisições no código

## Contato

Para dúvidas ou problemas, abra uma issue no GitHub.
