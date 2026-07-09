# VEDA AI

VEDA AI is a premium desktop assistant built with Python and PySide6. The project is structured for modular growth and includes a command engine, UI shell, and extension points for voice, automation, memory, browser, email, scheduling, and AI integrations.

## Quick Start

1. Create a virtual environment.
2. Install dependencies: pip install -r requirements.txt
3. Run the app: python -m src.veda_ai.app

## Architecture

- src/veda_ai/core: command classification and orchestration
- src/veda_ai/ui: PySide6 interface modules
- src/veda_ai/voice: voice capture and speech synthesis
- src/veda_ai/automation: desktop automation helpers
- src/veda_ai/ai: AI provider integrations
- src/veda_ai/database: SQLite persistence
- src/veda_ai/config: environment configuration
