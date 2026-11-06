# WhatsApp + Langflow em Python

Bot que recebe mensagens de texto no WhatsApp, consulta um fluxo do Langflow e envia a resposta na mesma conversa. A conexão com o WhatsApp usa a biblioteca Neonize, e as chamadas ao Langflow usam sua API HTTP.

```text
Mensagem no WhatsApp → Bot Python → API do Langflow → Resposta no WhatsApp
```

## Pré-requisitos

- Python e `pip` disponíveis no terminal. O ambiente de desenvolvimento deste projeto usa Python 3.13.
- Uma conta do WhatsApp para vincular ao bot.
- Uma instância do Langflow acessível, com um fluxo configurado para entrada e saída de chat.
- ID do fluxo e, se a instância exigir autenticação, uma chave de API.

O Langflow e o modelo usado pelo fluxo devem ser configurados separadamente. Este repositório não inclui um fluxo exportado nem instala o Langflow ou o Ollama.

## Instalação

No PowerShell, clone o projeto e crie um ambiente virtual:

```powershell
git clone https://github.com/EricoBorgonove/whatsapp-langflow-python.git
cd whatsapp-langflow-python
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Os comandos abaixo usam diretamente o Python do ambiente virtual, sem precisar ativá-lo.

## Configuração

Edite o arquivo `.env` com os dados da sua instância:

```dotenv
LANGFLOW_URL=http://localhost:7860
FLOW_ID=id-real-do-seu-fluxo
LANGFLOW_API_KEY=
```

| Variável | Descrição |
| --- | --- |
| `LANGFLOW_URL` | Endereço base do Langflow, sem o caminho da API. |
| `FLOW_ID` | ID real do fluxo que receberá as perguntas. Substitua o exemplo `SEU_FLOW_ID`. |
| `LANGFLOW_API_KEY` | Chave enviada no cabeçalho `x-api-key`. Substitua `SUA_CHAVE` ou deixe vazio quando a instância não exigir autenticação. |

O cliente faz requisições para `POST /api/v1/run/{FLOW_ID}`, com entrada e saída do tipo `chat` e tempo limite de 120 segundos. Cada conversa recebe um `session_id` próprio; o uso desse identificador para manter memória depende da configuração do fluxo.

## Executar o bot

Com o Langflow disponível e o `.env` preenchido, execute na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe bot.py
```

Na primeira conexão, acompanhe o terminal e vincule a conta pelo QR Code, usando a opção de aparelhos conectados no WhatsApp. A sessão é armazenada localmente em `sessao_whatsapp.db` para reutilização nas próximas execuções.

Envie uma mensagem de outra conta para o número conectado. O bot encaminha o texto ao Langflow e devolve a resposta. O comando `/ajuda` mostra uma orientação de uso, sem consultar a IA.

O bot ignora grupos, status, mensagens sem texto e mensagens identificadas como enviadas pelo próprio cliente. Se a consulta ao Langflow falhar, ele tenta responder pedindo uma nova tentativa mais tarde. Para encerrar, pressione `Ctrl+C`.

## Verificações manuais

Os scripts abaixo acessam serviços reais. Execute apenas um dos clientes WhatsApp por vez, pois eles compartilham o mesmo banco de sessão.

### Consultar somente o Langflow

```powershell
.\.venv\Scripts\python.exe teste_conexao.py
```

Digite uma pergunta no terminal. Esse script usa a sessão `teste-terminal` e não conecta ao WhatsApp.

### Verificar a conexão com o WhatsApp

```powershell
.\.venv\Scripts\python.exe conecta_whatsapp.py
```

Conecta ao WhatsApp e responde às mensagens de texto recebidas com uma confirmação, sem consultar o Langflow.

### Acompanhar a integração completa

```powershell
.\.venv\Scripts\python.exe teste_recebimento.py
```

Executa a integração com logs detalhados de recebimento, consulta e resposta. Esse script exibe no terminal identificadores de conversa, textos recebidos e respostas da IA. Ele usa um prefixo de sessão diferente do `bot.py`, portanto o identificador enviado ao Langflow também muda.

Esses scripts são verificações manuais; não constituem uma suíte de testes automatizados.

## Arquivos do projeto

| Arquivo | Finalidade |
| --- | --- |
| `bot.py` | Executa o bot com integração ao Langflow e logs básicos. |
| `langflow_client.py` | Carrega o `.env`, consulta a API e extrai o texto da resposta. |
| `conecta_whatsapp.py` | Verifica conexão, recebimento e resposta pelo WhatsApp. |
| `teste_conexao.py` | Permite consultar o Langflow pelo terminal. |
| `teste_recebimento.py` | Executa a integração com logs detalhados. |
| `requirements.txt` | Lista as dependências Python. |
| `.env.example` | Modelo das variáveis de ambiente. |
| `.gitignore` | Exclui credenciais, sessão, ambiente virtual e caches do Git. |

## Problemas comuns

- **Erro de conexão com o Langflow:** confirme se a instância está em execução e se `LANGFLOW_URL` é acessível a partir da máquina do bot.
- **Erro HTTP na consulta:** confira o ID do fluxo, a chave de API e os logs do Langflow.
- **Formato de saída inesperado:** verifique se o fluxo retorna uma mensagem de chat. O cliente espera a mensagem em `outputs[0].outputs[0].results.message`.
- **Bot sem responder:** confirme a conexão no terminal e teste com texto enviado por outra conta em conversa individual.

Mantenha o `.env` e o banco `sessao_whatsapp.db` privados. Ambos estão excluídos do versionamento pelo `.gitignore`.
