import asyncio
import os
import edge_tts

text = (
    "There are things we mean to say and do not say. Not because we are cruel or cowardly, "
    "but because the moment passes before we find the right words, and then it is the next day, "
    "and the next, and the words are still not right, and the moment is further away now, "
    "and sending something imperfect into that distance feels worse than saying nothing at all. "
    "This is how thirty years pass. This is how a box fills up. "
    "This is the story of a woman named Margaret, a box of letters she never sent, "
    "and the slow, difficult work of deciding it was not too late."
)

output_dir = r"D:\Himu\Luna\tts_samples"
os.makedirs(output_dir, exist_ok=True)

voices = [
    {
        "id": "en-US-ChristopherNeural",
        "rate": "-10%",
        "file": "sample_01_christopher_deep_reflective.mp3",
        "desc": "Christopher (US) - Deep, reflective, meditative"
    },
    {
        "id": "en-GB-RyanNeural",
        "rate": "-8%",
        "file": "sample_02_ryan_literary_british.mp3",
        "desc": "Ryan (GB) - Literary, warm, thoughtful British storyteller"
    },
    {
        "id": "en-GB-SoniaNeural",
        "rate": "-8%",
        "file": "sample_03_sonia_calm_female.mp3",
        "desc": "Sonia (GB) - Gentle, calm, soothing female storyteller"
    },
    {
        "id": "en-US-GuyNeural",
        "rate": "-10%",
        "file": "sample_04_guy_classic_narrator.mp3",
        "desc": "Guy (US) - Classic, grounded storytelling voice"
    }
]

async def generate():
    for v in voices:
        dest = os.path.join(output_dir, v["file"])
        print(f"Generating {v['desc']}...")
        communicate = edge_tts.Communicate(text, v["id"], rate=v["rate"])
        await communicate.save(dest)
        size = os.path.getsize(dest)
        print(f"  Saved: {dest} ({size} bytes)")

if __name__ == "__main__":
    asyncio.run(generate())
