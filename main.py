#!/usr/bin/env python3
"""news-23 b143 heroes-scene: copy entry.png (1024x1024) to $MAKEFUN_OUTPUT_DIR/entry.png.

Stdlib only (no PIL). Never writes next to itself: it writes only to
MAKEFUN_OUTPUT_DIR, which the grader sets to a fresh empty directory.
Validates the PNG header by hand (struct) before copying.
"""
import hashlib
import os
import struct
import sys
import zlib

# SHA-256 of entry.png as committed in this repo. Filled in after the
# final draw; main.py refuses to copy a PNG whose hash differs.
EXPECTED_SHA256 = "f64fc2915edef937a00f69cd8c5c73dbb342bff50300af139cc996c0a3391a04"

MIN_BYTES = 10_000
MAX_BYTES = 1_048_576


def fail(msg):
    print("main.py: error: " + msg, file=sys.stderr)
    return 1


def read_png(path):
    """Validate a PNG file by hand. Returns (width, height, data)."""
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) < MIN_BYTES:
        raise ValueError("too small: %d bytes" % len(data))
    if len(data) > MAX_BYTES:
        raise ValueError("too large: %d bytes" % len(data))
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("bad PNG signature")
    # Chunk layout: length (4 bytes, big-endian) | type (4) | data | CRC (4).
    # The first chunk must be IHDR, 13 bytes of data, starting at offset 8.
    if len(data) < 8 + 8 + 13 + 4:
        raise ValueError("truncated before IHDR")
    ihdr_len = struct.unpack(">I", data[8:12])[0]
    ihdr_type = data[12:16]
    if ihdr_type != b"IHDR" or ihdr_len != 13:
        raise ValueError("first chunk is not a 13-byte IHDR")
    # IHDR data lives at bytes 16-28; its CRC covers type+data (bytes 12-28).
    ihdr_data = data[16:29]
    ihdr_crc_stored = struct.unpack(">I", data[29:33])[0]
    ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data) & 0xFFFFFFFF
    if ihdr_crc != ihdr_crc_stored:
        raise ValueError("bad CRC in chunk IHDR")
    width, height, depth, ctype, comp, filt, interlace = struct.unpack(
        ">IIBBBBB", ihdr_data)
    if (width, height) != (1024, 1024):
        raise ValueError("wrong size: %dx%d" % (width, height))
    if depth != 8 or ctype not in (2, 6):
        raise ValueError("unsupported bit depth %d / colour type %d"
                         % (depth, ctype))
    if comp != 0 or filt != 0 or interlace != 0:
        raise ValueError("unsupported compression/filter/interlace")
    # Walk the remaining chunks: CRC each, require non-empty IDAT payload,
    # require IEND (0 bytes) as the last chunk with no trailing data.
    pos = 8 + 8 + 13 + 4  # next chunk starts at offset 33
    idat_total = 0
    seen_iend = False
    while pos < len(data):
        if pos + 8 > len(data):
            raise ValueError("truncated chunk header at %d" % pos)
        clen = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        end = pos + 8 + clen + 4
        if end > len(data):
            raise ValueError("truncated chunk %r" % ctype)
        crc_stored = struct.unpack(">I", data[pos + 8 + clen:end])[0]
        crc = zlib.crc32(data[pos + 4:pos + 8 + clen]) & 0xFFFFFFFF
        if crc != crc_stored:
            raise ValueError("bad CRC in chunk %r" % ctype)
        if ctype == b"IDAT":
            if clen == 0:
                raise ValueError("empty IDAT chunk")
            idat_total += clen
        if ctype == b"IEND":
            if clen != 0:
                raise ValueError("IEND must be 0 bytes")
            if end != len(data):
                raise ValueError("trailing data after IEND")
            seen_iend = True
            break
        pos = end
    if not seen_iend:
        raise ValueError("missing IEND chunk")
    if idat_total < 1000:
        raise ValueError("IDAT payload too small: %d bytes" % idat_total)
    return width, height, data


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    if not out_dir:
        return fail("MAKEFUN_OUTPUT_DIR is empty")
    out_dir_abs = os.path.abspath(out_dir)
    if out_dir_abs == here or out_dir_abs.startswith(here + os.sep):
        return fail("MAKEFUN_OUTPUT_DIR must not be inside the repo")
    if os.path.isfile(out_dir_abs):
        return fail("MAKEFUN_OUTPUT_DIR is a file, not a directory")
    dst = os.path.join(out_dir_abs, "entry.png")
    if os.path.abspath(dst) == os.path.abspath(src):
        return fail("output would overwrite the source image")
    if not os.path.isfile(src):
        return fail("source entry.png not found next to main.py")
    try:
        width, height, data = read_png(src)
    except (OSError, ValueError) as exc:
        return fail("invalid entry.png: %s" % exc)
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        return fail("sha256 mismatch: got %s, expected %s"
                    % (digest, EXPECTED_SHA256))
    os.makedirs(out_dir_abs, exist_ok=True)
    with open(dst, "wb") as fh:
        fh.write(data)
    with open(dst, "rb") as fh:
        written = fh.read()
    if written != data:
        return fail("re-read of output differs from source")
    print("main.py: wrote %s (%dx%d, %d bytes, sha256 %s)"
          % (dst, width, height, len(data), digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
