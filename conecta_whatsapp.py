
from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv
from neonize import extract_text

cliente = NewClient("sessao_whatsapp.db")


@cliente.event(ConnectedEv)
def conectado(client, evento):
    print("\n✅ WhatsApp conectado!", flush=True)
    print("Aguardando mensagens...\n", flush=True)


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

        if origem.IsFromMe:
            print("Ignorando mensagem própria.", flush=True)
            return

        if origem.Chat.Server in ("g.us", "broadcast"):
            print("Ignorando grupo ou status.", flush=True)
            return

        if not texto:
            print("Mensagem sem texto.", flush=True)
            return

        print("Enviando resposta...", flush=True)

        client.reply_message(
            "✅ Recebi sua mensagem: " + texto,
            evento
        )

        print("✅ Resposta enviada!", flush=True)

    except Exception as erro:
        print("❌ ERRO:", repr(erro), flush=True)


if __name__ == "__main__":
    print("Iniciando WhatsApp...", flush=True)
    cliente.connect()
