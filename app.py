import base64
import random
from io import BytesIO
import pandas as pd
import plotly.express as px
import streamlit as st
from gtts import gTTS
from googletrans import Translator
from audio_recorder_streamlit import audio_recorder

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & PINK/WHITE THEME
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Language Learning Assistant",
    page_icon="🌸",
    layout="wide",
)

# Custom CSS for Pink and White Theme
st.markdown(
    """
    <style>
    /* Main Background & Text Color */
    .stApp {
        background-color: #FFF0F5; /* Soft Pink / LavenderBlush */
        color: #4A4A4A;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #D81B60 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 2px solid #FFB6C1;
    }

    /* Buttons */
    div.stButton > button {
        background-color: #FF69B4 !important;
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        font-weight: bold !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #FF1493 !important;
        box-shadow: 0px 4px 10px rgba(255, 20, 147, 0.3);
    }

    /* Card Containers */
    .pink-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #FFC0CB;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    /* Input Fields */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {
        border-radius: 10px !important;
        border: 1px solid #FFB6C1 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. DATA & STATE INITIALIZATION
# -----------------------------------------------------------------------------

LANGUAGES = [
    "Afrikaans", "Albanian", "Amharic", "Arabic", "Armenian", "Azerbaijani",
    "Basque", "Belarusian", "Bengali", "Bosnian", "Bulgarian", "Catalan",
    "Cebuano", "Chichewa", "Chinese (Simplified)", "Chinese (Traditional)",
    "Corsican", "Croatian", "Czech", "Danish", "Dutch", "English",
    "Esperanto", "Estonian", "Filipino", "Finnish", "French", "Frisian",
    "Galician", "Georgian", "German", "Greek", "Gujarati", "Haitian Creole",
    "Hausa", "Hawaiian", "Hebrew", "Hindi", "Hmong", "Hungarian",
    "Icelandic", "Igbo", "Indonesian", "Irish", "Italian", "Japanese",
    "Javanese", "Kannada", "Kazakh", "Khmer", "Kinyarwanda", "Korean",
    "Kurdish", "Kyrgyz", "Lao", "Latin", "Latvian", "Lithuanian",
    "Luxembourgish", "Macedonian", "Malagasy", "Malay", "Malayalam",
    "Maltese", "Maori", "Marathi", "Mongolian", "Myanmar (Burmese)",
    "Nepali", "Norwegian", "Odia", "Pashto", "Persian", "Polish",
    "Portuguese", "Punjabi", "Romanian", "Russian", "Samoan", "Scots Gaelic",
    "Serbian", "Sesotho", "Shona", "Sindhi", "Sinhala", "Slovak",
    "Slovenian", "Somali", "Spanish", "Sundanese", "Swahili", "Swedish",
    "Tajik", "Tamil", "Tatar", "Telugu", "Thai", "Turkish",
    "Turkmen", "Ukrainian", "Urdu", "Uyghur", "Uzbek", "Vietnamese",
    "Welsh", "Xhosa", "Yiddish", "Yoruba", "Zulu"
]

MOTIVATIONAL_QUOTES = [
    "“A different language is a different vision of life.” — Federico Fellini",
    "“To have another language is to possess a second soul.” — Charlemagne",
    "“Learning another language is not only learning different words for the same things, but learning another way to think about things.” — Flora Lewis",
    "“You can never understand one language until you understand at least two.” — Geoffrey Willans"
]

VOCAB_DATABASE = {
    "Spanish": [
        {"word": "Hola", "meaning": "Hello", "level": "Beginner", "sample": "Hola, ¿cómo estás?"},
        {"word": "Gracias", "meaning": "Thank you", "level": "Beginner", "sample": "Muchas gracias por tu ayuda."},
        {"word": "Biblioteca", "meaning": "Library", "level": "Intermediate", "sample": "Voy a la biblioteca a estudiar."},
        {"word": "Desarrollo", "meaning": "Development", "level": "Intermediate", "sample": "El desarrollo tecnológico es rápido."},
        {"word": "Imprescindible", "meaning": "Essential/Indispensable", "level": "Pro", "sample": "El agua es imprescindible para la vida."}
    ],
    "French": [
        {"word": "Bonjour", "meaning": "Hello", "level": "Beginner", "sample": "Bonjour tout le monde."},
        {"word": "Merci", "meaning": "Thank you", "level": "Beginner", "sample": "Merci beaucoup!"},
        {"word": "Papillon", "meaning": "Butterfly", "level": "Intermediate", "sample": "Le papillon vole dans le jardin."},
        {"word": "Épanouissement", "meaning": "Fulfillment", "level": "Pro", "sample": "Travail de qualité et épanouissement personnel."}
    ]
}

DEFAULT_VOCAB = [
    {"word": "Welcome", "meaning": "Greeting", "level": "Beginner", "sample": "Welcome to language learning!"},
    {"word": "Practice", "meaning": "Exercise", "level": "Intermediate", "sample": "Practice makes perfect."},
    {"word": "Fluency", "meaning": "Mastery", "level": "Pro", "sample": "Achieving fluency takes dedication."}
]

# Session State
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "name": "Learner",
        "age": 22,
        "reason": "Travel and Career Growth",
        "level": "Beginner",
        "target_lang": "Spanish",
        "daily_limit": 5,
        "words_today": 0,
        "streak": 3,
        "score": 150
    }

if "custom_vocab" not in st.session_state:
    st.session_state.custom_vocab = []

if "activity_log" not in st.session_state:
    st.session_state.activity_log = pd.DataFrame({
        "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "Words Learned": [3, 5, 4, 6, 2, 5, 1],
        "Quiz Points": [20, 40, 30, 50, 20, 45, 10]
    })

if "leaderboard" not in st.session_state:
    st.session_state.leaderboard = pd.DataFrame([
        {"Rank": 1, "Name": "Sophia", "Language": "French", "Score": 420},
        {"Rank": 2, "Name": "Aarav", "Language": "Spanish", "Score": 310},
        {"Rank": 3, "Name": "Elena", "Language": "German", "Score": 240},
        {"Rank": 4, "Name": st.session_state.user_profile["name"], "Language": st.session_state.user_profile["target_lang"], "Score": st.session_state.user_profile["score"]}
    ])

# -----------------------------------------------------------------------------
# 3. HELPER FUNCTIONS
# -----------------------------------------------------------------------------

def play_audio(text, lang_code="en"):
    """Generates audio for given text using gTTS and renders an inline player."""
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_b64 = base64.b64encode(fp.read()).decode()
        audio_html = f'<audio autoplay controls src="data:audio/mp3;base64,{audio_b64}" style="height:30px;"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception:
        st.warning("Pronunciation audio not available for this selection.")

def translate_text(text, target_lang_name):
    """Translates text into the target language using googletrans."""
    try:
        translator = Translator()
        translated = translator.translate(text, dest='es' if target_lang_name == 'Spanish' else 'fr')
        return translated.text
    except Exception:
        return f"[Translation Simulation for '{text}' in {target_lang_name}]"

def get_current_vocab():
    lang = st.session_state.user_profile["target_lang"]
    base_vocab = VOCAB_DATABASE.get(lang, DEFAULT_VOCAB)
    return base_vocab + st.session_state.custom_vocab

# -----------------------------------------------------------------------------
# 4. SIDEBAR NAVIGATION & MOTIVATION
# -----------------------------------------------------------------------------
st.sidebar.title("🌸 Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "Profile",
        "Dashboard & Vocab",
        "Daily Game Tasks",
        "Pronunciation & Voice Studio",
        "Grammar & Translation",
        "Performance Analytics",
        "AI Performance Review",
        "Leaderboard"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔥 Streak & Progress")
st.sidebar.metric("Current Streak", f"{st.session_state.user_profile['streak']} Days")
st.sidebar.progress(min(st.session_state.user_profile["words_today"] / st.session_state.user_profile["daily_limit"], 1.0))
st.sidebar.write(f"Daily Goal: **{st.session_state.user_profile['words_today']} / {st.session_state.user_profile['daily_limit']} Words**")

st.sidebar.markdown("---")
st.sidebar.subheader("💡 Daily Inspiration")
st.sidebar.caption(random.choice(MOTIVATIONAL_QUOTES))

# -----------------------------------------------------------------------------
# 5. PAGE ROUTING
# -----------------------------------------------------------------------------

# --- PROFILE PAGE ---
if page == "Profile":
    st.title("👤 User Profile & Target Settings")
    st.markdown("<div class='pink-card'>", unsafe_allow_html=True)

    with st.form("profile_form"):
        name = st.text_input("Name", value=st.session_state.user_profile["name"])
        age = st.number_input("Age", min_value=5, max_value=100, value=int(st.session_state.user_profile["age"]))
        reason = st.text_area("Reason for Learning", value=st.session_state.user_profile["reason"])
        
        col1, col2 = st.columns(2)
        with col1:
            target_lang = st.selectbox(
                "Target Language (120 Available)", 
                LANGUAGES, 
                index=LANGUAGES.index(st.session_state.user_profile["target_lang"])
            )
            level = st.selectbox(
                "Learning Level", 
                ["Beginner", "Intermediate", "Pro"],
                index=["Beginner", "Intermediate", "Pro"].index(st.session_state.user_profile["level"])
            )
        with col2:
            daily_limit = st.slider("Daily Word Goal", min_value=3, max_value=30, value=int(st.session_state.user_profile["daily_limit"]))

        submit = st.form_submit_button("Save Profile")

        if submit:
            st.session_state.user_profile.update({
                "name": name,
                "age": age,
                "reason": reason,
                "target_lang": target_lang,
                "level": level,
                "daily_limit": daily_limit
            })
            st.success("Profile updated successfully!")
    st.markdown("</div>", unsafe_allow_html=True)

# --- DASHBOARD & VOCABULARY PAGE ---
elif page == "Dashboard & Vocab":
    st.title(f"📖 Vocabulary Vault ({st.session_state.user_profile['target_lang']})")
    
    tab1, tab2 = st.tabs(["Browse Vocabulary", "Add Custom Word"])
    
    with tab1:
        vocab_list = get_current_vocab()
        filtered_vocab = [
            v for v in vocab_list 
            if v["level"] == st.session_state.user_profile["level"] or st.session_state.user_profile["level"] == "Pro"
        ]

        for idx, item in enumerate(filtered_vocab):
            st.markdown("<div class='pink-card'>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([3, 3, 2])
            
            with col1:
                st.subheader(item["word"])
                st.write(f"**Meaning:** {item['meaning']}")
            
            with col2:
                st.write(f"*Example:* {item['sample']}")
                st.caption(f"Level: {item['level']}")
                
            with col3:
                if st.button(f"🔊 Listen", key=f"audio_{idx}"):
                    play_audio(item["word"])
                    if st.session_state.user_profile["words_today"] < st.session_state.user_profile["daily_limit"]:
                        st.session_state.user_profile["words_today"] += 1
            
            st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='pink-card'>", unsafe_allow_html=True)
        st.subheader("➕ Add Custom Word to Library")
        with st.form("custom_word_form"):
            new_word = st.text_input("Word")
            new_meaning = st.text_input("Meaning")
            new_sample = st.text_input("Example Sentence")
            new_level = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Pro"])
            
            if st.form_submit_button("Add Word"):
                if new_word and new_meaning:
                    st.session_state.custom_vocab.append({
                        "word": new_word,
                        "meaning": new_meaning,
                        "sample": new_sample,
                        "level": new_level
                    })
                    st.success(f"Added '{new_word}' to your custom vocabulary!")
                else:
                    st.error("Please fill in both the Word and Meaning fields.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- DAILY GAME TASKS ---
elif page == "Daily Game Tasks":
    st.title("🎮 Daily Interactive Challenges")
    st.write("Complete interactive mini-games to boost your leaderboard score!")

    vocab = get_current_vocab()
    selected_item = random.choice(vocab)

    tab1, tab2 = st.tabs(["Multiple Choice Quiz", "Word Unscramble"])

    with tab1:
        st.markdown("<div class='pink-card'>", unsafe_allow_html=True)
        st.subheader(f"What is the meaning of: **{selected_item['word']}**?")
        
        options = [selected_item["meaning"], "House", "Journey", "Happiness"]
        random.shuffle(options)

        choice = st.radio("Select the correct answer:", options, key="mcq")
        if st.button("Submit Answer"):
            if choice == selected_item["meaning"]:
                st.balloons()
                st.success("Correct! +10 Points added to Leaderboard.")
                st.session_state.user_profile["score"] += 10
            else:
                st.error(f"Incorrect! The correct answer was: {selected_item['meaning']}")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='pink-card'>", unsafe_allow_html=True)
        target_word = selected_item["word"]
        scrambled = "".join(random.sample(target_word, len(target_word)))
        
        st.subheader(f"Unscramble the word: **{scrambled.upper()}**")
        st.write(f"Hint: Means '{selected_item['meaning']}'")
        
        user_guess = st.text_input("Your Guess:", key="scramble_input")
        if st.button("Check Word"):
            if user_guess.strip().lower() == target_word.lower():
                st.success("Spot on! +15 Points added!")
                st.session_state.user_profile["score"] += 15
            else:
                st.error("Try again!")
        st.markdown("</div>", unsafe_allow_html=True)

# --- PRONUNCIATION & VOICE STUDIO ---
elif page == "Pronunciation & Voice Studio":
    st.title("🎙️ Pronunciation & Speech Studio")
    st.write("Listen to the target word, record your own voice, and practice matching the pronunciation!")

    st.markdown("<div class='pink-card'>", unsafe_allow_html=True)
    vocab = get_current_vocab()
    practice_word = st.selectbox("Select a word to practice:", [v["word"] for v in vocab])

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Reference Audio")
        if st.button("🔊 Play Native Pronunciation"):
            play_audio(practice_word)

    with col2:
        st.subheader("2. Voice Recorder")
        st.write("Click below to record your voice:")
        audio_bytes = audio_recorder(text="Click to Record", recording_color="#FF1493", neutral_color="#FF69B4")
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            st.success("Audio captured! Play back your voice above to compare with native pronunciation.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- GRAMMAR & TRANSLATION PAGE ---
elif page == "Grammar & Translation":
    st.title("🔍 Live Translation & Grammar Checker")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='pink-card'>", unsafe_allow_html=True)
        st.subheader("🌐 Live Translator")
        source_text = st.text_area("Enter text to translate:")
        if st.button("Translate Text"):
            if source_text:
                result = translate_text(source_text, st.session_state.user_profile["target_lang"])
                st.info(f"**Translation ({st.session_state.user_profile['target_lang']}):**\n\n{result}")
                play_audio(result)
            else:
                st.warning("Please enter text to translate.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='pink-card'>", unsafe_allow_html=True)
        st.subheader("✍️ Rule-Based Grammar Check")
        sentence = st.text_area("Type a sentence to verify structure:")
        if st.button("Check Grammar"):
            if sentence:
                if len(sentence.split()) < 3:
                    st.warning("Sentence is brief. Ensure complete subject-verb agreement.")
                elif not sentence[0].isupper() or sentence[-1] not in [".", "!", "?"]:
                    st.error("Grammar Suggestion: Ensure initial capitalization and terminal punctuation.")
                else:
                    st.success("Grammar structure looks good! Syntax verified.")
            else:
                st.warning("Please enter a sentence.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- PERFORMANCE ANALYTICS PAGE ---
elif page == "Performance Analytics":
    st.title("📊 Performance Analytics & Trends")
    st.markdown("<div class='pink-card'>", unsafe_allow_html=True)
    st.subheader("Weekly Activity Summary")

    df_activity = st.session_state.activity_log
    fig = px.bar(
        df_activity, 
        x="Day", 
        y="Words Learned", 
        title="Words Learned Per Day",
        color_discrete_sequence=["#FF69B4"]
    )
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    fig_points = px.line(
        df_activity, 
        x="Day", 
        y="Quiz Points", 
        title="Points Growth",
        markers=True,
        color_discrete_sequence=["#D81B60"]
    )
    fig_points.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_points, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# --- AI PERFORMANCE REVIEW PAGE ---
elif page == "AI Performance Review":
    st.title("🤖 AI Learning Coach")
    st.markdown("<div class='pink-card'>", unsafe_allow_html=True)

    profile = st.session_state.user_profile
    st.subheader(f"Analysis for {profile['name']}")
    
    st.write(f"- **Target Language:** {profile['target_lang']}")
    st.write(f"- **Current Level:** {profile['level']}")
    st.write(f"- **Daily Progress:** {profile['words_today']}/{profile['daily_limit']} Words reviewed")

    st.markdown("---")
    st.subheader("💡 Tailored Feedback")

    if profile["words_today"] >= profile["daily_limit"]:
        st.success("🌟 Outstanding performance! Daily goal reached.")
    else:
        st.info(f"🎯 Complete {profile['daily_limit'] - profile['words_today']} more words to hit today's target.")

    if profile["level"] == "Beginner":
        st.write("📌 Recommendations: Focus on building core vocabulary and standard daily greetings.")
    elif profile["level"] == "Intermediate":
        st.write("📌 Recommendations: Expand sentence construction and practice interactive game quizzes.")
    else:
        st.write("📌 Recommendations: Practice speech audio recording and advanced word definitions.")

    st.markdown("</div>", unsafe_allow_html=True)

# --- LEADERBOARD PAGE ---
elif page == "Leaderboard":
    st.title("🏆 Leaderboard")
    st.markdown("<div class='pink-card'>", unsafe_allow_html=True)

    df = st.session_state.leaderboard
    df.loc[df["Name"] == st.session_state.user_profile["name"], "Score"] = st.session_state.user_profile["score"]
    df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)
    df["Rank"] = df.index + 1

    st.dataframe(df, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
