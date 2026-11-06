
import sqlite3
import threading

from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv
from neonize import extract_text

from langflow_client import consultar_langflow


# ==========================================
# CONFIGURACOES GERAIS
# ==========================================

BANCO = "usuarios_bot.db"
SESSAO_WHATSAPP = "sessao_whatsapp.db"

cliente = NewClient(SESSAO_WHATSAPP)

controle_usuarios = threading.Lock()


# ==========================================
# BANCO DE DADOS SQLITE
# ==========================================

def iniciar_banco():

    with sqlite3.connect(BANCO, timeout=15) as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                identificador TEXT PRIMARY KEY,
                primeira_interacao TEXT
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

    print("Banco SQLite inicializado!", flush=True)


def usuario_cadastrado(identificador):

    with sqlite3.connect(BANCO, timeout=15) as conexao:
        cursor = conexao.execute(
            """
            SELECT 1 FROM usuarios
            WHERE identificador = ?
            """,
            (identificador,)
        )

        return cursor.fetchone() is not None


def cadastrar_usuario(identificador):

    with sqlite3.connect(BANCO, timeout=15) as conexao:
        conexao.execute(
            """
            INSERT OR IGNORE INTO usuarios
            (identificador)
            VALUES (?)
            """,
            (identificador,)
        )


# ==========================================
# MENSAGENS DO CHATBOT
# ==========================================

def gerar_boas_vindas():

    return (
        "👋 *Seja bem-vindo(a)!*\n\n"
        "🤖 Sou seu assistente de Inteligência "
        "Artificial, desenvolvido com Python, "
        "Langflow e Ollama.\n\n"
        "📋 *Comandos disponíveis:*\n\n"
        "/menu - Exibir o menu\n"
        "/ajuda - Como utilizar\n"
        "/sobre - Informações do projeto\n\n"
        "💬 Pode enviar sua pergunta!"
    )


def gerar_menu():

    return (
        "🤖 *MENU DO ASSISTENTE IA*\n\n"
        "📋 /menu - Exibir este menu\n\n"
        "❓ /ajuda - Como utilizar o assistente\n\n"
        "ℹ️ /sobre - Informações sobre o projeto\n\n"
        "💬 Envie qualquer pergunta para "
        "conversar com nosso agente de IA."
    )


def gerar_ajuda():

    return (
        "❓ *COMO UTILIZAR O ASSISTENTE*\n\n"
        "1. Envie uma pergunta pelo WhatsApp.\n"
        "2. Sua mensagem será encaminhada "
        "ao agente de IA no Langflow.\n"
        "3. O agente processará sua pergunta "
        "utilizando o Ollama.\n"
        "4. Você receberá a resposta "
        "diretamente nesta conversa.\n\n"
        "📋 Digite /menu para ver os comandos."
    )


def gerar_sobre():

    return (
        "ℹ️ *SOBRE O ASSISTENTE*\n\n"
        "Projeto: WhatsApp Langflow Python\n\n"
        "Tecnologias utilizadas:\n"
        "🐍 Python\n"
        "💬 WhatsApp + Neonize\n"
        "🔗 Langflow\n"
        "🤖 Ollama\n"
        "🗄️ SQLite\n\n"
        "O processamento da inteligência "
        "artificial é realizado localmente "
        "por meio do Ollama.\n\n"
        "Projeto desenvolvido para fins "
        "educacionais."
    )


# ==========================================
# EVENTO: WHATSAPP CONECTADO
# ==========================================

@cliente.event(ConnectedEv)
def conectado(client, evento):

    print("\n✅ WhatsApp conectado!", flush=True)
    print("🤖 Bot integrado ao Langflow!", flush=True)
    print("📨 Aguardando mensagens...\n", flush=True)


# ==========================================
# EVENTO: NOVA MENSAGEM
# ==========================================

