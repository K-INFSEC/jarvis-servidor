import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
import uvicorn
import time

# Inicializa o app FastAPI
app = FastAPI()

# Inicializa o cliente do Google GenAI
# Certifique-se de configurar a variável de ambiente GEMINI_API_KEY no seu sistema
# Exemplo (Windows PowerShell): $env:GEMINI_API_KEY="SuaChaveAqui"
# Exemplo (Mac/Linux): export GEMINI_API_KEY="SuaChaveAqui"
# O cliente puxa automaticamente a chave da variável GEMINI_API_KEY
client = genai.Client()

# Define o modelo de dados para a requisição recebida
class ChatRequest(BaseModel):
    message: str

# Rota /chat (aceita POST)
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        user_message = request.message
        print(f"Mensagem recebida do Android: {user_message}")

        # Configura as instruções do sistema (System Prompt)
        # e ajusta a criatividade através da temperatura.
        config = types.GenerateContentConfig(
            system_instruction="Você é um assistente autônomo. Responda de forma concisa e natural.",
            temperature=0.7,
        )

        # Inicia a sessão de chat (recomendado para gerenciar histórico e permitir AFC - Automatic Function Calling)
        chat = client.chats.create(
            model='gemini-3.8-flash',
            config=config
        )

        max_retries = 3
        retry_delay = 2 # segundos de espera entre as tentativas
        response = None

        for attempt in range(max_retries):
            try:
                # Envia a mensagem utilizando o chat.send_message
                response = chat.send_message(user_message)
                break # Se der certo, sai do loop imediatamente
            except Exception as api_error:
                if "503" in str(api_error) and attempt < max_retries - 1:
                    print(f"Aviso: API sobrecarregada (503). Tentativa {attempt + 1} falhou. Retentando em {retry_delay} segundos...")
                    time.sleep(retry_delay)
                else:
                    # Re-lança a exceção se esgotar as tentativas ou for outro tipo de erro
                    raise api_error

        # Extrai a resposta textual
        ai_reply = response.text
        print(f"Resposta gerada pelo Gemini: {ai_reply}")

        # Retorna no formato JSON esperado pelo Android
        return {"reply": ai_reply}

    except Exception as e:
        print(f"Erro ao processar a mensagem: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a requisição com o Gemini.")

if __name__ == "__main__":
    print("Iniciando o cérebro do Jarvis (Powered by Gemini) na porta 5000...")
    uvicorn.run(app, host="0.0.0.0", port=5000)
