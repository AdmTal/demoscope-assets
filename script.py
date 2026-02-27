#!/usr/bin/env python3
"""
DemoScope In-App Event Video Generator
Creates event_card.mp4 (landscape) and event_details.mp4 (portrait)
No text overlay — clean clips, scaled and concatenated.
"""

import subprocess
import os
import tempfile

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
CLIP_ORDER = ["woman_1", "man_1", "woman_2", "man_2"]
CLIP_DURATION = 3  # seconds per clip

INPUT_BASE = "."
LANDSCAPE_DIR = os.path.join(INPUT_BASE, "Landscape")
PORTRAIT_DIR = os.path.join(INPUT_BASE, "Portrait")
OUTPUT_CARD = "event_card.mp4"
OUTPUT_DETAILS = "event_details.mp4"

LANDSCAPE_W, LANDSCAPE_H = 1920, 1080
PORTRAIT_W, PORTRAIT_H = 1080, 1920


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def build_clip(input_path, output_path, target_w, target_h):
    scale_filter = (
        f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
        f"crop={target_w}:{target_h}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-t", str(CLIP_DURATION),
        "-vf", scale_filter,
        "-an",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-r", "30", "-vsync", "cfr",
        output_path,
    ]

    print(f"  Processing: {os.path.basename(input_path)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR:\n{result.stderr[-3000:]}")
        raise RuntimeError(f"ffmpeg failed for {input_path}")


def concatenate_clips(clip_paths, output_path):
    list_file = output_path + ".concat.txt"
    with open(list_file, "w") as f:
        for p in clip_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        output_path,
    ]
    print(f"  Concatenating → {output_path}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    os.remove(list_file)
    if result.returncode != 0:
        print(f"  ERROR:\n{result.stderr[-2000:]}")
        raise RuntimeError("concat failed")


def process_set(source_dir, target_w, target_h, output_path):
    label = "Portrait" if target_h > target_w else "Landscape"
    print(f"\n{'=' * 50}")
    print(f"  Building {label}  →  {output_path}")
    print(f"{'=' * 50}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_clips = []
        for key in CLIP_ORDER:
            gender, num = key.split("_")
            input_path = os.path.join(source_dir, f"{gender}_{num}.mp4")

            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Missing: {input_path}")

            clip_out = os.path.join(tmpdir, f"{key}.mp4")
            build_clip(input_path, clip_out, target_w, target_h)
            tmp_clips.append(clip_out)

        concatenate_clips(tmp_clips, output_path)

    print(f"  ✓ Done → {output_path}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    process_set(LANDSCAPE_DIR, LANDSCAPE_W, LANDSCAPE_H, OUTPUT_CARD)
    process_set(PORTRAIT_DIR, PORTRAIT_W, PORTRAIT_H, OUTPUT_DETAILS)

    print("\n✓ All outputs ready:")
    print(f"  {OUTPUT_CARD}")
    print(f"  {OUTPUT_DETAILS}")
