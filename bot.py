
import logging

from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv
from neonize import extract_text

from langflow_client import consultar_langflow


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

cliente = NewClient("sessao_whatsapp.db")


@cliente.event(ConnectedEv)
def conectado(client, evento):
    logging.info("WhatsApp conectado. Bot iniciado!")


@cliente.event(MessageEv)
def mensagem(client, evento):
    origem = evento.Info.MessageSource

    # Não responder a grupos ou status
    if origem.Chat.Server in ("broadcast", "g.us"):
        return

    # Não responder às próprias mensagens
    if origem.Sender == client.me.JID:
        return

    texto = (extract_text(evento.Message) or "").strip()

    if not texto:
        return

    if texto.lower() == "/ajuda":
        client.send_message(
            origem.Chat,
            "Envie sua pergunta para conversar com a IA."
        )
        return

    # Cada conversa tem um identificador independente
    sessao = f"wa-{origem.Chat.User}@{origem.Chat.Server}"

    logging.info(
        "Nova pergunta recebida: %s caracteres",
        len(texto)
    )

    try:
        resposta = consultar_langflow(
            pergunta=texto,
            sessao=sessao
        )

    except Exception:
        logging.exception("Erro ao consultar Langflow")
        resposta = (
            "Não consegui consultar a IA agora. "
            "Tente novamente mais tarde."
        )

    try:
        client.send_message(origem.Chat, resposta)

    except Exception:
        logging.exception(
            "Erro ao enviar mensagem pelo WhatsApp"
        )


if __name__ == "__main__":
    cliente.connect()
