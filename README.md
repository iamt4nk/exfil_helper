# HTTP Decode Server

A simple Python HTTP server for capturing and decoding incoming requests. Useful for security testing, debugging webhooks, and analyzing encoded payloads.

## Features

- Captures GET and POST requests
- Chainable decoders applied in specified order
- Parses `application/x-www-form-urlencoded` POST bodies automatically
- Decodes query parameters individually
- Clean output format

## Installation

No dependencies required — uses only Python standard library.

```bash
git clone https://github.com/yourusername/http-decode-server.git
cd http-decode-server
```

## Usage

```bash
python python_server.py [-p PORT] [-<decoders>]
```

### Decoder Flags

| Flag | Decoder |
|------|---------|
| `0` | Hex |
| `b` | Base64 |
| `u` | URL |
| `H` | HTML entity |

Decoders are applied left-to-right in the order specified.

### Examples

```bash
# No decoding (plaintext)
python python_server.py

# Base64 decode
python python_server.py -b

# Base64 decode, then HTML entity decode
python python_server.py -bH

# Hex decode → Base64 decode → URL decode
python python_server.py -0bu

# Custom port with URL decoding
python python_server.py -p 8080 -u
```

## Example Output

```
$ python python_server.py -bH
Decode chain: Base64 -> HTML
Server listening on port 4000...
127.0.0.1 - - [28/Jan/2026 17:31:59] "GET /?data=JiN4MjU7 HTTP/1.1" 200 -
PATH: /?data=JiN4MjU7
Decoded data (Base64 -> HTML):
%
==================================================
```

## Use Cases

- Receiving exfiltrated data in security assessments
- Debugging encoded webhook payloads
- Analyzing multi-layer encoded data
- Testing payloads

## License

MIT
