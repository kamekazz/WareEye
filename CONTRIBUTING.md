# Contributing to WareEye

Thanks for checking out **WareEye**! We are building a real-time pallet tracking system and welcome contributions of all kinds. Whether you enjoy polishing dashboards or squeezing every last millisecond out of computer-vision code, there is a place for you here.

## Where We Need the Most Help

| Area | What We’re After | Tech Stack |
|------|-------------------|-----------|
| ✨ **UI / UX** | Improve the Flask-served dashboard (dark Tailwind theme) — better tables, filters, mobile layout, clean design tokens, iconography. | Jinja2 · Tailwind CSS · Vanilla JS (no Bootstrap) |
| 🚀 **Scan Speed / Accuracy** | Swap our basic pyzbar pipeline for something faster and more robust. Ideas welcome: YOLO-v8 barcode head, ZBar OpenCL branch, OpenCV DNN, etc. | Python · OpenCV · (YOLO, ONNX, TensorRT...your pick) |
| 🛠 **Packaging & DevOps** | Docker-compose setup, Raspberry Pi builds, GitHub Actions CI, systemd service templates. | Docker · bash · GitHub Actions |
| 📝 **Docs & Tests** | Better README diagrams, CONTRIBUTING how-tos, unit/integration tests. | Markdown · PyTest |

## Quick Start

```bash
# fork + clone, then:

# --- Server ---
cd Server
pip install -r requirements.txt
python app.py     # localhost:5000

# --- Client ---
cd ../Client
pip install -r requirements.txt
python client.py  # streams webcam / RTSP and posts scans
```

Python 3.12+ is required for both components.

## Coding Conventions

* **Formatter:** [black](https://black.readthedocs.io/) (`black .` before you commit).
* **Linter:** [ruff](https://beta.ruff.rs/) (optional, but recommended).
* **Type hints:** please add them where obvious.
* **Docstrings / comments:** keep them short and practical.

## How to Contribute

1. Fork the repo and create a topic branch (`feat/ui-filter-bar`, `perf/yolo-decoder`, etc.).
2. Commit small, logical chunks.
3. Open a pull request against `main` with:
   - A clear summary of what and why.
   - Screenshots or benchmarks if you touched UI or performance code.
   - Confirmation that `pip install -r requirements.txt` works for both `Server/` and `Client/`.
4. Be ready for friendly code review—together we’ll polish and merge.

## Community

* **Issues** – Any bug, feature idea, or performance tip: open it!
* **Discussions** – Planning big changes? Start the conversation there.
* **Slack / Discord (coming soon)** – Live chat once the project gains steam.

We especially welcome contributors who:

* 💜 Enjoy crafting clean, responsive Tailwind interfaces.
* 🤖 Have experience with YOLO, OpenCV DNN, or GPU acceleration.
* 🐧 Like turning rough scripts into rock-solid Docker images or systemd services.

Come build the warehouse “eye” with us!
