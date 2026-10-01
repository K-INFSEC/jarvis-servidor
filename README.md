# Jarvis: Assistente Virtual Autônomo

## Visão Geral do Projeto
O Projeto Jarvis é um assistente virtual autônomo projetado para receber comandos de voz, processar a intenção do usuário utilizando modelos de Inteligência Artificial de última geração, e retornar a resposta falada.

O sistema possui uma arquitetura dividida: um cliente nativo Android (Walkie-Talkie) e um servidor Python (Cérebro) hospedado na nuvem.

---

## Status Atual (Fase 1 e 2 Concluídas)
O projeto encontra-se com a sua infraestrutura base 100% validada e funcional (MVP). O ciclo de ponta-a-ponta (captura de voz -> rede -> IA -> síntese de voz) está operante.

### O Que Já Está Implementado (Funcionalidades)
- **Push-to-Talk (Walkie-Talkie):** Interface simples no Android. O usuário pressiona um botão para falar e solta para enviar.
- **Reconhecimento de Voz Nativo:** Utiliza o `SpeechRecognizer` do Android para transcrever o áudio do usuário para texto (Speech-to-Text).
- **Processamento de IA via Groq:** O backend utiliza o modelo `allam-2-7b` rodando na infraestrutura ultra-rápida (LPU) da Groq para processar as perguntas e gerar respostas.
- **Respostas Faladas (TTS):** Utiliza o `TextToSpeech` nativo do Android, ajustado para uma voz mais grave (`pitch=0.7`) e rápida (`rate=1.25`) para simular a voz do assistente.
- **Acesso Ubíquo (Wi-Fi e 5G):** O aplicativo é capaz de conectar-se ao servidor na nuvem a partir de qualquer rede móvel.

---

## Arquitetura do Sistema

### 1. Frontend (App Android - Cliente)
- **Linguagem/Framework:** Kotlin / Views XML.
- **Componentes Principais:**
  - `MainActivity.kt`: Controla o ciclo de vida, o microfone, as permissões e o TextToSpeech.
  - `OkHttp`: Gerencia as requisições HTTP para a nuvem. Configurado com timeout de 60 segundos (resiliência a *Cold Start*).
  - **Form-URL-Encoded:** O aplicativo foi migrado de requisições JSON estritas para `FormBody` a fim de evitar corrompimento de caracteres e erros HTTP 422 ao atravessar proxies de nuvem.
  - `network_security_config.xml`: Configurações de segurança de rede (`trust-anchors`) para permitir tráfego HTTPS irrestrito em redes 5G, evitando bloqueios nativos do Android.

### 2. Backend (Servidor Python - Nuvem)
- **Linguagem/Framework:** Python / FastAPI.
- **Hospedagem:** Render (Plano Free Tier) com proxy reverso Cloudflare.
- **Integração de IA:** SDK oficial do `groq` conectando-se ao modelo `allam-2-7b`.
- **Componentes Principais:**
  - `server.py`: Expõe a rota `/chat` que recebe o texto via POST (Form Data).
  - **Mecanismo de Resiliência (Retry):** Um loop `try/except` que detecta instabilidades na API da Groq (Erro 503) e realiza até 3 retentativas com *sleep* de 2 segundos antes de falhar.
  - **Tratamento de Exceções:** Todos os erros da API (como limite de cota) são extraídos e devolvidos detalhadamente (`detail`) na resposta HTTP (500) para facilitar o debug pelo cliente Android.

---

## Log de Problemas Resolvidos (Troubleshooting History)
Durante o desenvolvimento, vários gargalos técnicos foram superados:
1. **Erro 422 (Unprocessable Entity):** Resolvido abandonando o envio via JSON pelo OkHttp e migrando para `Form-URL-Encoded`, devido à formatação de aspas duplas no proxy do Render.
2. **Falha Exclusiva no 5G:** Resolvida criando o `network_security_config.xml` para contornar políticas agressivas de certificado TLS em conexões de dados móveis no Android.
3. **Erros de Cota e Modelos (429 / 400 / 404):** O projeto iniciou usando Google Gemini (2.5/3.8 Flash), mas atingiu limites de cota da camada gratuita (Erro 429). Migramos para a Groq. Na Groq, descobrimos via script de diagnóstico direto que a conta específica tinha acesso barrado à família Llama (Erro 400/404), exigindo o uso do modelo garantido `allam-2-7b`.

---

## Próximos Passos (Roadmap - Fase 3 e 4)

1. **Aprimoramento da Sintetização de Voz (TTS):** Substituir o motor nativo do Android pela geração de áudio no backend (Edge TTS ou ElevenLabs) e devolver arquivo MP3.
2. **Memória e Contexto (RAG):** Implementar um Banco de Dados Vetorial (Pinecone/Chroma) ou lista circular no Python para gerenciar o histórico de conversação de curto e longo prazo.
3. **Agent Tools (Function Calling):** Configurar o LLM para orquestrar chamadas de funções no Python para:
   - Pesquisa web em tempo real (Tavily/DuckDuckGo).
   - Manipulação de e-mails, agendas e lembretes (APIs do Google Workspace).
   - Previsão do tempo (OpenWeather).
4. **Acionamento por Voz (Wake Word):** Integrar a engine *Picovoice Porcupine* no Android para eliminar a necessidade de pressionar o botão, permitindo ativação contínua e offline (ex: "Ei, Jarvis").
5. **Ajuste de Persona:** Refinar o `system_prompt` para garantir respostas curtas, naturais e menos enciclopédicas.
