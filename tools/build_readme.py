"""Regenerate the profile assets and the network block in README.md.

    python tools/build_readme.py

Rebuilds assets/results.svg and replaces everything between the network markers
with a fresh Mermaid block. Refresh tools/descriptions.json first when repo
descriptions change:  gh repo list Marc-Dvci --limit 200 --visibility public --json name,description
"""
import re, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import build_carousel, build_network

ROOT = HERE.parent
readme = ROOT / "README.md"
(ROOT / "assets").mkdir(exist_ok=True)
(ROOT / "assets" / "results.svg").write_text(build_carousel.svg(), encoding="utf-8")

block = "```mermaid\n" + build_network.mermaid() + "```"
assert len(block) < 50_000, f"Mermaid block is {len(block)} chars; GitHub's limit is 50,000"
text = readme.read_text(encoding="utf-8")
new, n = re.subn(r"<!-- network:start -->.*?<!-- network:end -->",
                 lambda _: f"<!-- network:start -->\n{block}\n<!-- network:end -->", text, flags=re.S)
assert n == 1, "network markers not found"
readme.write_text(new, encoding="utf-8")
print(f"README.md updated: network block {len(block):,} chars")
