"""
speech_synthesizer.py
Stage 0 Speech Synthesizer for Master Story Production Pipeline:
Takes a narrative Script.txt (formatted in chunks or paragraphs),
synthesizes natural neural voiceover using edge-tts with calm, deliberate pacing,
inserts natural story pauses between chunks, and exports a master MP3.
"""

import argparse
import asyncio
import io
import os
import re
import sys
import edge_tts
from pydub import AudioSegment

DEFAULT_VOICE = "en-GB-SoniaNeural"
DEFAULT_RATE = "-8%"
DEFAULT_PAUSE_MS = 1400

def parse_script_chunks(script_path: str) -> list[str]:
    with open(script_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Split by Chunk header if present, otherwise split by double newlines
    if re.search(r'Chunk\s+\d+', text, re.I):
        raw_chunks = re.split(r'Chunk\s+\d+', text, flags=re.I)
    else:
        raw_chunks = text.split('\n\n')

    chunks = []
    for c in raw_chunks:
        cleaned = re.sub(r'[\r\n]+', ' ', c).strip()
        if cleaned:
            chunks.append(cleaned)
    return chunks

async def synthesize_chunk(text: str, voice: str, rate: str, max_retries: int = 4) -> bytes:
    for attempt in range(1, max_retries + 1):
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            buffer = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    buffer.write(chunk["data"])
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            if attempt == max_retries:
                raise
            print(f"  [SpeechSynthesizer] Connection warning: {e}. Retrying ({attempt+1}/{max_retries}) in {attempt * 2}s...")
            await asyncio.sleep(attempt * 2)

async def synthesize_story(
    script_path: str,
    output_path: str,
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE,
    pause_ms: int = DEFAULT_PAUSE_MS
):
    print(f"\n[SpeechSynthesizer] Reading script from: {script_path}")
    chunks = parse_script_chunks(script_path)
    num_chunks = len(chunks)
    print(f"[SpeechSynthesizer] Parsed {num_chunks} narrative chunks.")
    print(f"[SpeechSynthesizer] Synthesizing with Voice='{voice}', Rate='{rate}', Pause={pause_ms}ms...")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    master_audio = AudioSegment.silent(duration=1000) # Initial 1s calm breath
    separator = AudioSegment.silent(duration=pause_ms)

    for idx, chunk_text in enumerate(chunks, 1):
        print(f"[SpeechSynthesizer] Synthesizing Chunk {idx}/{num_chunks} ({len(chunk_text)} chars)...")
        audio_data = await synthesize_chunk(chunk_text, voice, rate)
        chunk_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
        
        master_audio += chunk_segment
        if idx < num_chunks:
            master_audio += separator
        else:
            master_audio += AudioSegment.silent(duration=2000) # Trailing 2s silence

    duration_sec = len(master_audio) / 1000.0
    print(f"[SpeechSynthesizer] Total Duration: {duration_sec:.2f}s ({len(master_audio)*1000} us)")
    print(f"[SpeechSynthesizer] Exporting to: {output_path}...")
    master_audio.export(output_path, format="mp3", bitrate="320k")
    print(f"[SpeechSynthesizer] Successfully created master voiceover: {output_path} ({os.path.getsize(output_path)} bytes)\n")

    return {
        "output_path": output_path,
        "duration_seconds": duration_sec,
        "num_chunks": num_chunks,
        "voice": voice,
        "rate": rate
    }

def main():
    parser = argparse.ArgumentParser(description="Stage 0: Speech Synthesizer for Story Pipelines")
    parser.add_argument("--script", required=True, help="Path to Script.txt")
    parser.add_argument("--output", required=True, help="Path for output MP3 audio file")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"Voice identifier (default: {DEFAULT_VOICE})")
    parser.add_argument("--rate", default=DEFAULT_RATE, help="Speech rate e.g. -8%% or -10%%")
    parser.add_argument("--pause-ms", type=int, default=DEFAULT_PAUSE_MS, help=f"Inter-chunk pause in ms (default: {DEFAULT_PAUSE_MS})")
    args, unknown = parser.parse_known_args()

    # Normalize rate string
    rate_val = args.rate
    if not rate_val.endswith('%'):
        rate_val = f"{rate_val}%"
    if not rate_val.startswith('+') and not rate_val.startswith('-'):
        rate_val = f"+{rate_val}"

    asyncio.run(synthesize_story(
        script_path=args.script,
        output_path=args.output,
        voice=args.voice,
        rate=rate_val,
        pause_ms=args.pause_ms
    ))

if __name__ == "__main__":
    main()
