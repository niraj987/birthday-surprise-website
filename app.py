# app.py
# Complete birthday site: gallery carousel, note, QR generator (segno), scanner, confetti, hearts, music
from flask import Flask, request, send_file, render_template_string, Response
import segno
from io import BytesIO

app = Flask(__name__, static_folder='static')

PAGE = r'''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Baby ji — Happy Birthday 🎂</title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;500;700&display=swap" rel="stylesheet">
<style>
:root{--bg1:#071427;--bg2:#072a3f;--accent:#ff6b6b;--accent2:#ffd166;--muted:#cfe7f3}
*{box-sizing:border-box}html,body{height:100%;margin:0;font-family:Montserrat,system-ui,Arial;background:linear-gradient(180deg,var(--bg1),var(--bg2));color:#eef8ff}
.container{max-width:1100px;margin:24px auto;display:grid;grid-template-columns:1fr 360px;gap:18px;padding:0 16px;align-items:start}
.header{display:flex;gap:12px;align-items:center}.logo{width:56px;height:56px;border-radius:12px;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;font-weight:800;color:#071126}.title h1{margin:0;font-size:20px}.title p{margin:2px 0 0 0;color:var(--muted);font-size:13px}
.card{background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));padding:14px;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,0.6)}.controls{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}.btn{padding:10px 12px;border-radius:10px;border:0;cursor:pointer;font-weight:700;background:linear-gradient(90deg,var(--accent),var(--accent2));color:#071126;text-decoration:none}.btn.secondary{background:#14414f;color:#e6f8ff}
.preview-top{display:flex;gap:12px;align-items:center}#qrPreview{width:140px;height:140px;border-radius:12px;background:#fff;padding:8px;object-fit:contain;border:6px solid rgba(255,255,255,0.02)}.qr-text{color:var(--muted);font-size:14px;max-width:540px}
.carousel{position:relative;margin-top:14px;border-radius:12px;overflow:hidden}.carousel-track{display:flex;transition:transform 0.6s ease}.carousel img{width:100%;height:320px;object-fit:cover;flex:0 0 100%}.carousel-controls{position:absolute;top:50%;left:8px;right:8px;display:flex;justify-content:space-between;transform:translateY(-50%)}.cbtn{background:rgba(0,0,0,0.35);border:0;color:white;padding:8px;border-radius:8px;cursor:pointer}
.note{margin-top:12px;background:linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.01));padding:12px;border-radius:12px;border:1px solid rgba(255,255,255,0.02)}.note h2{margin:0 0 8px 0}.note p{color:var(--muted);line-height:1.5;white-space:pre-wrap}
.hearts{position:fixed;left:0;top:0;right:0;bottom:0;pointer-events:none;z-index:9998}.aside{padding:14px;position:sticky;top:18px}.preview-card{background:linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.01)); padding:14px;border-radius:12px}.preview-card h3{margin:0 0 8px 0}.preview-card p{margin:0;color:var(--muted);white-space:pre-wrap}
@media(max-width:980px){.container{grid-template-columns:1fr}.carousel img{height:220px}.aside{position:static;margin-top:14px}}
.modal{position:fixed;inset:0;background:rgba(0,0,0,0.65);display:flex;align-items:center;justify-content:center;z-index:9999;padding:24px}.modal img{max-width:96vw;max-height:90vh;border-radius:12px;box-shadow:0 30px 60px rgba(0,0,0,0.6)}.hidden{display:none}
#confettiCanvas{position:fixed;pointer-events:none;top:0;left:0;right:0;bottom:0;width:100vw;height:100vh;z-index:9999}
</style>
</head>
<body>
<canvas id="confettiCanvas"></canvas>
<div class="hearts" id="hearts"></div>

<div class="container">
  <div>
    <div class="header">
      <div class="logo">BJ</div>
      <div class="title">
        <h1>Baby ji — Happy Birthday 🎂</h1>
        <p>Click Celebrate to make it magical ✨</p>
      </div>
    </div>

    <div class="card" style="margin-top:12px">
      <div class="preview-top">
        <img id="qrPreview" src="/qr?data=Happy%20Birthday%2C%20Baby%20ji%21&format=svg" alt="QR">
        <div>
          <div class="qr-text" id="qrText">Tip: put <code>/surprise</code> into message to make the QR open the surprise page.</div>
          <div style="margin-top:8px" class="controls">
            <button id="generateBtn" class="btn">Update QR</button>
            <a id="downloadLink" class="btn" href="#" download>Download SVG</a>
            <button id="celebrateBtn" class="btn secondary">Celebrate 🎊</button>
            <a class="btn" href="/memories">Photo Memories</a>
          </div>
        </div>
      </div>

      <div class="carousel" id="carousel">
        <div class="carousel-track" id="track">
          <img src="/static/images/photo1.jpg" alt="p1">
          <img src="/static/images/photo2.jpg" alt="p2">
          <img src="/static/images/photo3.jpg" alt="p3">
        </div>
        <div class="carousel-controls">
          <button id="prevBtn" class="cbtn">◀</button>
          <button id="nextBtn" class="cbtn">▶</button>
        </div>
      </div>

      <div class="note">
        <h2>Baby ji,</h2>
        <p id="noteText">
Baby ji,
Happy Birthday to the most beautiful, caring, and precious person in my life. On your special day, I just want to remind you how much you mean to me. You’re not just my girlfriend — you’re my happiness, my peace, and my favorite blessing.

Thank you for loving me, supporting me, and staying with me even when things aren’t perfect. I know sometimes I make mistakes or say things that may hurt you, and for that, I’m really sorry, baby ji. I never want to be the reason for your tears — only your smile.

Today, I just want you to feel special, loved, and celebrated.
May your year be filled with joy, success, good health, and endless happiness. I promise to stand by your side, love you better every day, and make more beautiful memories with you.

Happy Birthday, baby ji. I love you always. ❤️✨
        </p>
      </div>

      <div style="margin-top:14px">
        <h3 style="margin:0 0 8px 0;color:var(--muted)">Scan a QR (camera)</h3>
        <div id="reader" style="background:#071426;border-radius:10px;min-height:180px;display:flex;align-items:center;justify-content:center;color:var(--muted)">Click start to use camera</div>
        <div style="margin-top:8px;display:flex;gap:8px">
          <button id="startScannerBtn" class="btn secondary">Start Scanner</button>
          <button id="stopScannerBtn" class="btn secondary" disabled>Stop Scanner</button>
        </div>
        <div style="color:var(--muted);margin-top:8px"><strong>Scanned:</strong> <span id="scanResult">—</span></div>
      </div>
    </div>
  </div>

  <aside class="aside">
    <div class="preview-card">
      <h3>To: <span id="previewName">Baby ji</span></h3>
      <p id="previewMessage">Happy Birthday, Baby ji! I love you. Click → /surprise</p>
      <div style="margin-top:12px">
        <label style="color:var(--muted)">Edit message to generate QR:</label>
        <textarea id="messageInput" rows="3" style="width:100%;margin-top:6px;border-radius:8px;padding:8px;background:transparent;border:1px solid rgba(255,255,255,0.04)"></textarea>
        <div style="margin-top:8px;color:var(--muted);font-size:13px">Pro tip: use <code>/surprise</code> to make the QR open the in-app surprise page.</div>
      </div>
    </div>
  </aside>
</div>

<div id="modal" class="modal hidden" onclick="hideModal()">
  <img id="modalImg" src="">
</div>

<!-- audio (will play on Celebrate click) -->
<audio id="bgAudio" src="/static/audio/happy.wav" preload="auto"></audio>

<script src="https://unpkg.com/html5-qrcode@2.3.7/minified/html5-qrcode.min.js"></script>
<script>
// Carousel
const track = document.getElementById('track');
const slides = Array.from(track.children);
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
let index = 0;
function goTo(i){ index = (i + slides.length) % slides.length; track.style.transform = `translateX(-${index*100}%)`; }
nextBtn.addEventListener('click', ()=> goTo(index+1));
prevBtn.addEventListener('click', ()=> goTo(index-1));
let auto = setInterval(()=> goTo(index+1), 3500);
slides.forEach(s => s.addEventListener('click', ()=> { showModal(s.src); }));

// UI elements & QR
const msgInput = document.getElementById('messageInput');
const previewName = document.getElementById('previewName');
const previewMessage = document.getElementById('previewMessage');
const qrPreview = document.getElementById('qrPreview');
const qrText = document.getElementById('qrText');
const downloadLink = document.getElementById('downloadLink');
const genBtn = document.getElementById('generateBtn');
const celebrateBtn = document.getElementById('celebrateBtn');

msgInput.value = '/surprise';
function updateQR(){
  const msg = msgInput.value.trim() || ('Happy Birthday, ' + previewName.textContent + '!');
  previewMessage.textContent = msg;
  const url = '/qr?data=' + encodeURIComponent(msg) + '&format=svg';
  qrPreview.src = url;
  qrText.textContent = 'This QR encodes: ' + msg;
  downloadLink.href = '/download?data=' + encodeURIComponent(msg) + '&format=svg';
}
genBtn.addEventListener('click', updateQR);
updateQR();

// modal
function showModal(src){ document.getElementById('modalImg').src = src; document.getElementById('modal').classList.remove('hidden'); }
function hideModal(){ document.getElementById('modal').classList.add('hidden'); }

// confetti
const confettiCanvas = document.getElementById('confettiCanvas');
const ctx = confettiCanvas.getContext && confettiCanvas.getContext('2d');
function resize(){ confettiCanvas.width = innerWidth; confettiCanvas.height = innerHeight; }
window.addEventListener('resize', resize); resize();
let confetti = [], anim = null;
function spawnConfetti(){ for(let i=0;i<110;i++){ confetti.push({x:Math.random()*innerWidth,y:Math.random()*-innerHeight,s:6+Math.random()*12,sp:2+Math.random()*4,col:['#ff6b6b','#ffd166','#6bcB77','#9be7ff'][Math.floor(Math.random()*4)],r:Math.random()*6}); } if(!anim) anim=requestAnimationFrame(loop); }
function loop(){ ctx.clearRect(0,0,innerWidth,innerHeight); for(let p of confetti){ p.y+=p.sp; p.x+=Math.sin(p.y/30)*1.5; p.r+=0.02; ctx.save(); ctx.translate(p.x,p.y); ctx.rotate(p.r); ctx.fillStyle=p.col; ctx.fillRect(-p.s/2,-p.s/2,p.s,p.s*1.6); ctx.restore(); } confetti = confetti.filter(p=>p.y < innerHeight+50); if(confetti.length>0) anim=requestAnimationFrame(loop); else cancelAnimationFrame(anim),anim=null; }

// hearts
const heartsContainer = document.getElementById('hearts');
function spawnHearts(count=18){ for(let i=0;i<count;i++){ const h = document.createElement('div'); h.innerHTML = '❤'; Object.assign(h.style,{position:'fixed',left:(Math.random()*100)+'%',top:'60%',fontSize:(14+Math.random()*34)+'px',color:['#ff6b6b','#ffd166','#ff9fb1'][Math.floor(Math.random()*3)],opacity:1,transform:'translate(-50%,0)',pointerEvents:'none',transition:'transform 2.4s linear,opacity 2.4s linear'}); heartsContainer.appendChild(h); setTimeout(()=> { h.style.transform = `translate(-50%,-${200+Math.random()*300}px) rotate(${Math.random()*360}deg)`; h.style.opacity = '0'; }, 10); setTimeout(()=> h.remove(), 2600); } }

// music + celebrate
const audio = document.getElementById('bgAudio');
celebrateBtn.addEventListener('click', ()=>{ spawnConfetti(); spawnHearts(20); try{ audio.currentTime = 0; audio.play().catch(()=>{}); }catch(e){} });

// qr scanner
let scanner = null;
const startBtn = document.getElementById('startScannerBtn');
const stopBtn = document.getElementById('stopScannerBtn');
const scanResult = document.getElementById('scanResult');
startBtn.addEventListener('click', async ()=>{ startBtn.disabled = true; stopBtn.disabled = false; scanResult.textContent='Waiting for camera...'; if(!scanner) scanner = new Html5Qrcode('reader'); try{ await scanner.start({facingMode:'environment'},{fps:10,qrbox:250}, decoded=>{ scanResult.textContent = decoded; if(decoded.startsWith('/') && !decoded.startsWith('//')) setTimeout(()=> window.open(window.location.origin + decoded,'_blank'), 300); else if(decoded.startsWith('http')) setTimeout(()=> window.open(decoded,'_blank'), 300); spawnConfetti(); }); }catch(e){ alert('Cannot access camera. Allow permission or close other apps using it.'); startBtn.disabled=false; stopBtn.disabled=true; } });
stopBtn.addEventListener('click', async ()=>{ stopBtn.disabled = true; startBtn.disabled = false; if(scanner){ await scanner.stop().catch(()=>{}); scanner.clear(); scanner = null; } document.getElementById('reader').innerHTML = 'Click start to use camera'; scanResult.textContent = 'Stopped'; });
</script>
</body>
</html>
'''

