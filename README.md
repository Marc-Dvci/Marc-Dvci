# Marc Donovici

AI implementation lead for Group Internal Audit at Crédit Mutuel Alliance Fédérale in Strasbourg.
I take generative AI from a business problem to production: six solutions shipped to a
500-person function, with 80%+ regular usage. Outside work I build offline, multimodal and
agentic systems in AI competitions, always solo.

[LinkedIn](https://linkedin.com/in/marc-donovici)

## Results

| Result | Competition | Project |
|---|---|---|
| **3rd of 850+ teams** | Google MedGemma Impact Challenge 2026 | [FieldScreen AI](https://github.com/Marc-Dvci/FieldScreen_AI) · [writeup](https://www.kaggle.com/competitions/med-gemma-impact-challenge/writeups/fieldscreen-ai) · [Google blog](https://blog.google/innovation-and-ai/technology/health/med-gemma-impact-challenge/) |
| **Winner, EdgeAgent track** | Global AI Hackathon with Qwen Cloud (Alibaba Cloud) | [LUMEN](https://github.com/Marc-Dvci/LUMEN) · [demo](https://youtu.be/h8hPsUjZMuU) |
| **Finalist, 1 of 6** | European Patent Office CodeFest 2026 | IP Value Framework |
| **2nd place, Pro category** | Euro-Information Concours de Code 2025 (Python, C++) | |

## Selected projects

**Offline healthcare AI**
- [FieldScreen AI](https://github.com/Marc-Dvci/FieldScreen_AI): tuberculosis screening for community
  health workers with no network. Fine-tuned MedGemma on chest X-rays, cough audio classification,
  voice intake and output in 15 languages, on one laptop.
- [LUMEN](https://github.com/Marc-Dvci/LUMEN): neonatal danger-sign screening on the WHO IMNCI protocol.
  Runs on Qwen Cloud and falls back to a fine-tuned on-device model when the connection drops.
  [Android app](https://github.com/Marc-Dvci/LUMEN-Mobile).

**Governed agents for regulated work**
- [AssuranceOS](https://github.com/Marc-Dvci/AssuranceOS): an internal-audit platform run by 19 governed
  agents on Gemini. Signed releases, a default-deny tool gateway and evidence validation.
- [Lore](https://github.com/Marc-Dvci/Lore): a permission and lineage control plane for archival media
  on ClickHouse. Every query family answers in under 33 ms at p99 on 300M rows.
- [Threshold](https://github.com/Marc-Dvci/Threshold): several care organisations answer one person's
  AI assistant through WebMCP and compose a single plan.
 [Video](https://youtu.be/J_AyAdoT05I)

**Performance and systems**
- [fastpath64](https://github.com/Marc-Dvci/fastpath64): an Arm `smmla` kernel for IQ4_XS in llama.cpp.
  Prefill goes from 0.58x to 1.24x of Q4_K on Neoverse N2.
- [decimal-rs](https://github.com/Marc-Dvci/decimal-rs): decimal.js ported to Rust. The original test
  suite runs unmodified against the Rust build.
- [Vitrify](https://github.com/Marc-Dvci/Vitrify): inverse design of organ nanowarming as one
  differentiable function across JAX and FEniCSx.

## Stack
Python · TypeScript · Java · Rust · C · FastAPI · React · Google ADK · AWS Strands · MCP ·
Vertex AI · Cloud Run · AWS CDK · Alibaba Function Compute · ClickHouse · Docker · pytest · Playwright
