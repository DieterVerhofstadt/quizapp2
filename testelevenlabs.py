import streamlit as st
import io

from elevenlabs.client import ElevenLabs

client = ElevenLabs(
    api_key=st.secrets["elevenlabs"]["api_key"]
)

def create_eleven_mp3(text, voice, model):
    audio_generator = client.text_to_speech.convert(
        text=text,
        voice_id=voice,
        model_id=model,
        output_format="mp3_44100_128",
    )
    # Combineer alle stukjes in één bytes-object
    audio_bytes = b"".join(chunk for chunk in audio_generator)
    return io.BytesIO(audio_bytes)

if st.button("Einde"):
    audio_bytes = create_eleven_mp3('Thank you for playing this quiz', voice="JBFqnCBsd6RMkjVDRZzb", model="eleven_monolingual_v1")
    st.audio(audio_bytes, format="audio/mp3")
