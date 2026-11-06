from langflow_client import consultar_langflow

pergunta = input("Pergunta para o agente: ")

try:
    resposta = consultar_langflow(
        pergunta,
        "teste-terminal"
    )
    print("IA:", resposta)

except Exception as erro:
    print("Erro ao chamar Langflow:", erro)