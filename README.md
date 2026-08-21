# HappyMan Inventory

Raw material purchase tracking for HappyMan Sweets (Madurai, India).

Part of the HappyMan suite:
- HappyManPos — point of sale system
- HappyManInventory — this project

## Features

- Track raw material purchases (sugar, cashew, ghee, etc.)
- Manage supplier database
- Manage material catalog
- Bilingual Tamil/English material names
- Excel report generation
- Runs locally on family laptop

## Tech Stack

- Backend: FastAPI + SQLite
- Frontend: Vanilla JavaScript
- Bundling: PyInstaller

## Setup (Development)

```bash
git clone https://github.com/devayani24/happyman-inventory.git
cd happyman-inventory

conda create -n happyman_inventory python=3.10 -y
conda activate happyman_inventory

pip install -r requirements.txt

python -m app.db.setup_db

python run_app.py
```

## Building Executable

```bash
pyinstaller HappyManInventory.spec
```

Output in `dist/HappyManInventory.exe`.

## Related Projects

- [HappyManPos](https://github.com/devayani24/happyman-pos)