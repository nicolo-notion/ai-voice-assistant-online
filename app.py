from flask import Flask, request, jsonify, Response
import time

app = Flask(__name__)

# ---------- LOGICA ASSISTENTE ----------
def genera_risposta(testo: str) -> str:
    t = (testo or "").lower()
    if "ciao" in t:
        return "Ciao! Come stai?"
    elif "come stai" in t:
        return "Tutto bene, grazie!"
    elif "che ore sono" in t:
        return f"Ora sono le {time.strftime('%H:%M')}"
    elif "esci" in t or "quit" in t or "exit" in t:
        return "Ok, alla prossima!"
    else:
        return "Non ho ancora imparato a rispondere a questo."

# ---------- PAGINA WEB (HTML integrato) ----------
PAGE = """<!doctype html>
<html lang="it"><head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Assistente vocale</title>
<style>
  body{font-family:system-ui,Arial,sans-serif;margin:0;background:#0b1020;color:#e9eefc}
  .app{max-width:720px;margin:0 auto;padding:16px}
  #log{background:#121935;border:1px solid #243056;border-radius:12px;padding:12px;height:55vh;overflow:auto}
  .tu{margin:8px 0;padding:10px 12px;background:#1a2452;border-radius:10px}
  .ai{margin:8px 0;padding:10px 12px;background:#1b3a2e;border-radius:10px}
  .controls{display:flex;gap:8px;margin-top:12px}
  button{padding:10px 14px;border:0;border-radius:10px;background:#5869ff;color:#fff;font-weight:600;cursor:pointer}
  input{flex:1;padding:10px 12px;border-radius:10px;border:1px solid #243056;background:#0f1630;color:#e9eefc}
</style>
</head><body>
<div class="app">
  <h1>Assistente vocale</h1>
  <div id="log"></div>
  <div class="controls">
    <button id="talkBtn">🎤 Parla</button>
    <input id="textInput" placeholder="Scrivi qui e premi Invio…" />
  </div>
  <div class="hint">Suggerimenti: "ciao", "come stai", "che ore sono", "esci"</div>
</div>
<script>
const log = document.getElementById("log");
const talkBtn = document.getElementById("talkBtn");
const textInput = document.getElementById("textInput");

function addMsg(cls, text){
  const el = document.createElement("div");
  el.className = cls;
  el.textContent = (cls==="tu"?"Tu: ":"Assistente: ")+text;
  log.appendChild(el); log.scrollTop = log.scrollHeight;
}
function speak(text){
  if(!("speechSynthesis" in window)) return;
  const u = new SpeechSynthesisUtterance(text);
  u.lang="it-IT"; u.rate=1; speechSynthesis.cancel(); speechSynthesis.speak(u);
}
async function askServer(text){
  const r = await fetch("/reply",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text})});
  return (await r.json()).reply;
}
async function handleText(text){
  if(!text) return;
  addMsg("tu", text);
  try{ const reply = await askServer(text); addMsg("ai", reply); speak(reply);}
  catch{ addMsg("ai","Errore di rete. Riprova.");}
}
textInput.addEventListener("keydown", e=>{
  if(e.key==="Enter"){ const v=textInput.value.trim(); textInput.value=""; handleText(v); }
});
let recognition=null;
if("webkitSpeechRecognition" in window || "SpeechRecognition" in window){
  const Rec = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new Rec(); recognition.lang="it-IT"; recognition.interimResults=false; recognition.continuous=false;
  recognition.onresult = e=> handleText(e.results[0][0].transcript);
  recognition.onerror = e=>{ if(e.error==="not-allowed"){ alert("Consenti il microfono al browser."); } };
}
talkBtn.onclick = ()=>{ if(!recognition){ alert("Usa Safari (iPhone) o Chrome (Android)."); return; } recognition.start(); };
addMsg("ai","Ciao! Premi 'Parla' oppure scrivi un messaggio.");
</script>
</body></html>"""

@app.get("/")
def index():
    return Response(PAGE, mimetype="text/html")

@app.post("/reply")
def reply():
    data = request.get_json(force=True) or {}
    text = data.get("text","")
    return jsonify({"reply": genera_risposta(text)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
