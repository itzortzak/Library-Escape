"""Build a separate non-public v3 preview, retaining the existing game engine."""
from pathlib import Path
import csv
import hashlib
import json
import re
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
bankdir = root / "question-bank-v3"
subprocess.run([sys.executable, str(root / "scripts/build.py")], check=True)
subprocess.run(["node", str(bankdir / "validate-drafts.mjs")], check=True)
catalogue = json.loads((bankdir / "anthology-coverage.json").read_text(encoding="utf-8"))["entries"]
by_id = {e["id"]: e for e in catalogue}
by_title = {e.get("legacyBankTitle", e["work"]): e for e in catalogue}
# Prior first editorial passes (not independent approval); later batches require explicit additions.
reviewed_files = {f"bank-draft-{i:02d}.json" for i in range(1, 19)} | {"theory-draft-01.json", "theory-draft-02.json"}
questions = []
for p in sorted(bankdir.glob("*-draft-*.json")):
    if not re.fullmatch(r"(bank|comparative|theory)-draft-\d+\.json", p.name):
        continue
    for q in json.loads(p.read_text(encoding="utf-8"))["questions"]:
        q = dict(q)
        if q.get("category") == "theory":
            periods = ["Θεωρία λογοτεχνίας"]
        elif q.get("category") == "comparative":
            periods = list(dict.fromkeys(by_id[e]["period"] for e in q["comparisonEntryIds"]))
        else:
            e = by_id[q["entryId"]] if q.get("entryId") else by_title[q["work"]]
            periods = [e["period"]]
        q.update(periods=periods, reviewed=p.name in reviewed_files)
        questions.append(q)
assert len(questions) == 1350
assert len({q["id"] for q in questions}) == 1350
assert sum(q["reviewed"] for q in questions) == 1090
html = (root / "dist/index.html").read_text(encoding="utf-8")
def replace_once(old, new):
    global html
    if html.count(old) != 1:
        raise RuntimeError(f"Expected unique patch anchor: {old[:100]!r}, got {html.count(old)}")
    html = html.replace(old, new, 1)

# Keep preview save data isolated from the production game.
replace_once("STORE='literary-room-v105-progress'", "STORE='literary-room-v3-preview-progress'")
replace_once("BANKSTORE='literary-room-v10-bank'", "BANKSTORE='literary-room-v3-preview-legacy-disabled'")
replace_once("LEVELSTORE='literary-room-v10-levels'", "LEVELSTORE='literary-room-v3-preview-levels'")
# Replace only the room question selection step, not movement, puzzles or scoring.
start = html.index("function start(){let rows=available();")
a = html.index("let rooms=rows.map(", start)
b = html.index("let teams=", a)
html = html[:a] + "let rooms=selectV3Rooms(rows,level);" + html[b:]
payload = json.dumps(questions, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
runtime = (root / "scripts/v3-preview-runtime.js").read_text(encoding="utf-8")
replace_once("menu();requestAnimationFrame(frame);", "const V3_DATA="+payload+";\n"+runtime+"\nmenu();requestAnimationFrame(frame);")
scripts = re.findall(r"<script[^>]*>(.*?)</script>", html, re.S)
assert len(scripts) == 3
with tempfile.TemporaryDirectory() as td:
    for i, script in enumerate(scripts):
        path = Path(td) / f"script-{i}.js"
        path.write_text(script, encoding="utf-8")
        subprocess.run(["node", "--check", str(path)], check=True)
out = root / "dist-v3"
out.mkdir(exist_ok=True)
data = html.encode("utf-8")
(out / "index.html").write_bytes(data)
(out / ".nojekyll").touch()
(out / "VERSION").write_text("3.0.0-preview.7\n", encoding="utf-8")
(out / "SHA256SUMS").write_text(hashlib.sha256(data).hexdigest()+"  index.html\n", encoding="utf-8")
(out / "PREVIEW.txt").write_text("Δοκιμαστική έκδοση. 1090 ερωτήσεις πρώτης επιμέλειας, 260 προς αναλυτική επαλήθευση. Όχι οριστική δημοσίευση. Τα σχολικά χωρία παραπέμπονται με συνδέσμους, δεν αναπαράγονται αυτούσια.\n", encoding="utf-8")
with (out / "catalogue.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["ID","Έργο","Συγγραφέας","Αίθουσα","Δυσκολία","Πρώτη επιμέλεια","Ερώτηση","Σωστή απάντηση","Αιτιολόγηση","Πηγή","Χωρίο"])
    def cell(v):
        v = str(v if v is not None else "")
        return "'" + v if v.startswith(("=", "+", "-", "@")) else v
    for q in questions:
        w.writerow([cell(v) for v in [q["id"],q["work"],q["author"],q["room"]+1,q["level"],"Ναι" if q["reviewed"] else "Όχι",q["prompt"],q["correct"],q["why"],q["sourceUrl"],q["sourceLocator"]]])
print("Built separate v3 preview with 1350 questions, default 1090 first-reviewed.")
