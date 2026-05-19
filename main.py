#!/usr/bin/env python3
"""ScreenLingo — real-time screen translation with vocabulary learning."""

from screenlingo.bootstrap import init_app

if __name__ == "__main__":
    init_app()
    from screenlingo.app import run

    run()
