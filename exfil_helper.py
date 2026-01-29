from http.server import HTTPServer, BaseHTTPRequestHandler
import base64
import urllib.parse
import html
import sys
import signal


def print_help(arg: str):
    print(f"""HTTP server with configurable data decoding

Usage: python {arg} [-p PORT] [-<decoders>]

Options:
  -p PORT    Port to listen on (default: 4000)
  -h         Show this help message

Decoder flags (applied in order specified):
  0  Hex decode
  b  Base64 decode
  u  URL decode
  H  HTML entity decode

Examples:
  python {arg}              # No decoding (plaintext)
  python {arg} -b           # Base64 decode
  python {arg} -bH          # Base64 decode, then HTML decode
  python {arg} -0bu         # Hex decode, Base64 decode, URL decode
  python {arg} -p 8080 -b   # Custom port with Base64 decode
""")


def hex_decode(data: bytes) -> bytes:
    text = data.decode("utf-8", errors="replace").replace(" ", "").replace("\n", "")
    return bytes.fromhex(text)


def base64_decode(data: bytes) -> bytes:
    text = data.decode("utf-8", errors="replace")
    padding = 4 - (len(text) % 4)
    if padding != 4:
        text += "=" * padding
    return base64.b64decode(text)


def url_decode(data: bytes) -> bytes:
    text = data.decode("utf-8", errors="replace")
    return urllib.parse.unquote(text).encode("utf-8")


def html_decode(data: bytes) -> bytes:
    text = data.decode("utf-8", errors="replace")
    return html.unescape(text).encode("utf-8")


DECODERS = {
    "0": ("Hex", hex_decode),
    "b": ("Base64", base64_decode),
    "u": ("URL", url_decode),
    "H": ("HTML", html_decode),
}


def apply_decode_chain(data: bytes, chain: str) -> tuple[bytes, list[str]]:
    """Apply a chain of decoders in order. Returns (result, steps_applied)."""
    steps = []
    result = data

    for char in chain:
        if char in DECODERS:
            name, decoder = DECODERS[char]
            result = decoder(result)
            steps.append(name)

    return result, steps


class Handler(BaseHTTPRequestHandler):
    decode_chain = ""

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        content_type = self.headers.get("Content-Type", "text/plain")
        post_data = self.rfile.read(content_length)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Data received")

        print(f"PATH: {self.path}")

        if "application/x-www-form-urlencoded" in content_type:
            # Parse form data and decode each value
            form_data = post_data.decode("utf-8", errors="replace")
            for param in form_data.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                else:
                    key, value = param, ""
                print(f"Raw {key}: {value}")
                if self.decode_chain:
                    try:
                        decoded, steps = apply_decode_chain(
                            value.encode("utf-8"), self.decode_chain
                        )
                        print(f"Decoded {key} ({' -> '.join(steps)}):")
                        print(decoded.decode("utf-8", errors="replace"))
                    except Exception as e:
                        print(f"Decode failed for {key}: {e}")
        else:
            # Plain text body
            print("Raw:")
            print(post_data.decode("utf-8", errors="replace"))
            if self.decode_chain:
                try:
                    decoded, steps = apply_decode_chain(post_data, self.decode_chain)
                    print(f"Decoded ({' -> '.join(steps)}):")
                    print(decoded.decode("utf-8", errors="replace"))
                except Exception as e:
                    print(f"Decode failed: {e}")

        print(f"{'=' * 50}\n")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()

        print(f"PATH: {self.path}")

        if "?" in self.path and self.decode_chain:
            query = self.path.split("?", 1)[1]
            # Parse query params and decode each value
            for param in query.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                else:
                    key, value = param, ""
                try:
                    decoded, steps = apply_decode_chain(
                        value.encode("utf-8"), self.decode_chain
                    )
                    print(f"Decoded {key} ({' -> '.join(steps)}):")
                    print(decoded.decode("utf-8", errors="replace"))
                except Exception as e:
                    print(f"Decode failed for {key}: {e}")

        print(f"{'=' * 50}\n")


def main():
    port = 4000
    decode_chain = ""

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "-h" or arg == "--help":
            print_help(sys.argv[0])
            sys.exit(0)
        elif arg == "-p":
            if i + 1 < len(args):
                port = int(args[i + 1])
                i += 2
                continue
            else:
                print("Error: -p requires a port number")
                sys.exit(1)
        elif arg.startswith("-"):
            # This is a decode chain
            decode_chain = arg[1:]  # Strip the leading dash
        i += 1

    # Validate decode chain
    for char in decode_chain:
        if char not in DECODERS:
            print(f"Unknown decoder: '{char}'")
            print("Valid decoders: 0 (hex), b (base64), u (url), H (html)")
            sys.exit(1)

    Handler.decode_chain = decode_chain

    if decode_chain:
        steps = [DECODERS[c][0] for c in decode_chain]
        print(f"Decode chain: {' -> '.join(steps)}")
    else:
        print("No decoding (plaintext mode)")

    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Server listening on port {port}...")

    def shutdown(sig, frame):
        print("\nShutting down...")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
