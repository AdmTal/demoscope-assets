#!/usr/bin/env python3
"""
Combine App Preview Videos for App Store Connect

Concatenates individual demo videos into a single App Preview video
that meets Apple's exact specifications.

Apple App Preview Specs (from developer.apple.com):
  - Codec: H.264 High Profile Level 4.0, 10-12 Mbps
  - Audio: Stereo AAC 256kbps (silent track required)
  - Frame rate: 30 fps, progressive
  - Duration: 15-30 seconds total
  - Pixel format: yuv420p
  - Format: .mp4 / .mov / .m4v

iPhone resolutions (portrait):
  - 6.9"/6.5"/6.3"/6.1" displays: 886x1920
  - 5.5" display: 1080x1920

iPad resolutions (portrait):
  - 13"/12.9"/11"/10.5" displays: 1200x1600
  - 9.7" display: 900x1200

Usage:
  python3 combine_preview_videos.py
"""

import subprocess
import os
import sys
import tempfile

# ─────────────────────────────────────────────
# VIDEO ORDER — Rearrange this list to change
# the order clips appear in the final video.
# ─────────────────────────────────────────────
CLIP_ORDER = [
    "demo_woman_1",
    "demo_man_1",
    "demo_woman_2",
    "demo_man_2",
]

# ─────────────────────────────────────────────
# DEVICE CONFIGS
# ─────────────────────────────────────────────
DEVICES = {
    "iPhone": {
        "input_dir": "demo_vids/iPhone",
        "filename_prefix": "iphone",
        "output": "demo_vids/iPhone/app_preview_iPhone.mp4",
        "width": 886,
        "height": 1920,
    },
    "iPad": {
        "input_dir": "demo_vids/iPad",
        "filename_prefix": "ipad",
        "output": "demo_vids/iPad/app_preview_iPad.mp4",
        "width": 1200,
        "height": 1600,
    },
}

# ─────────────────────────────────────────────
# ENCODING SETTINGS (Apple App Preview specs)
# ─────────────────────────────────────────────
FPS = 30
VIDEO_BITRATE = "10M"
AUDIO_BITRATE = "256k"
AUDIO_SAMPLE_RATE = 48000
H264_PROFILE = "high"
H264_LEVEL = "4.0"


def get_input_path(device_cfg, clip_name):
    """Build the input file path for a clip.

    Clip names in CLIP_ORDER are like 'demo_woman_1'.
    Files on disk are like 'iphone_demo_woman_1.mp4'.
    """
    filename = f"{device_cfg['filename_prefix']}_{clip_name}.mp4"
    return os.path.join(device_cfg["input_dir"], filename)


def normalize_clip(input_path, output_path, target_w, target_h):
    """Re-encode a single clip to match App Preview specs exactly.

    - Scales/crops to exact target resolution
    - Adds silent stereo audio track (required by App Store Connect)
    - Encodes H.264 High Profile Level 4.0
    - Forces 30fps CFR, yuv420p, bt709 color
    """
    video_filter = (
        # Scale to cover target, then crop to exact size
        f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
        f"crop={target_w}:{target_h},"
        # Force color space for Apple compatibility
        f"colorspace=all=bt709,"
        f"format=yuv420p"
    )

    cmd = [
        "ffmpeg", "-y",
        # Input video
        "-i", input_path,
        # Generate silent audio (anullsrc) — Apple requires an audio track
        "-f", "lavfi", "-i",
        f"anullsrc=channel_layout=stereo:sample_rate={AUDIO_SAMPLE_RATE}",
        # Video encoding
        "-c:v", "libx264",
        "-profile:v", H264_PROFILE,
        "-level:v", H264_LEVEL,
        "-b:v", VIDEO_BITRATE,
        "-maxrate", VIDEO_BITRATE,
        "-bufsize", "20M",
        "-r", str(FPS),
        "-vsync", "cfr",
        "-pix_fmt", "yuv420p",
        "-vf", video_filter,
        # Audio encoding (from the silent source)
        "-c:a", "aac",
        "-b:a", AUDIO_BITRATE,
        "-ar", str(AUDIO_SAMPLE_RATE),
        "-ac", "2",
        # Use shortest input to determine duration (video length, not infinite audio)
        "-shortest",
        # Map: video from input 0, audio from input 1
        "-map", "0:v:0",
        "-map", "1:a:0",
        # Faststart for streaming
        "-movflags", "+faststart",
        output_path,
    ]

    print(f"  Normalizing: {os.path.basename(input_path)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR:\n{result.stderr[-3000:]}")
        raise RuntimeError(f"ffmpeg failed for {input_path}")


