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
<title>J.A.R.V.I.S.</title>
<style>
  :root{
    --bg:#0d1117;          /* sfondo scuro */
    --panel:#121826;       /* pannello chat */
    --border:#243b55;      /* bordo freddo */
    --text:#f5f7ff;        /* testo chiaro */
    --muted:#cbd5e1;       /* testo secondario */
    --iron-red:#b91c1c;    /* rosso Iron Man */
    --iron-red-dark:#7f1212;
    --gold:#f59e0b;        /* oro */
    --arc:#22d3ee;         /* arc reactor */
  }

  *{box-sizing:border-box}
  body{
    margin:0; color:var(--text);
    font-family:system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    font-size:16px; line-height:1.55;
    -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
  background:
    /* velo scuro per leggibilità del testo */
    linear-gradient(rgba(0,0,0,.68), rgba(0,0,0,.68)),
    /* la tua immagine (cache buster v=1) */
    url('/static/bg.jpg?v=1') center / cover no-repeat,
    /* i TUOI gradienti originali sotto all'immagine */
    radial-gradient(900px 500px at 70% -10%, rgba(34,211,238,.12), transparent 60%),
    linear-gradient(180deg, #0b0f16 0%, #0d1117 100%);
  }

  .app{max-width:900px;margin:0 auto;padding:16px}
 h1{
  margin:10px 0 14px;
  font-size: clamp(26px, 3.2vw, 34px); /* grande ma responsive */
  font-weight: 800;
  letter-spacing: .3px;
  line-height: 1.2;
  text-shadow: 0 2px 6px rgba(0,0,0,.35); /* leggero alone per leggibilità */
}

  /* Contenitore chat */
  #log{
    background:var(--panel);
    border:1px solid var(--border);
    border-radius:14px;
    padding:14px; height:60vh; overflow:auto;
    box-shadow:0 10px 24px rgba(0,0,0,.35);
  }

  /* Bolle messaggi: ALTISSIMO CONTRASTO */
  .tu,.ai{
    margin:10px 0; padding:12px 14px;
    border-radius:12px; line-height:1.5; font-size:16px;
    word-wrap:break-word;
  }
  .tu{
    background:linear-gradient(135deg, var(--iron-red), var(--iron-red-dark));
    color:#ffffff;
    border:1px solid rgba(245,158,11,.55); /* bordo oro */
    box-shadow:0 4px 10px rgba(185,28,28,.30);
  }
  .ai{
    background:linear-gradient(135deg, #0c2b3d, #123a53);
    color:#e6fbff;
    border:1px solid rgba(34,211,238,.55); /* bordo arc */
    box-shadow:0 4px 12px rgba(34,211,238,.22);
  }

  /* Controlli in basso */
  .controls{display:flex;gap:10px;margin-top:12px}
  input{
    flex:1; padding:12px 14px; border-radius:10px;
    border:1px solid var(--border);
    background:#0f1629; color:var(--text);
    outline:none; transition:border .15s, box-shadow .15s;
  }
  input::placeholder{color:#94a3b8}
  input:focus{
    border-color:rgba(34,211,238,.7);
    box-shadow:0 0 0 3px rgba(34,211,238,.18);
  }

  button{
    padding:12px 16px; border:0; border-radius:10px; cursor:pointer;
    color:#fff; font-weight:800; letter-spacing:.2px;
    background:linear-gradient(135deg, var(--iron-red), var(--iron-red-dark));
    border:1px solid rgba(245,158,11,.6);
    box-shadow:0 6px 14px rgba(185,28,28,.35), inset 0 0 10px rgba(245,158,11,.18);
    transition:transform .08s ease, filter .15s ease, box-shadow .15s ease;
  }
  button:hover{transform:translateY(-1px);filter:brightness(1.05)}
  button:active{transform:translateY(0);filter:brightness(.98)}

  /* Pulsante microfono con glow controllato */
  #talkBtn{
    box-shadow:
      0 0 18px rgba(34,211,238,.28),
      0 0 36px rgba(34,211,238,.18),
      inset 0 0 10px rgba(245,158,11,.22);
  }

  .hint{font-size:12px;opacity:.85;margin-top:8px;color:var(--muted)}
</style>
</head><body>
<div class="app">
  <h1>J.A.R.V.I.S.</h1>
  <div id="log"></div>
  <div class="controls">
    <button id="talkBtn">🎤 Parla porco dio</button>
    <input id="textInput" placeholder="Scrivi qui e premi Invio…" />
  </div>
  <div class="hint">Suggerimenti: "ciao", "come stai", "che ore sono? è ora di Ironman", "esci"</div>
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
