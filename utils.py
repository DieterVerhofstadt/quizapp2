import io
import os
import asyncio
import tempfile

import pandas as pd
from gtts import gTTS
from pydub import AudioSegment
from pydub.generators import Sine
import edge_tts

def create_tts_mp3(text):
    """Create TTS audio using Edge TTS and return as AudioSegment."""
    try:
        # Use Edge TTS with Belgian Dutch voice
        audio = asyncio.run(_generate_edge_tts(text))
        return audio
    except Exception as e:
        print(f"Edge TTS error for text '{text[:50]}...': {e}")
        print("Falling back to Google TTS...")
        # Fallback to gTTS
        try:
            mp3_fp = io.BytesIO()
            tts = gTTS(text=text, lang='nl', tld='be', slow=False)
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            return AudioSegment.from_mp3(mp3_fp)
        except Exception as e2:
            print(f"gTTS also failed: {e2}")
            return AudioSegment.silent(duration=1000)


async def _generate_edge_tts(text):
    """Async helper to generate Edge TTS audio."""
    # Use Belgian Dutch male voice (sounds more natural)
    voice = "nl-BE-ArnaudNeural"

    # Create temporary file for Edge TTS output
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_path = tmp_file.name

    try:
        # Generate speech with Edge TTS
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(tmp_path)

        # Load as AudioSegment
        audio = AudioSegment.from_mp3(tmp_path)

        return audio
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def create_beep(frequency=800, duration_ms=200):
    """Create a beep sound."""
    beep = Sine(frequency).to_audio_segment(duration=duration_ms)
    # Reduce volume to -10dB to avoid being too loud
    return beep - 10

def pauze(number, beeps_at_end=0):
    """
    Return an AudioSegment containing `number` seconds of silence.
    If beeps_at_end > 0, adds that many beeps (1 per second) at the end.
    """
    duration_ms = max(0, int(number * 1000))

    if beeps_at_end == 0:
        return AudioSegment.silent(duration=duration_ms)

    # Calculate silence duration (total minus beep time)
    beep_section_ms = beeps_at_end * 1000
    silence_ms = max(0, duration_ms - beep_section_ms)

    # Start with silence
    audio = AudioSegment.silent(duration=silence_ms)

    # Add beeps (one per second)
    for i in range(beeps_at_end):
        audio += create_beep(frequency=800, duration_ms=200)
        # Add silence to fill the rest of the second (except for last beep)
        if i < beeps_at_end - 1:
            audio += AudioSegment.silent(duration=800)

    # Add final silence to reach exact duration
    final_silence = duration_ms - len(audio)
    if final_silence > 0:
        audio += AudioSegment.silent(duration=final_silence)

    return audio

def merge_csv(output_filename="samengevoegd.csv", exclude_files=None):
    """Combineer alle CSV-bestanden in één bestand en retourneer het pad."""
    map_pad = "csv"
    exclude = {os.path.basename(name) for name in (exclude_files or [])}
    exclude.add(os.path.basename(output_filename))
    alle_bestanden = [
        f for f in os.listdir(map_pad)
        if f.endswith(".csv") and f not in exclude
    ]
    if not alle_bestanden:
        raise FileNotFoundError("Geen CSV-bestanden gevonden om samen te voegen.")

    dataframes = []
    for bestand in alle_bestanden:
        volledig_pad = os.path.join(map_pad, bestand)
        try:
            df = pd.read_csv(volledig_pad, encoding='utf-8')
            # Validate required columns
            if 'vraag' in df.columns and 'antwoord' in df.columns:
                dataframes.append(df)
            else:
                print(f"Skipping {bestand}: missing 'vraag' or 'antwoord' column")
        except Exception as e:
            print(f"Error reading {bestand}: {e}")
            continue

    if not dataframes:
        raise ValueError("Geen geldige CSV-bestanden gevonden met 'vraag' en 'antwoord' kolommen.")

    combined_df = pd.concat(dataframes, ignore_index=True).drop_duplicates()
    output_path = os.path.join(map_pad, output_filename)
    combined_df.to_csv(output_path, index=False)
    return output_path
