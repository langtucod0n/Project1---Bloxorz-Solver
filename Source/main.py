"""Khởi động máy chủ Bloxorz và mở trình duyệt: python main.py [--port 8000] [--no-browser]"""
import argparse
import socket
import sys
import threading
import webbrowser

import uvicorn


def port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def main() -> int:
    # Console Windows mặc định không in được tiếng Việt (cp1252)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Bloxorz Solver")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true", help="không tự mở trình duyệt")
    args = parser.parse_args()

    if port_in_use(args.host, args.port):
        print(f"Cổng {args.port} đang bị chiếm. Chạy lại với cổng khác: python main.py --port {args.port + 1}")
        return 1

    url = f"http://{args.host}:{args.port}/"
    if not args.no_browser:
        threading.Timer(1.0, webbrowser.open, args=(url,)).start()
    print(f"Máy chủ chạy tại {url}  (tài liệu API: {url}docs)")
    uvicorn.run("server.app:app", host=args.host, port=args.port, log_level="info")
    return 0


if __name__ == "__main__":
    sys.exit(main())
