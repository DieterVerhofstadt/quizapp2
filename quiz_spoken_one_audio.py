import csv
import io
import random
import base64
from pathlib import Path
from typing import Dict, List

import streamlit as st
from pydub import AudioSegment

from utils import create_tts_mp3, merge_csv, pauze

st.title("Audioquiz")
st.write(
    "Kies een onderwerp. De app bouwt een mp3 met het getoonde aantal vragen, uit een grote vragenlijst over het onderwerp."
    " Die mp3 kan je vervolgens afspelen. Als je hetzelfde onderwerp nog eens kiest, krijg je opnieuw dat aantal random vragen,"
    " dus misschien soms dezelfde. Je kan met de slider het aantal aanpassen, dat standaard op 20 ingesteld staat. Reken op een minuut per vijf vragen."
)

aantal_vragen = st.slider("Aantal vragen.", min_value=5, max_value=50, value=20, step=5)

TOPICS: List[Dict[str, str]] = [
    {"label": "Wetenschap", "path": "csv/wetenschap.csv", "description": "Algemene wetenschappelijke weetjes."},
    {"label": "Presidenten", "path": "csv/presidenten.csv", "description": "Trivia over (voormalige) wereldleiders."},
    {"label": "Hoofdsteden van de wereld", "path": "csv/hoofdsteden.csv", "description": "Steden en landen overal ter wereld."},
    {"label": "Romeinse keizers", "path": "csv/romeinse_keizers.csv", "description": "Een duik in de Romeinse geschiedenis."},
    {"label": "Aardrijkskunde", "path": "csv/aardrijkskunde.csv", "description": "Topografie, continenten en natuur."},
    {"label": "Schaduw Red Michiel", "path": "csv/Schaduw Red Michiel.csv", "description": "Privévragen voor Michiel."},
    {"label": "Wereldkampioenen F1", "path": "csv/formule1.csv", "description": "Alle F1 wereldkampioenen per jaar."},
    {"label": "Nobelprijswinnaars literatuur", "path": "csv/nobelprijsliteratuur.csv", "description": "Literaire toppers sinds 1901."},
    {"label": "Winnaars Ronde van Frankrijk", "path": "csv/tourdefrance.csv", "description": "Elke Tour de France winnaar."},
    {"label": "Chemische elementen", "path": "csv/chemische elementen.csv", "description": "Periodiek systeem en eigenschappen."},
    {"label": "Alles door elkaar", "path": None, "description": "Combineert alle categorieën."},
]


def count_questions(csv_path: Path) -> int:
    try:
        with csv_path.open(newline='', encoding='utf-8') as csvfile:
            return sum(1 for _ in csv.DictReader(csvfile))
    except FileNotFoundError:
        return 0


def build_topic_metadata() -> List[Dict[str, str]]:
    metadata = []
    for topic in TOPICS:
        topic_copy = topic.copy()
        if topic_copy["path"]:
            topic_copy["count"] = count_questions(Path(topic_copy["path"]))
        else:
            topic_copy["count"] = 0
        metadata.append(topic_copy)

    total_count = sum(item["count"] for item in metadata if item.get("path"))
    for item in metadata:
        if not item.get("path"):
            item["count"] = total_count
    return metadata


