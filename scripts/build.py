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
