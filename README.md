# Exfil Helper

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
git clone https://github.com/iamt4nk/exfil_helper.git
cd exfil_helper
```

## Usage

```bash
python exfil_helper.py [-p PORT] [-<decoders>]
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
python exfil_helper.py

# Base64 decode
python exfil_helper.py -b

# Base64 decode, then HTML entity decode
python exfil_helper.py -bH

# Hex decode → Base64 decode → URL decode
python exfil_helper.py -0bu

# Custom port with URL decoding
python exfil_helper.py -p 8080 -u
```

## Example Output

```
$ python exfil_helper.py -bH
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
