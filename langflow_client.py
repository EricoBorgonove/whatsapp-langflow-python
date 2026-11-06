
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def consultar_langflow(pergunta: str, sessao: str) -> str:
    base = os.getenv(
        "LANGFLOW_URL",
        "http://localhost:7860"
    ).rstrip("/")

    flow_id = os.getenv("FLOW_ID", "").strip()
    chave = os.getenv("LANGFLOW_API_KEY", "").strip()

    if not flow_id or flow_id == "COLOQUE_O_ID_DO_FLUXO":
        raise RuntimeError("Configure FLOW_ID no arquivo .env")

    url = f"{base}/api/v1/run/{flow_id}"

    payload = {
        "input_value": pergunta,
        "input_type": "chat",
        "output_type": "chat",
        "session_id": sessao
    }

    headers = {"Content-Type": "application/json"}

    if chave and chave != "COLOQUE_SUA_CHAVE":
        headers["x-api-key"] = chave

    resposta = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=120
    )
    resposta.raise_for_status()

    dados = resposta.json()

    try:
        item = dados["outputs"][0]["outputs"][0]
        mensagem = item["results"]["message"]

        if isinstance(mensagem, str):
            texto = mensagem
        else:
            texto = mensagem.get("text") or (
                mensagem.get("data", {}).get("text")
            )

        if not texto:
            raise ValueError("Saída sem texto")

        return str(texto)

    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise RuntimeError(
            f"Formato de saída inesperado: {str(dados)[:700]}"
        ) from exc