def create_one_mp3_quiz(vragen_pad: str) -> None:
    csv_path = Path(vragen_pad)
    with csv_path.open(newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        vragenlijst = list(reader)

    if not vragenlijst:
        st.error(f"Geen vragen gevonden in {csv_path.name}.")
        return

    sample_size = min(aantal_vragen, len(vragenlijst))
    if sample_size < aantal_vragen:
        st.warning(
            f"Er zijn maar {len(vragenlijst)} vragen in {csv_path.name}, dus er worden {sample_size} vragen gebruikt."
        )

    random_vragen = random.sample(vragenlijst, sample_size)

    # Build combined audio
    combined_audio = AudioSegment.silent(duration=0)
    for index, rij in enumerate(random_vragen, start=1):
        vraag = rij.get('vraag', '')
        antwoord = rij.get('antwoord', '')
        combined_audio += (
            create_tts_mp3(f"Vraag {index}")
            + pauze(1)
            + create_tts_mp3(vraag)
            + pauze(20, beeps_at_end=4)
            + create_tts_mp3(antwoord)
            + pauze(5)
        )

    # Export to base64 for custom player
    mp3_fp = io.BytesIO()
    combined_audio.export(mp3_fp, format="mp3")
    mp3_fp.seek(0)
    audio_b64 = base64.b64encode(mp3_fp.read()).decode()

    # Store in session state
    st.session_state['quiz_audio'] = audio_b64
    st.session_state['total_questions'] = sample_size
    st.session_state['quiz_topic'] = csv_path.stem  # Store topic name

    st.success("✅ Quiz gegenereerd! Gebruik de controls hieronder om te starten.")


topic_metadata = build_topic_metadata()
selected_topic = st.selectbox(
    "Kies een onderwerp",
    options=topic_metadata,
    format_func=lambda topic: topic["label"],
)

st.caption(selected_topic["description"])
st.metric("Beschikbare vragen", selected_topic.get("count", 0))

if st.button("Genereer audioquiz", type="primary"):
    target_path = selected_topic["path"]
    if target_path is None:
        target_path = merge_csv()
    create_one_mp3_quiz(target_path)

# Interactive player controls (only show if quiz is generated)
if 'quiz_audio' in st.session_state and 'total_questions' in st.session_state:
    st.markdown("---")

    # Custom HTML/CSS/JS for interactive player
    player_html = f"""
    <style>
        .player-container {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 2rem;
            padding: 1.5rem;
            background: #f9fafb;
            border-radius: 12px;
            margin: 1rem 0;
        }}

        .play-btn {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}

        .play-btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
        }}

        .timer-wrapper {{
            position: relative;
            width: 80px;
            height: 80px;
        }}

        .timer-svg {{
            transform: rotate(-90deg);
        }}

        .timer-number {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 1.5rem;
            font-weight: 700;
            color: #1f2937;
        }}

        .counter-box {{
            text-align: center;
        }}

        .counter-label {{
            font-size: 0.75rem;
            color: #6b7280;
            margin-bottom: 0.25rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .counter-number {{
            font-size: 1.75rem;
            font-weight: 700;
            color: #374151;
        }}

        @media (max-width: 768px) {{
            .player-container {{
                flex-wrap: wrap;
                gap: 1rem;
            }}
        }}
    </style>

    <div class="player-container">
        <button class="play-btn" id="playBtn" onclick="togglePlay()">▶</button>

        <div class="timer-wrapper">
            <svg class="timer-svg" width="80" height="80">
                <circle cx="40" cy="40" r="36" fill="none" stroke="#e5e7eb" stroke-width="6"/>
                <circle id="timerCircle" cx="40" cy="40" r="36" fill="none"
                        stroke="#10b981" stroke-width="6" stroke-dasharray="226.195"
                        stroke-dashoffset="0" stroke-linecap="round"/>
            </svg>
            <div class="timer-number" id="timerText">-</div>
        </div>

        <div class="counter-box">
            <div class="counter-label">Vragen resterend</div>
            <div class="counter-number" id="questionCounter">{st.session_state['total_questions']}</div>
        </div>

        <div class="counter-box">
            <div class="counter-label">Onderwerp</div>
            <div class="counter-number" style="font-size: 1.25rem;">{st.session_state.get('quiz_topic', '')}</div>
        </div>
    </div>

    <audio id="quizAudio" preload="auto">
        <source src="data:audio/mp3;base64,{st.session_state['quiz_audio']}" type="audio/mp3">
    </audio>

    <script>
        const audio = document.getElementById('quizAudio');
        const playBtn = document.getElementById('playBtn');
        const timerCircle = document.getElementById('timerCircle');
        const timerText = document.getElementById('timerText');
        const questionCounter = document.getElementById('questionCounter');

        const QUESTION_DURATION = 27;
        const THINK_TIME = 20;
        const totalQuestions = {st.session_state['total_questions']};
        let currentQuestion = 1;

        const circumference = 2 * Math.PI * 36;

        function togglePlay() {{
            if (audio.paused) {{
                audio.play();
                playBtn.textContent = '⏸';
            }} else {{
                audio.pause();
                playBtn.textContent = '▶';
            }}
        }}

        function updateTimer() {{
            if (!audio.paused) {{
                const currentTime = audio.currentTime;
                const questionTime = currentTime % QUESTION_DURATION;

                if (questionTime >= 5 && questionTime < 25) {{
                    const timeLeft = Math.ceil(25 - questionTime);

                    if (timeLeft > 4) {{
                        timerCircle.setAttribute('stroke', '#10b981');
                    }} else {{
                        timerCircle.setAttribute('stroke', '#ef4444');
                    }}

                    const progress = timeLeft / THINK_TIME;
                    const offset = circumference * (1 - progress);
                    timerCircle.setAttribute('stroke-dashoffset', offset);

                    timerText.textContent = timeLeft;
                }} else {{
                    timerCircle.setAttribute('stroke-dashoffset', 0);
                    timerCircle.setAttribute('stroke', '#e5e7eb');
                    timerText.textContent = '-';
                }}

                const newQuestion = Math.floor(currentTime / QUESTION_DURATION) + 1;
                if (newQuestion !== currentQuestion && newQuestion <= totalQuestions) {{
                    currentQuestion = newQuestion;
                    questionCounter.textContent = totalQuestions - currentQuestion + 1;
                }}
            }}
        }}

        setInterval(updateTimer, 100);

        audio.addEventListener('ended', () => {{
            playBtn.textContent = '▶';
            questionCounter.textContent = '0';
            timerText.textContent = '✓';
            timerCircle.setAttribute('stroke', '#10b981');
            timerCircle.setAttribute('stroke-dashoffset', 0);
        }});
    </script>
    """

    st.components.v1.html(player_html, height=150)
