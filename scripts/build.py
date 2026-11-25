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
