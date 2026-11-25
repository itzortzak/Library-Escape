from pathlib import Path
import hashlib, re, json, csv, subprocess, tempfile, shutil
root = Path(__file__).resolve().parents[1]
data = b"".join(p.read_bytes() for p in sorted((root / "source").glob("part-*.txt")))
assert hashlib.sha256(data).hexdigest() == (root / "SHA256SUMS").read_text().split()[0]
html = data.decode("utf-8")
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
for name in ["README.txt", "CHANGELOG.md", "VERSION", "VALIDATION.txt"]:
    shutil.copyfile(root / name, dist / name)
(dist / "SHA256SUMS").write_text(hashlib.sha256(data).hexdigest() + "  index.html\n")
with (dist / "catalogue.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["ID","Θεματική","Ενδεικτικό επίπεδο","Ερώτηση","Ορθή απάντηση","Αιτιολόγηση","Πηγή"])
    for room in bank:
        for q in room:
            w.writerow([q["id"],q["room"]+1,q["level"],q["prompt"],q["correct"],q["why"],q["source"]])
print("Validated SHA-256, JavaScript, 240 questions and 10 rooms.")
