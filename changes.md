# Changes

- Reworked `quiz_spoken_one_audio.py` to clamp the requested sample size to the available inventory, warn users when a topic contains fewer questions, and to rebuild the UI with uniquely keyed buttons plus a single "Terug naar start" control so Streamlit no longer logs duplicate widget warnings.
- Swapped the pause generator in `utils.py` for a real silent MP3 rendered locally via `pydub` and implemented a working `merge_csv` helper that concatenates the CSV pool (minus the output file), removes duplicates, and returns the generated file path.
- Added the missing `requests` import and light response validation to `test_getting_wikipedia.py` so the script can query Wikipedia reliably.
- Fixed the `gTTS` import in `brol/quiz_app.py` so the prototype streamlit app starts without raising `ModuleNotFoundError`.
- Streamlined the Streamlit UI by replacing the crowded button grid with a selectbox, topic descriptions, and a question-count metric so users immediately understand each category before generating audio.
- Updated the quiz generator to operate on `AudioSegment` objects end-to-end and export to MP3 once, fixing the runtime error raised after switching `utils` to return pydub segments.
- Restored the 5-second countdown beeps before each answer by reapplying the `beeps_at_end` parameter to the longer pause.
- Tweaked the quiz flow to speak the question number before each prompt and to limit the countdown tones to the final 4 seconds before answers.