MEMORIES = r'''
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Photo Memories — Baby ji</title>
<style>body{font-family:Arial,Helvetica,sans-serif;background:#071427;color:#fff;margin:0;padding:24px}.wrap{max-width:900px;margin:0 auto}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}img{width:100%;border-radius:10px} .top{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}button{padding:8px 12px;border-radius:8px;border:0;cursor:pointer}@media(max-width:600px){.grid{grid-template-columns:1fr}}</style></head>
<body>
<div class="wrap">
  <div class="top">
    <h1>Photo Memories</h1>
    <div>
      <button onclick="window.print()">Print / Save as PDF</button>
      <a href="/" style="color:#ffd166;margin-left:10px;text-decoration:none">Back</a>
    </div>
  </div>
  <div class="grid">
    <img src="/static/images/photo1.jpg">
    <img src="/static/images/photo2.jpg">
    <img src="/static/images/photo3.jpg">
    <img src="/static/images/photo1.jpg">
  </div>
  <p style="color:#cfe8ff;margin-top:12px">Tip: choose "Save as PDF" in the print dialog to create a printable PDF card.</p>
</div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(PAGE)

@app.route('/memories')
def memories():
    return render_template_string(MEMORIES)

@app.route('/qr')
def qr():
    data = request.args.get('data', ' ')
    qr = segno.make(data, micro=False)
    out = BytesIO()
    qr.save(out, kind='svg', xmldecl=False)
    out.seek(0)
    return Response(out.getvalue(), mimetype='image/svg+xml')

@app.route('/download')
def download():
    data = request.args.get('data', ' ')
    qr = segno.make(data, micro=False)
    out = BytesIO()
    qr.save(out, kind='svg', xmldecl=False)
    out.seek(0)
    return send_file(out, mimetype='image/svg+xml', as_attachment=True, download_name='birthday-qr.svg')

@app.route('/surprise')
def surprise():
    return '''
    <html><body style="background:linear-gradient(180deg,#081224,#0b2a40);color:#fff;font-family:Arial;text-align:center;padding:80px">
    <h1 style="font-size:34px;margin-bottom:6px">🎁 Surprise — Happy Birthday, Baby ji!</h1>
    <p style="color:#cfe8ff;font-size:18px;max-width:760px;margin:10px auto 20px auto">I made this just for you. Thank you for being my happiness and my favorite blessing. ❤️</p>
    <div style="margin-top:18px"><a href="/" style="color:#ffd166;text-decoration:underline">Back</a></div>
    </body></html>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
