from pathlib import Path
import hashlib, re, json, csv, subprocess, tempfile, shutil
root = Path(__file__).resolve().parents[1]
parts = sorted((root / "source").glob("part-*.txt"))
assert len(parts) == 22
data = b"".join(p.read_bytes() for p in parts)
assert hashlib.sha256(data).hexdigest() == (root / "SHA256SUMS").read_text().split()[0]
html = data.decode("utf-8")
# Apply the presentation-only revision after verifying the original source archive.
def replace_once(old, new):
    global html
    assert html.count(old) == 1, old[:100]
    html = html.replace(old, new, 1)

start = html.index('<div class="notice">${esc(importNote||', html.index('function menu()'))
end = html.index('<label>Συλλογή κειμένων</label>', start)
html = html[:start] + html[end:]
start = html.index("$('resume').disabled=", html.index('function menu()'))
end = html.index("['collection','period','author']", start)
html = html[:start] + html[end:]
start = html.index('<details class="panel"><summary>Πηγές και πληροφορίες έκδοσης</summary>')
end = html.index('</details>', start) + len('</details>')
html = html[:start] + """<details class="panel"><summary>Βιβλιογραφία και πηγές</summary><h3>Σχολικά εγχειρίδια</h3><p>Γρηγοριάδης, Ν., Καρβέλης, Δ., Μηλιώνης, Χ., Μπαλάσκας, Κ., Παγανός, Γ., &amp; Παπακώστας, Γ. (χ.χ.). <em>Κείμενα νεοελληνικής λογοτεχνίας: Α΄ τεύχος, Α΄ τάξη Γενικού Λυκείου.</em> ΙΤΥΕ «Διόφαντος». ISBN 978-960-06-2316-1. <a href="https://ebooks.edu.gr/" target="_blank" rel="noopener">Ψηφιακά σχολικά βιβλία</a>.</p><p>Παρίσης, Ι., &amp; Παρίσης, Ν. (χ.χ.). <em>Λεξικό λογοτεχνικών όρων.</em> ΙΤΥΕ «Διόφαντος». ISBN 978-960-06-2329-1.</p><h3>Θεσμικό και διδακτικό πλαίσιο</h3><p>Ινστιτούτο Εκπαιδευτικής Πολιτικής. (2015). <em>Πρόγραμμα σπουδών: Λογοτεχνία (τάξεις Α΄, Β΄, Γ΄), Γενικό Λύκειο</em> (σσ. 5–7).</p><p><em>Οδηγίες διδασκαλίας για τη Νεοελληνική Γλώσσα και Λογοτεχνία Α΄ και Β΄ τάξης Γενικού Λυκείου για το σχολικό έτος 2026–2027</em> (σσ. 4–5).</p><p>Οι παραπομπές των γρίφων ακολουθούν την έντυπη σελιδαρίθμηση του ανθολογίου. Οι ανοικτές απαντήσεις αξιολογούνται από τον εκπαιδευτικό. Οι αποθηκεύσεις γίνονται στη συσκευή. Τα δικαιώματα των κειμένων, μεταφράσεων και εικόνων υπόκεινται σε χωριστό έλεγχο.</p></details>""" + html[end:]
replace_once('Το μυστήριο του χαμένου χειρογράφου · v1.0 · Νέα αυτοτελής έκδοση', 'Το μυστήριο του χαμένου χειρογράφου · v1.0.1')
# Improve floor navigation without changing the question bank.
replace_once("const upperRooms=[0,5,9],stairs=[2.5,12.5];", "const upperRooms=[0,5,9],stairs=[9.5,12.5];")
start = html.index("// Upper decorative gallery")
end = html.index("\n}", start)
html = html[:start] + """// Illuminated stair portal on the central aisle, close to the entrance.
if([0,5,9].includes(l.r)){let x=9.5,z=12.5;for(let j=0;j<5;j++)m.box(x,0,z+.45-j*.20,1.35,.12*(j+1),.20,stone);for(let sign of [-1,1]){m.box(x+sign*.78,0,z,.12,2.65,.18,'#b99add',.85);m.box(x+sign*.78,0,z-.52,.12,1.15,.12,'#b99add',.6)}m.box(x,2.65,z,1.7,.17,.22,'#b99add',1);m.box(x,2.35,z,1.15,.25,.12,'#e2c4ff',1);m.box(x,.015,z+.65,1.8,.025,.18,'#b99add',1);}
""" + html[end:]
replace_once("if(Math.hypot(cam.x-stairs[0],cam.z-stairs[1])>2){hintUntil=performance.now()+5000;$('tip').textContent='Η κλίμακα βρίσκεται στον δυτικό διάδρομο, κοντά στην είσοδο.';return}", "")
replace_once("if(!force&&!near()){", "if(!force&&s.floor!==s.targetFloor&&Math.hypot(cam.x-stairs[0],cam.z-stairs[1])<2.4){switchFloor();return}if(!force&&!near()){")
replace_once("if(drag&&!drag.m&&near()){", "if(drag&&!drag.m&&s&&!modal&&s.floor!==s.targetFloor&&Math.hypot(cam.x-stairs[0],cam.z-stairs[1])<2.4){let p=renderer.project(cam,stairs[0],1.8,stairs[1]),b=view.getBoundingClientRect(),x=(e.clientX-b.left)*view.width/b.width,y=(e.clientY-b.top)*view.height/b.height;if(p&&Math.abs(p.x-x)<Math.max(40,view.height*.65/p.d)&&Math.abs(p.y-y)<Math.max(40,view.height/p.d)){switchFloor();drag=null;return}}if(drag&&!drag.m&&near()){")
replace_once("c.fillRect(ox+stairs[0]*sz-2,oy+stairs[1]*sz-2,4,4)", "c.fillRect(ox+stairs[0]*sz-4,oy+stairs[1]*sz-4,8,8);c.fillStyle='#fff';c.font='bold 9px sans-serif';c.fillText(s?.floor?'↓':'↑',ox+stairs[0]*sz+5,oy+stairs[1]*sz+3)")
replace_once("hintUntil>performance.now()&&s.floor!==s.targetFloor?'Το στοιχείο βρίσκεται '+(s.targetFloor?'στον άνω όροφο':'στο ισόγειο')+'. Η κλίμακα σημειώνεται μωβ στον χάρτη.'", "s.floor!==s.targetFloor?'Ο επόμενος γρίφος βρίσκεται '+(s.targetFloor?'στον άνω όροφο':'στο ισόγειο')+'. Πάτησε το κουμπί αλλαγής ορόφου ή πλησίασε τη φωτεινή μωβ κλίμακα και πάτησε E.'")
replace_once("$('floorBtn').textContent=s.floor?'Κλίμακα · ισόγειο':'Κλίμακα · άνω όροφος';", "$('floorBtn').textContent=s.floor?'↓ Μετάβαση στο ισόγειο':'↑ Μετάβαση στον άνω όροφο';$('floorBtn').classList.toggle('primary',s.floor!==s.targetFloor);")
replace_once("Το μυστήριο του χαμένου χειρογράφου · v1.0.1", "Το μυστήριο του χαμένου χειρογράφου · v1.0.2")
# Make bibliography accessible both in the menu and during play.
replace_once('<button id="dictBtn">Λεξικό</button>', '<button id="dictBtn">Λεξικό</button><button id="bibBtn">Βιβλιογραφία</button>')
replace_once('<summary>Βιβλιογραφία και πηγές</summary>', '<summary>Βιβλιογραφία και πηγές</summary><div id="bibContent">')
start = html.index('</details>', html.index('id="bibContent"'))
html = html[:start] + '</div>' + html[start:]
replace_once("<label>Συλλογή κειμένων</label><select id=", "${button('menuBib','Βιβλιογραφία και πηγές')}<label>Συλλογή κειμένων</label><select id=")
replace_once("['collection','period','author'].forEach", "$('menuBib').onclick=()=>bibliography(menu);['collection','period','author'].forEach")
replace_once("function dict(){", "function bibliography(back=hide){show('Βιβλιογραφία και πηγές',$('bibContent').innerHTML+button('bibBack','Επιστροφή','primary'));$('bibBack').onclick=back}function dict(){")
replace_once("$('dictBtn').onclick=dict;", "$('dictBtn').onclick=dict;$('bibBtn').onclick=()=>bibliography(modal?menu:hide);")
replace_once("Το μυστήριο του χαμένου χειρογράφου · v1.0.2", "Το μυστήριο του χαμένου χειρογράφου · v1.0.3")
# Larger rooms, wider bookcases, full-height stair and persistent target marker.
replace_once("const W=19,H=15;const startPos=[9.5,13.5],gatePos=[9.5,1.4];", "const W=23,H=19;const startPos=[11.5,17.5],gatePos=[11.5,1.4];")
start = html.index("function makeLayout(")
end = html.index("function isClear(", start)
html = html[:start] + """function makeLayout(r,floor=0){let variant=r+floor*4;let map=Array.from({length:H},(_,z)=>Array.from({length:W},(_,x)=>x===0||z===0||x===W-1||z===H-1?1:0));for(let z of [4,5,6,10,11,12])for(let x of [2,3,7,8,14,15,19,20]){if((variant+z+Math.floor(x/2))%9!==0)map[z][x]=2}if(variant%3===1)for(let x of [4,5,6,16,17,18])map[8][x]=2;if(variant%3===2)for(let x of [4,5,6,16,17,18])map[14][x]=2;if(variant%2===1)for(let x of [4,5,17,18])map[2][x]=2;const spots=[];for(let z=2;z<H-2;z++)for(let x=2;x<W-2;x++)if(!map[z][x]&&Math.abs(x-11)>2&&(map[z][x-1]===2||map[z][x+1]===2))spots.push([x+.5,z+.5]);return {map,spots,r,floor};}
""" + html[end:]
start = html.index("function decor(")
end = html.index("class Renderer", start)
d = html[start:end]
d = d.replace("9.5","11.5").replace("8.34,10.66","10.34,12.66").replace("17.65","21.65").replace("4.5,11.5,14.5","4.5,11.5,18.5").replace("4.5,14.5","4.5,18.5").replace("3.5,6.5,12.5,15.5","3.5,7.5,15.5,19.5")
# Open a real ceiling aperture above the flight and its landing.
d = d.replace("m.box(X,3.45,Z,.995,.05,.995,(x+z)%2?'#544d40':'#625b48');", "if(!([0,5,9].includes(l.r)&&x>=10&&x<=12&&z>=11&&z<=16))m.box(X,3.45,Z,.995,.05,.995,(x+z)%2?'#544d40':'#625b48');")
a = d.index("// Illuminated stair portal")
b = d.index("\n}", a)
d = d[:a] + """// Full-height stair flight with landing, balustrade and upper doorway.
if([0,5,9].includes(l.r)){let x=11.5,z=16.5;for(let j=0;j<18;j++){let h=(j+1)*.192,zz=z-j*.25;m.box(x,0,zz,1.85,h,.25,stone);m.box(x,h-.045,zz,1.95,.045,.27,'#b79a70');if(j%3===0)for(let sign of [-1,1])m.box(x+sign*.92,h,zz,.065,.95,.065,'#b99add',.35);}for(let sign of [-1,1]){for(let j=0;j<18;j++)m.box(x+sign*.92,1.0+(j+1)*.192,z-j*.25,.09,.12,.29,'#b99add',.55);m.box(x+sign*1.05,3.45,11.5,.15,2.25,.18,'#b99add',.7);}m.box(x,3.40,11.5,2.35,.15,1.1,stone);m.box(x,5.65,11.5,2.25,.18,.22,'#b99add',.8);m.box(x,3.55,11.08,1.65,2.05,.12,'#4d3c58',.25);m.box(x,.02,17.0,2.1,.04,.22,'#b99add',1);}
""" + d[b:]
html = html[:start] + d + html[end:]
replace_once("const upperRooms=[0,5,9],stairs=[9.5,12.5];", "const upperRooms=[0,5,9],stairs=[11.5,16.5];")
replace_once("wx>8.3&&wx<10.7?(Math.abs(wx-9.5)>1.12", "wx>10.3&&wx<12.7?(Math.abs(wx-11.5)>1.12")
start = html.index("if(target&&s?.floor===s?.targetFloor&&hintUntil>performance.now())", html.index("function drawMap()"))
end = html.index("\nfunction move(", start)
html = html[:start] + """if(target&&s?.floor===s?.targetFloor&&!s?.done){let tx=ox+target[0]*sz,tz=oy+target[1]*sz;c.beginPath();c.arc(tx,tz,4.5,0,Math.PI*2);c.fillStyle='#ffd34f';c.fill();c.lineWidth=1.3;c.strokeStyle='#fff3b0';c.stroke();c.lineWidth=1}}""" + html[end:]
replace_once('<canvas id="map" width="135" height="110" aria-label="Μικρός χάρτης"></canvas>', '<canvas id="map" width="190" height="150" aria-label="Χάρτης ορόφου: χρυσή κουκκίδα βιβλίο, λευκή παίκτης, μωβ κλίμακα"></canvas>')
replace_once('width:135px;height:110px;', 'width:190px;height:150px;')
replace_once('max-width:calc(100% - 165px)', 'max-width:calc(100% - 220px)')
replace_once('width:95px;height:78px;', 'width:125px;height:100px;')
replace_once('max-width:calc(100% - 110px)', 'max-width:calc(100% - 145px)')
replace_once('κλικ στο φωτεινό αντικείμενο ή E.</small>', 'κλικ στο φωτεινό αντικείμενο ή E. Χάρτης: χρυσή κουκκίδα = βιβλίο ή θύρα στον ίδιο όροφο · λευκή = παίκτης · μωβ = κλίμακα.</small>')
replace_once("Το μυστήριο του χαμένου χειρογράφου · v1.0.3", "Το μυστήριο του χαμένου χειρογράφου · v1.0.4")
# Navigation and rendering improvements: retain room dimensions and double-width cases.
start = html.index("function makeLayout(")
end = html.index("function isClear(", start)
html = html[:start] + """function makeLayout(r,floor=0){let variant=r+floor*4;let map=Array.from({length:H},(_,z)=>Array.from({length:W},(_,x)=>x===0||z===0||x===W-1||z===H-1?1:0));for(let z of [4,5,6,10,11,12])for(let x of [2,3,7,8,14,15,19,20]){if((variant+Math.floor(z/3)+Math.floor(x/2))%9!==0)map[z][x]=2}if(variant%3===1)for(let x of [4,5,17,18])map[8][x]=2;if(variant%3===2)for(let x of [4,5,17,18])map[14][x]=2;const spots=[];for(let z=2;z<H-2;z++)for(let x=2;x<W-2;x++)if(!map[z][x]&&Math.abs(x-11)>2&&(map[z][x-1]===2||map[z][x+1]===2))spots.push([x+.5,z+.5]);return {map,spots,r,floor};}
""" + html[end:]
# Keep the staircase to the east, clear of the central aisle and book locations.
replace_once("stairs=[11.5,16.5]", "stairs=[17.5,16.5]")
replace_once("let x=11.5,z=16.5;for(let j=0;j<18;j++)", "let x=17.5,z=16.5;for(let j=0;j<18;j++)")
replace_once("x>=10&&x<=12&&z>=11&&z<=16", "x>=16&&x<=18&&z>=11&&z<=16")
# Exclude the staircase footprint and preserve a reachable approach.
replace_once("const spots=[];for(let z=2;z<H-2;z++)", "if([0,5,9].includes(r)){for(let z=11;z<=16;z++)for(let x=16;x<=18;x++)map[z][x]=0;for(let z=12;z<=15;z++)for(let x=17;x<=18;x++)map[z][x]=3;}const spots=[];for(let z=2;z<H-2;z++)")
replace_once("cam={x:stairs[0],z:stairs[1],a:-Math.PI/2}", "cam={x:stairs[0],z:17.5,a:-Math.PI/2}")
# Keep shelf appearance, omit hidden interior faces and tiny labels to lower triangle count.
replace_once("for(let k=0;k<7;k++)", "for(let k=0;k<6;k++)")
replace_once("x-.34+k*.112", "x-.33+k*.132")
replace_once(".092,bh,.25", ".114,bh,.25")
replace_once("m.box(bx,y+.13,bz+sign*.128,.073,.025,.009,'#c6a26a');", "")
# Frame-rate independent movement with swept substeps and wall sliding.
start = html.index("function move(")
end = html.index("function frame(", start)
html = html[:start] + """function move(d,dt){if(!s||s.done||modal||opening)return;if(d==='left')cam.a-=dt*2.15;else if(d==='right')cam.a+=dt*2.15;else{let k=dt*3.72*(d==='back'||d==='strafeL'?-1:1),angle=cam.a+(d.startsWith('strafe')?Math.PI/2:0),steps=Math.max(1,Math.ceil(Math.abs(k)/.10));for(let i=0;i<steps;i++){let x=cam.x+Math.cos(angle)*k/steps,z=cam.z+Math.sin(angle)*k/steps;if(isClear(layout,x,cam.z,.18))cam.x=x;if(isClear(layout,cam.x,z,.18))cam.z=z}if(performance.now()-lastStep>450){tone(82,.08,'triangle',.027);lastStep=performance.now()}}}
""" + html[end:]
replace_once("Math.min(.05,(t-last)/1000||0)", "Math.min(.12,(t-last)/1000||0)")
# Avoid rendering static geometry repeatedly while the player is idle.
replace_once("if(!modal||!frame.drawn){renderer.draw", "let stamp=[cam.x,cam.z,cam.a,s?.floor,s?.targetFloor,target?.join(','),s?.lantern,isGate(),layout.r].join('|');if((!modal&&(stamp!==frame.stamp||opening||t-(frame.paint||0)>100))||!frame.drawn){frame.stamp=stamp;frame.paint=t;renderer.draw")
replace_once("const objects=[[3.5,1.7],[15.5,1.7],[3.5,12.5],[15.5,12.5],[9.5,3],[9.5,7],[9.5,11]]", "const objects=[[3.5,1.7],[19.5,1.7],[3.5,15.5],[19.5,15.5],[11.5,3],[11.5,7],[11.5,11]]")
replace_once("const STORE='literary-room-v10-progress'", "const STORE='literary-room-v105-progress'")
replace_once("Το μυστήριο του χαμένου χειρογράφου · v1.0.4", "Το μυστήριο του χαμένου χειρογράφου · v1.0.5")
data = html.encode("utf-8")
scripts = re.findall(r"<script[^>]*>(.*?)</script>", html, re.S)
assert len(scripts) == 3
with tempfile.TemporaryDirectory() as td:
    for i, script in enumerate(scripts):
        path = Path(td) / f"script-{i}.js"
        path.write_text(script, encoding="utf-8")
        subprocess.run(["node", "--check", str(path)], check=True)
bank, _ = json.JSONDecoder().raw_decode(scripts[0].split("const BASE_BANK=", 1)[1].lstrip())
assert len(bank) == 10 and all(len(room) == 24 for room in bank)
assert len({q["id"] for room in bank for q in room}) == 240
for room in bank:
    assert sorted(q["level"] for q in room) == [1]*8 + [2]*8 + [3]*8
    for q in room:
        assert q["source"] and q["correct"] in q["options"]
dist = root / "dist"
dist.mkdir(exist_ok=True)
(dist / "index.html").write_bytes(data)
(dist / ".nojekyll").touch()
for name in ["README.txt", "CHANGELOG.md", "VERSION"]:
    shutil.copyfile(root / name, dist / name)
(dist / "SHA256SUMS").write_text(hashlib.sha256(data).hexdigest() + "  index.html\n")
with (dist / "catalogue.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["ID","Θεματική","Ενδεικτικό επίπεδο","Ερώτηση","Ορθή απάντηση","Αιτιολόγηση","Πηγή"])
    for room in bank:
        for q in room:
            w.writerow([q["id"],q["room"]+1,q["level"],q["prompt"],q["correct"],q["why"],q["source"]])
print("Validated SHA-256, JavaScript, 240 questions and 10 rooms.")
