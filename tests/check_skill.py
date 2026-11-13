"""Static checks for both skill files. Run: python3 tests/check_skill.py"""
import pathlib, re, subprocess, sys

root = pathlib.Path(__file__).resolve().parent.parent
errors = []

REQUIRED = {
    "SKILL.md": ["ASSESSMENT:", "STATUS: DONE | ESCALATE | CLARIFY", "You cannot change it yourself",
                 "`haiku`", "`sonnet`", "`opus`", "`fable`", "At most two escalations", ".orchestra/"],
    "de/SKILL.md": ["EINSCHÄTZUNG:", "STATUS: FERTIG | ESKALATION | KLÄRUNG", "Du kannst es nicht selbst wechseln",
                    "`haiku`", "`sonnet`", "`opus`", "`fable`", "Höchstens zwei Eskalationen", ".orchestra/"],
}
headings = {}
for rel, needles in REQUIRED.items():
    text = (root / rel).read_text(encoding="utf-8")
    if not re.match(r"---\nname: adaptive-multi-agent\ndescription: Use when .+\n---\n", text):
        errors.append(f"{rel}: frontmatter missing or malformed")
    for n in needles:
        if n not in text:
            errors.append(f"{rel}: required text missing: {n}")
    if len(text.splitlines()) > 200:
        errors.append(f"{rel}: longer than 200 lines")
    if re.search(r"/Users/|/home/|api[_-]?key|password", text, re.I):
        errors.append(f"{rel}: contains a local path or credential word")
    headings[rel] = len(re.findall(r"^## ", text, re.M))
if len(set(headings.values())) != 1:
    errors.append(f"English and German editions differ in section count: {headings}")

# The fixture must fail exactly as planted: 2 of 5 tests pass.
out = subprocess.run([sys.executable, "run_tests.py"], cwd=root / "tests" / "fixture",
                     capture_output=True, text=True).stdout
if "2/5" not in out:
    errors.append("fixture: expected 2/5 passing tests in the untouched fixture")

print("\n".join(errors) if errors else "all checks passed")
sys.exit(1 if errors else 0)
