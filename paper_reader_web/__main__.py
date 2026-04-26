from __future__ import annotations

import argparse

import uvicorn

from .config import DEFAULT_HOST, DEFAULT_PORT


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local Paper Reader web workbench")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", default=DEFAULT_PORT, type=int)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()
    uvicorn.run("paper_reader_web.main:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
