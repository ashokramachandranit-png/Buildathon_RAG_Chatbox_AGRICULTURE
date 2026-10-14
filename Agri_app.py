
import os
from io import BytesIO
import streamlit as st
from dotenv import load_dotenv
from gtts import gTTS
from openai import OpenAI
from rag_chain import query_rag_with_sources
from streamlit_mic_recorder import mic_recorder

load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="TN Agri Schemes & Voice Assistant",
    page_icon="🌾",
    layout="wide",
)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Custom CSS for Professional UI Alignment & Card Styling
st.markdown(
    """
    <style>
    .banner-container {
        background: linear-gradient(135deg, #1b4d3e 0%, #2e7d32 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .banner-title {
        font-size: 26px;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .banner-subtitle {
        font-size: 15px;
        color: #ffeb3b;
        font-weight: 600;
    }
    .scheme-card {
        background-color: #ffffff;
        border: 2px solid #2e7d32;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
        text-align: center;
        margin-bottom: 10px;
        min-height: 270px;
    }
    .scheme-number {
        background-color: #2e7d32;
        color: white;
        font-weight: bold;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 10px auto;
        font-size: 15px;
    }
    .scheme-title {
        font-size: 14px;
        font-weight: bold;
        color: #1b4d3e;
        margin-bottom: 8px;
    }
    .scheme-desc {
        font-size: 12px;
        color: #444;
        margin-bottom: 10px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def text_to_speech(text: str):
    try:
        selected_lang = (
            "ta" if any("\u0b80" <= char <= "\u0bff" for char in text) else "en"
        )
        tts = gTTS(text=text, lang=selected_lang, slow=False)
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp
    except Exception as e:
        return None


# Navigation Tabs
tab1, tab2 = st.tabs(
    ["🌱 தமிழ்நாடு அரசு வேளாண் திட்டங்கள் (TN Schemes)", "🎙️ AI Voice & Text Assistant"]
)

# ==========================================
# TAB 1: TAMIL NADU GOVT AGRICULTURE SCHEMES DASHBOARD
# ==========================================
with tab1:
    st.markdown(
        """
        <div class="banner-container">
            <div class="banner-title">🌾 தமிழ்நாடு அரசு வேளாண்மை மற்றும் உழவர் நலத்துறை திட்டங்கள்</div>
            <div class="banner-subtitle">Tamil Nadu Government Agriculture Schemes & Subsidies | Click any card below for details</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Initialize session state for selected scheme query if not present
    if "selected_query" not in st.session_state:
        st.session_state.selected_query = None

    col1, col2, col3, col4, = st.columns(4)

    # Card 1
    with col1:
        st.markdown(
            """
            <div class="scheme-card">
                <div class="scheme-number">01</div>
                <div class="scheme-title">WATER MANAGEMENT</div>
                <div class="scheme-desc">Electric motor pumpsets with subsidy.</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("🔍 Get Details", key="btn_1", use_container_width=True):
            st.session_state.selected_query = (
                "Get up to 50% subsidy (or up to ₹15,000) on purchasing new energy-efficient electric motor pumpsets—whether for replacing old ones or installing in newly created wells!"
            )

    # Card 2
    with col2:
        st.markdown(
            """
            <div class="scheme-card">
                <div class="scheme-number">02</div>
                <div class="scheme-title">AGRICULTURAL ENGINEERING</div>
                <div class="scheme-desc">Schemes Under Agricultural Engineering Department.</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("🔍 Get Details", key="btn_2", use_container_width=True):
            st.session_state.selected_query = (
                "What are all the schemes under agricultural engineering available for TN farmers?"
            )

    # Card 3
    with col3:
        st.markdown(
            """
            <div class="scheme-card">
                <div class="scheme-number">03</div>
                <div class="scheme-title">GROWER ONLINE REGISTRATION OF AGRICULTURE INPUT SYSTEM (GRAINS)</div>
                <div class="scheme-desc">Tamil Nadu's farmers benefit from real-time data on weather, market trends, and crop advisories, enhancing decision-making.</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("🔍 Get Details", key="btn_3", use_container_width=True):
            st.session_state.selected_query = (
                " It is poised to collectively shape the agricultural landscape of Tamil Nadu in the coming decade, ensuring sustainable development for the sector."
            )

   
    # Card 4
    with col4:
        st.markdown(
            """
            <div class="scheme-card">
                <div class="scheme-number">04</div>
                <div class="scheme-title">Special Welfare & Skill Development Schemes</div>
                <div class="scheme-desc">Agricultural Engineering Department is providing training to unemployed rural youth for increasing their employment opportunities.</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("🔍 Get Details", key="btn_4", use_container_width=True):
            st.session_state.selected_query = (
                "Agricultural Engineering Department is providing training to unemployed rural youth for increasing their employment opportunities"
            )

    # If a scheme button was clicked, display its detailed RAG response right here!
    if st.session_state.selected_query:
        st.divider()
        st.subheader(
            f"📖 Scheme Information: {st.session_state.selected_query}"
        )
        with st.spinner("Fetching official scheme details..."):
            res = query_rag_with_sources(st.session_state.selected_query)
            st.markdown(res["answer"])
            audio_fp = text_to_speech(res["answer"])
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")
            if res["sources"]:
                with st.expander("📚 Official Sources Consulted"):
                    for src in res["sources"]:
                        st.markdown(f"- {src}")

# ==========================================
# TAB 2: RAG VOICE & CHAT ASSISTANT
# ==========================================
# ==========================================
# TAB 2: RAG VOICE & CHAT ASSISTANT
# ==========================================
with tab2:
    st.header("🌾 Tamil Nadu Agri Schemes Voice & Text Chatbot")
    st.markdown(
        "Ask any question regarding subsidies, eligibility, or documentation in **English, Tamil (தமிழ்), or Tanglish**."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Track last processed audio bytes to prevent duplicate triggers on reruns
    if "last_audio_bytes" not in st.session_state:
        st.session_state.last_audio_bytes = None

    # Sidebar Voice Recorder
    with st.sidebar:
        st.header("🎙️ Voice Assistant")
        st.markdown("Record your query clearly:")
        audio_data = mic_recorder(
            start_prompt="Record Voice 🎤",
            stop_prompt="Stop Recording ⏹️",
            key="mic_tab_voice",
        )

    user_input = None

    # Handle Voice Input Transcription
    if audio_data and audio_data.get("bytes"):
        current_bytes = audio_data["bytes"]
        if current_bytes != st.session_state.last_audio_bytes:
            st.session_state.last_audio_bytes = current_bytes
            with st.spinner("Transcribing voice via Whisper..."):
                try:
                    audio_file_path = "temp_audio.wav"
                    with open(audio_file_path, "wb") as f:
                        f.write(current_bytes)

                    with open(audio_file_path, "rb") as audio_file:
                        transcript = openai_client.audio.transcriptions.create(
                            model="whisper-1", file=audio_file
                        )
                    user_input = transcript.text
                    if os.path.exists(audio_file_path):
                        os.remove(audio_file_path)
                except Exception as e:
                    st.error(f"Audio transcription error: {e}")

    # Handle Text Chat Input
    chat_input = st.chat_input(
        "Type your question (e.g., சொட்டு நீர் பாசன மானியம் என்ன?)..."
    )
    if chat_input:
        user_input = chat_input

    # 1. DISPLAY CHAT HISTORY FIRST (Ensures proper chronological order)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "audio" in message and message["audio"]:
                st.audio(message["audio"], format="audio/mp3")
            if "sources" in message and message["sources"]:
                with st.expander("📚 Official Sources Consulted"):
                    for src in message["sources"]:
                        st.markdown(f"- {src}")

    # 2. PROCESS NEW USER INPUT & GENERATE ASSISTANT RESPONSE
    if user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner(
                "Searching Tamil Nadu agricultural databases..."
            ):
                result = query_rag_with_sources(user_input)
                response_text = result["answer"]
                sources = result["sources"]

                st.markdown(response_text)

                audio_fp = text_to_speech(response_text)
                if audio_fp:
                    st.audio(audio_fp, format="audio/mp3")

                if sources:
                    with st.expander("📚 Official Sources Consulted"):
                        for src in sources:
                            st.markdown(f"- {src}")

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response_text,
                "sources": sources,
                "audio": audio_fp,
            }
        )
        