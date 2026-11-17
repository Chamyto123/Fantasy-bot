import os
import threading
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types

app = Flask(__name__)

MODEL = "gemini-3.8-flash"
SYSTEM_INSTRUCTIONS = """
Você é o Mestre de um RPG medieval High Fantasy chamado Fantasy Bot RPG.
Conduza uma campanha cooperativa para várias pessoas na mesma sala.
Responda em português brasileiro, com narração envolvente e objetiva.
Interprete NPCs, descreva lugares, proponha desafios e reaja às decisões.
Nunca decida as ações dos jogadores.
Mantenha continuidade com o histórico fornecido.
Quando houver combate, narre por turnos e deixe claro de quem é a vez.
Não invente resultados de dados: quando precisar de teste, peça uma rolagem
ou use apenas resultados que o sistema ou os jogadores informarem.
Não controle nem fale pelos jogadores.
"""

# Protótipo simples: mensagens e histórico ficam na memória do servidor.
# Se o servidor reiniciar, a campanha reinicia também.
messages = []
history = []
lock = threading.Lock()
next_id = 1


def get_client():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "A chave GEMINI_API_KEY ainda não foi configurada no servidor."
        )
    return genai.Client(api_key=key)


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/messages")
def get_messages():
    with lock:
        return jsonify({"messages": messages[-100:]})


@app.post("/api/send")
def send_message():
    global next_id

    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()[:24]
    message = str(data.get("message", "")).strip()[:1000]

    if not name or not message:
        return jsonify({"error": "Digite seu nome e uma mensagem."}), 400

    with lock:
        user_item = {
            "id": next_id,
            "name": name,
            "text": message,
            "kind": "player",
            "time": datetime.now(timezone.utc).isoformat()
        }
        next_id += 1
        messages.append(user_item)
        history.append({
            "role": "user",
            "parts": [{"text": f"{name}: {message}"}]
        })
        conversation = list(history[-30:])

    try:
        client = get_client()
        response = client.models.generate_content(
            model=MODEL,
            contents=conversation,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTIONS,
                temperature=0.9
            )
        )
        answer = (response.text or "").strip()
        if not answer:
            answer = "O Mestre está em silêncio por um instante. Tentem novamente."
    except Exception as exc:
        # Remove a última fala do histórico para não contaminar a próxima tentativa.
        with lock:
            if history and history[-1].get("parts", [{}])[0].get("text") == f"{name}: {message}":
                history.pop()
        error_text = str(exc)
        if "503" in error_text or "UNAVAILABLE" in error_text:
            answer = "O Mestre está ocupado neste momento. Tentem novamente em alguns instantes."
        elif "API_KEY" in error_text or "key" in error_text.lower():
            answer = "Não consegui acessar a inteligência artificial. O administrador precisa conferir a chave do Gemini."
        else:
            answer = "O Mestre não conseguiu responder agora. Tentem novamente mais tarde."

    with lock:
        master_item = {
            "id": next_id,
            "name": "MESTRE IA",
            "text": answer,
            "kind": "master",
            "time": datetime.now(timezone.utc).isoformat()
        }
        next_id += 1
        messages.append(master_item)
        history.append({
            "role": "model",
            "parts": [{"text": answer}]
        })
        del messages[:-200]
        del history[:-40]

    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
