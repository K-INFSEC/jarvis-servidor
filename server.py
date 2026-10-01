import os
from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
from groq import Groq
import uvicorn
import time

# Inicializa o app FastAPI
app = FastAPI()

# Inicializa o cliente Groq
# O Groq vai usar a variável de ambiente GROQ_API_KEY
client = Groq()

# Rota /chat (aceita POST com Form Data)
@app.post("/chat")
async def chat_endpoint(message: str = Form(...)):
    try:
        user_message = message
        print(f"Mensagem recebida do Android: {user_message}")

        max_retries = 3
        retry_delay = 2 # segundos
        response = None

        for attempt in range(max_retries):
            try:
                # Chama a API ultra rápida do Groq (Usando o modelo estável padrão)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "Você é um assistente autônomo. Responda de forma concisa e natural."
                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],
                    model="llama3-8b-8192",
                    temperature=0.7,
                )
                response = chat_completion
                break
            except Exception as api_error:
                if "503" in str(api_error) and attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise api_error

        # Extrai a resposta textual
        ai_reply = response.choices[0].message.content
        print(f"Resposta gerada pelo Llama 3: {ai_reply}")

        # Retorna no formato JSON esperado pelo Android
        return {"reply": ai_reply}

    except Exception as e:
        print(f"Erro detalhado ao processar a mensagem: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno do Groq: {str(e)}")

if __name__ == "__main__":
    print("Iniciando o cérebro do Jarvis (Powered by Groq) na porta 5000...")
    uvicorn.run(app, host="0.0.0.0", port=5000)
