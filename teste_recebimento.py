
from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv
from neonize import extract_text

from langflow_client import consultar_langflow


# ==========================================
# CONFIGURAÇÃO DO WHATSAPP
# ==========================================

cliente = NewClient("sessao_whatsapp.db")


# ==========================================
# EVENTO: WHATSAPP CONECTADO
# ==========================================

@cliente.event(ConnectedEv)
def conectado(client, evento):
    print("\n✅ WhatsApp conectado!", flush=True)
    print("🤖 Bot integrado ao Langflow!", flush=True)
    print("Aguardando mensagens...\n", flush=True)


# ==========================================
# EVENTO: NOVA MENSAGEM
# ==========================================

@cliente.event(MessageEv)
def mensagem(client, evento):

    print("\n========== NOVA MENSAGEM ==========", flush=True)

    try:
        origem = evento.Info.MessageSource
        texto = (extract_text(evento.Message) or "").strip()

        print("Chat:", origem.Chat, flush=True)
        print("Remetente:", origem.Sender, flush=True)
        print("Enviada por mim:", origem.IsFromMe, flush=True)
        print("Texto:", repr(texto), flush=True)

        # Ignorar mensagens enviadas pelo próprio bot
        if origem.IsFromMe:
            print("Ignorando mensagem própria.", flush=True)
            return

        # Ignorar grupos e status
        if origem.Chat.Server in ("g.us", "broadcast"):
            print("Ignorando grupo ou status.", flush=True)
            return

        # Ignorar mensagens vazias
        if not texto:
            print("Mensagem sem texto.", flush=True)
            return

        # Comando de ajuda
        if texto.lower() == "/ajuda":
            client.reply_message(
                "🤖 Olá! Sou um assistente com IA.\n\n"
                "Envie sua pergunta para conversar comigo.",
                evento
            )
            print("Ajuda enviada.", flush=True)
            return

        # ==========================================
        # CONSULTAR O LANGFLOW
        # ==========================================

        print("\n🔄 Consultando Langflow...", flush=True)

        # Identificador exclusivo para cada conversa
        sessao = (
            f"whatsapp-{origem.Chat.User}"
            f"@{origem.Chat.Server}"
        )

        try:
            resposta = consultar_langflow(
                pergunta=texto,
                sessao=sessao
            )

            print("\n✅ Resposta recebida do Langflow:", flush=True)
            print(resposta, flush=True)

        except Exception as erro:
            print(
                "\n❌ Erro ao consultar Langflow:",
                repr(erro),
                flush=True
            )

            resposta = (
                "⚠️ Não consegui consultar a IA agora.\n"
                "Por favor, tente novamente mais tarde."
            )

        # ==========================================
        # ENVIAR RESPOSTA AO WHATSAPP
        # ==========================================

        print("\n📤 Enviando resposta...", flush=True)

        client.reply_message(resposta, evento)

        print("✅ Resposta enviada!", flush=True)

    except Exception as erro:
        print(
            "\n❌ ERRO NO PROCESSAMENTO:",
            repr(erro),
            flush=True
        )


# ==========================================
# INICIAR BOT
# ==========================================

if __name__ == "__main__":
    print("====================================")
    print("   WHATSAPP + LANGFLOW + OLLAMA")
    print("====================================")
    print("Iniciando WhatsApp...", flush=True)

    cliente.connect()
