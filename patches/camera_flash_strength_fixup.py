# SPDX-FileCopyrightText: 2026 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

"""
camera.qcom.so fixup for the camx torch strength ceiling.

OxygenOS 15's camx initializes FlashInfoStrengthMaximumLevel = 164 and the
default strength level = 3 unconditionally. OxygenOS 16 gates the 164 behind
GetBooleanConfiguration("FlashLED", "ThreeLED") and uses 4 for every other
device. giulia is a dual-LED device (DualLedConfig), so OxygenOS 16 exposes
exactly four torch strength levels, matching the FlashLightCurrent table.

For blobs that already carry the OxygenOS 16 csel gate this fixup is a no-op.

For OxygenOS 15 blobs it replaces the hardcoded 164 with 4, reproducing the
OxygenOS 16 dual-LED behavior:

    mov  x2, #0xa4           ; 164      -> mov x2, #4
    movk x2, #0x3, lsl #32   ; default 3 (unchanged)
    str  x2, [x19, #0x3350]  ; max @0x3350, default @0x3354

The patch is anchored on the stock instruction pair, which is unique within
the blob, and is idempotent: re-running extraction over an already patched
blob is a no-op.
"""

from pathlib import Path
from typing import Final

# OxygenOS 15 stock pair: mov x2, #0xa4 / movk x2, #0x3, lsl #32.
_STOCK_PAIR: Final = bytes.fromhex("821480d26200c0f2")

# Same pair after patching: mov x2, #4 / movk x2, #0x3, lsl #32.
_PATCHED_PAIR: Final = bytes.fromhex("820080d26200c0f2")

_STOCK_INSN: Final = bytes.fromhex("821480d2")  # mov x2, #0xa4 (164)
_PATCHED_INSN: Final = bytes.fromhex("820080d2")  # mov x2, #4

# OxygenOS 16 gate prologue: mov w23, #4 / mov w8, #0xa4 / mov w9, #3 /
# mov w11, #2, followed shortly by csel w10, w8, w23, eq.
_C16_PROLOGUE: Final = bytes.fromhex(
    "97008052"  # mov w23, #4
    "88148052"  # mov w8, #0xa4
    "69008052"  # mov w9, #3
    "4b008052"  # mov w11, #2
)
_C16_CSEL: Final = bytes.fromhex("0a01971a")  # csel w10, w8, w23, eq
_C16_CSEL_WINDOW: Final = 0x30


class CameraFlashStrengthFixupError(RuntimeError):
    pass


def _has_c16_gate(blob: bytes) -> bool:
    """True when the blob already carries the OxygenOS 16 ThreeLED gate."""
    start = 0
    while True:
        start = blob.find(_C16_PROLOGUE, start)
        if start < 0:
            return False
        window = blob[start : start + len(_C16_PROLOGUE) + _C16_CSEL_WINDOW]
        if window.find(_C16_CSEL) >= 0:
            return True
        start += 1


def patch_camera_flash_strength(blob: bytes) -> bytes:
    """Cap the hardcoded torch strength maximum level at 4."""

    if blob.count(_PATCHED_PAIR) == 1 and blob.count(_STOCK_PAIR) == 0:
        # Already patched by a previous extraction.
        return blob

    if _has_c16_gate(blob):
        # OxygenOS 16 generation blob: the 164 level is already gated behind
        # the ThreeLED configuration and dual-LED devices get 4.
        return blob

    count = blob.count(_STOCK_PAIR)
    if count > 1:
        raise CameraFlashStrengthFixupError(
            f"camera.qcom.so: strength instruction pair found {count} times "
            "(expected at most 1)"
        )
    if count == 0:
        raise CameraFlashStrengthFixupError(
            "camera.qcom.so: strength initialization sequence not found"
        )

    offset = blob.index(_STOCK_PAIR)
    patched = bytearray(blob)
    patched[offset : offset + 4] = _PATCHED_INSN
    return bytes(patched)


def patch_camera_flash_strength_file(file_path: str) -> None:
    path = Path(file_path)
    try:
        patched = patch_camera_flash_strength(path.read_bytes())
    except CameraFlashStrengthFixupError as e:
        raise CameraFlashStrengthFixupError(f"{file_path}: {e}") from e
    path.write_bytes(patched)
