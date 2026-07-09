from __future__ import annotations

import sys

from .bootstrap import build_app_context, load_app_config
from .ui.main_window import VedaApp


def main() -> None:
    config = load_app_config()
    context = build_app_context(config)
    app = VedaApp(context)
    exit_code = app.run()
    if context.database:
        context.database.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