def concatenate_clips(clip_paths, output_path):
    """Concatenate normalized clips using ffmpeg concat demuxer."""
    concat_list = output_path + ".concat.txt"
    with open(concat_list, "w") as f:
        for p in clip_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        # Re-encode to ensure clean output with correct specs
        "-c:v", "libx264",
        "-profile:v", H264_PROFILE,
        "-level:v", H264_LEVEL,
        "-b:v", VIDEO_BITRATE,
        "-maxrate", VIDEO_BITRATE,
        "-bufsize", "20M",
        "-r", str(FPS),
        "-vsync", "cfr",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", AUDIO_BITRATE,
        "-ar", str(AUDIO_SAMPLE_RATE),
        "-ac", "2",
        "-movflags", "+faststart",
        output_path,
    ]

    print(f"  Concatenating → {output_path}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    os.remove(concat_list)
    if result.returncode != 0:
        print(f"  ERROR:\n{result.stderr[-2000:]}")
        raise RuntimeError("Concatenation failed")


def get_duration(filepath):
    """Get video duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        filepath,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return float(result.stdout.strip())


def process_device(device_name, device_cfg):
    """Process all clips for a single device type."""
    target_w = device_cfg["width"]
    target_h = device_cfg["height"]
    output_path = device_cfg["output"]

    print(f"\n{'=' * 55}")
    print(f"  {device_name} App Preview  ({target_w}x{target_h})")
    print(f"  Output: {output_path}")
    print(f"{'=' * 55}")

    # Check which clips exist
    clip_paths = []
    missing = []
    for clip_name in CLIP_ORDER:
        path = get_input_path(device_cfg, clip_name)
        if os.path.exists(path):
            clip_paths.append((clip_name, path))
        else:
            missing.append(path)

    if missing:
        print(f"\n  Skipping {device_name} — missing files:")
        for m in missing:
            print(f"    - {m}")
        return False

    if not clip_paths:
        print(f"\n  Skipping {device_name} — no clips found")
        return False

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Step 1: Normalize each clip
        normalized = []
        for i, (clip_name, input_path) in enumerate(clip_paths):
            norm_path = os.path.join(tmpdir, f"{i:02d}_{clip_name}.mp4")
            normalize_clip(input_path, norm_path, target_w, target_h)
            normalized.append(norm_path)

        # Step 2: Concatenate
        concatenate_clips(normalized, output_path)

    # Step 3: Validate duration
    duration = get_duration(output_path)
    if duration is not None:
        print(f"\n  Duration: {duration:.1f}s", end="")
        if duration < 15:
            print(f"  ⚠  WARNING: Under 15s minimum! ({duration:.1f}s)")
        elif duration > 30:
            print(f"  ⚠  WARNING: Over 30s maximum! ({duration:.1f}s)")
        else:
            print(f"  ✓  Within 15-30s requirement")
    else:
        print(f"\n  Could not verify duration (ffprobe not found?)")

    print(f"  ✓  Done → {output_path}")
    return True


def main():
    print("App Store Connect — App Preview Video Builder")
    print(f"Clip order: {', '.join(CLIP_ORDER)}")
    print(f"Encoding: H.264 {H264_PROFILE}@{H264_LEVEL}, {VIDEO_BITRATE}bps, {FPS}fps")

    results = {}
    for device_name, device_cfg in DEVICES.items():
        results[device_name] = process_device(device_name, device_cfg)

    # Summary
    print(f"\n{'=' * 55}")
    print("  Summary")
    print(f"{'=' * 55}")
    for device_name, success in results.items():
        status = "✓ Created" if success else "⊘ Skipped (missing files)"
        output = DEVICES[device_name]["output"]
        print(f"  {device_name}: {status}")
        if success:
            print(f"          {output}")

    if not any(results.values()):
        print("\n  No videos were created. Check that input files exist.")
        sys.exit(1)


if __name__ == "__main__":
    main()