@cliente.event(MessageEv)
def mensagem(client, evento):

    print(
        "\n========== NOVA MENSAGEM ==========",
        flush=True
    )

    try:
        origem = evento.Info.MessageSource
        texto = (extract_text(evento.Message) or "").strip()

        print("Chat:", origem.Chat, flush=True)
        print("Remetente:", origem.Sender, flush=True)
        print("Enviada por mim:", origem.IsFromMe, flush=True)
        print("Texto:", repr(texto), flush=True)

        # ----------------------------------
        # IGNORAR MENSAGENS PROPRIAS
        # ----------------------------------

        if origem.IsFromMe:
            print("Mensagem propria ignorada.", flush=True)
            return

        # ----------------------------------
        # IGNORAR GRUPOS E STATUS
        # ----------------------------------

        if origem.Chat.Server in ("g.us", "broadcast"):
            print("Grupo ou status ignorado.", flush=True)
            return

        # ----------------------------------
        # IGNORAR MENSAGENS VAZIAS
        # ----------------------------------

        if not texto:
            print("Mensagem sem texto.", flush=True)
            return

        # ----------------------------------
        # IDENTIFICAR A CONVERSA
        # ----------------------------------

        identificador = (
            f"{origem.Chat.User}@{origem.Chat.Server}"
        )

        print("Identificador:", identificador, flush=True)

        # ==================================
        # PRIMEIRA INTERACAO
        # ==================================

        with controle_usuarios:

            primeiro_contato = not usuario_cadastrado(
                identificador
            )

            if primeiro_contato:

                print(
                    "\n👋 Novo usuario identificado!",
                    flush=True
                )

                client.reply_message(
                    gerar_boas_vindas(),
                    evento
                )

                cadastrar_usuario(identificador)

                print(
                    "Boas-vindas enviadas e "
                    "usuario cadastrado!",
                    flush=True
                )

                return

        # ==================================
        # COMANDOS
        # ==================================

        comando = texto.lower()

        # COMANDO /menu

        if comando == "/menu":

            print("Comando /menu recebido.", flush=True)

            client.reply_message(
                gerar_menu(),
                evento
            )

            print("Menu enviado!", flush=True)
            return

        # COMANDO /ajuda

        if comando == "/ajuda":

            print("Comando /ajuda recebido.", flush=True)

            client.reply_message(
                gerar_ajuda(),
                evento
            )

            print("Ajuda enviada!", flush=True)
            return

        # COMANDO /sobre

        if comando == "/sobre":

            print("Comando /sobre recebido.", flush=True)

            client.reply_message(
                gerar_sobre(),
                evento
            )

            print("Informacoes enviadas!", flush=True)
            return

        # ==================================
        # CONSULTAR O LANGFLOW
        # ==================================

        print("\n🔄 Consultando Langflow...", flush=True)

        sessao = f"whatsapp-{identificador}"

        try:

            resposta = consultar_langflow(
                pergunta=texto,
                sessao=sessao
            )

            print(
                "\n✅ Resposta recebida do Langflow:",
                flush=True
            )

            print(resposta, flush=True)

        except Exception as erro:

            print(
                "\n❌ Erro ao consultar Langflow:",
                repr(erro),
                flush=True
            )

            resposta = (
                "⚠️ Não consegui consultar "
                "a IA agora.\n\n"
                "Por favor, tente novamente "
                "mais tarde."
            )

        # ==================================
        # ENVIAR RESPOSTA AO WHATSAPP
        # ==================================

        print("\n📤 Enviando resposta...", flush=True)

        client.reply_message(
            resposta,
            evento
        )

        print("✅ Resposta enviada!", flush=True)

    except Exception as erro:

        print(
            "\n❌ ERRO NO PROCESSAMENTO:",
            repr(erro),
            flush=True
        )


# ==========================================
# INICIAR APLICACAO
# ==========================================

if __name__ == "__main__":

    print("====================================")
    print("  WHATSAPP + LANGFLOW + OLLAMA")
    print("====================================")

    iniciar_banco()

    print("Iniciando WhatsApp...", flush=True)

    cliente.connect()
