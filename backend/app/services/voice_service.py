"""
Voice Service for EduPath AI.
Powers human-like, real-time conversational AI voice interactions:
- Natural spoken dialogue tailored for real-time speech (no robotic markdown or tables).
- Conversation context memory across multiple turns.
- Multilingual support: English (US & Indian), Hindi, and Telugu.
- Ultra-realistic neural speech synthesis using edge-tts.
"""

import io
import re
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import edge_tts
from app.core.config import settings

logger = logging.getLogger("edupath.voice")

VOICE_MAP = {
    "en": "en-US-JennyNeural",
    "en-US": "en-US-JennyNeural",
    "en-IN": "en-IN-NeerjaNeural",
    "te": "te-IN-ShrutiNeural",
    "hi": "hi-IN-SwaraNeural",
    "ta": "ta-IN-PallaviNeural",
    "kn": "kn-IN-SapnaNeural",
    "ml": "ml-IN-SobhanaNeural",
    "bn": "bn-IN-TanishaaNeural",
    "mr": "mr-IN-AarohiNeural",
    "ur": "ur-IN-GulNeural",
    "es": "es-ES-ElviraNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-TanjaNeural",
    "ja": "ja-JP-NanamiNeural",
    "zh": "zh-CN-XiaoxiaoNeural"
}

AVAILABLE_VOICES = [
    {"id": "en-US-JennyNeural", "name": "Jenny (US English, Natural)", "language": "en", "gender": "Female"},
    {"id": "en-US-GuyNeural", "name": "Guy (US English, Natural)", "language": "en", "gender": "Male"},
    {"id": "en-IN-NeerjaNeural", "name": "Neerja (Indian English)", "language": "en-IN", "gender": "Female"},
    {"id": "en-IN-PrabhatNeural", "name": "Prabhat (Indian English)", "language": "en-IN", "gender": "Male"},
    {"id": "te-IN-ShrutiNeural", "name": "Shruti (Telugu, Natural)", "language": "te", "gender": "Female"},
    {"id": "te-IN-MohanNeural", "name": "Mohan (Telugu, Natural)", "language": "te", "gender": "Male"},
    {"id": "hi-IN-SwaraNeural", "name": "Swara (Hindi, Natural)", "language": "hi", "gender": "Female"},
    {"id": "hi-IN-MadhurNeural", "name": "Madhur (Hindi, Natural)", "language": "hi", "gender": "Male"},
    {"id": "ta-IN-PallaviNeural", "name": "Pallavi (Tamil, Natural)", "language": "ta", "gender": "Female"},
    {"id": "ta-IN-ValluvarNeural", "name": "Valluvar (Tamil, Natural)", "language": "ta", "gender": "Male"},
    {"id": "kn-IN-SapnaNeural", "name": "Sapna (Kannada, Natural)", "language": "kn", "gender": "Female"},
    {"id": "kn-IN-GaganNeural", "name": "Gagan (Kannada, Natural)", "language": "kn", "gender": "Male"},
    {"id": "ml-IN-SobhanaNeural", "name": "Sobhana (Malayalam, Natural)", "language": "ml", "gender": "Female"},
    {"id": "ml-IN-MidhunNeural", "name": "Midhun (Malayalam, Natural)", "language": "ml", "gender": "Male"},
    {"id": "bn-IN-TanishaaNeural", "name": "Tanishaa (Bengali, Natural)", "language": "bn", "gender": "Female"},
    {"id": "bn-IN-BashkarNeural", "name": "Bashkar (Bengali, Natural)", "language": "bn", "gender": "Male"},
    {"id": "mr-IN-AarohiNeural", "name": "Aarohi (Marathi, Natural)", "language": "mr", "gender": "Female"},
    {"id": "mr-IN-ManoharNeural", "name": "Manohar (Marathi, Natural)", "language": "mr", "gender": "Male"},
    {"id": "ur-IN-GulNeural", "name": "Gul (Urdu, Natural)", "language": "ur", "gender": "Female"},
    {"id": "ur-IN-SalmanNeural", "name": "Salman (Urdu, Natural)", "language": "ur", "gender": "Male"},
    {"id": "es-ES-ElviraNeural", "name": "Elvira (Spanish, Castilian)", "language": "es", "gender": "Female"},
    {"id": "es-ES-AlvaroNeural", "name": "Alvaro (Spanish, Castilian)", "language": "es", "gender": "Male"},
    {"id": "fr-FR-DeniseNeural", "name": "Denise (French, Natural)", "language": "fr", "gender": "Female"},
    {"id": "fr-FR-HenriNeural", "name": "Henri (French, Natural)", "language": "fr", "gender": "Male"},
    {"id": "de-DE-TanjaNeural", "name": "Tanja (German, Natural)", "language": "de", "gender": "Female"},
    {"id": "de-DE-ChristophNeural", "name": "Christoph (German, Natural)", "language": "de", "gender": "Male"},
    {"id": "ja-JP-NanamiNeural", "name": "Nanami (Japanese, Natural)", "language": "ja", "gender": "Female"},
    {"id": "ja-JP-KeitaNeural", "name": "Keita (Japanese, Natural)", "language": "ja", "gender": "Male"},
    {"id": "zh-CN-XiaoxiaoNeural", "name": "Xiaoxiao (Mandarin Chinese)", "language": "zh", "gender": "Female"},
    {"id": "zh-CN-YunxiNeural", "name": "Yunxi (Mandarin Chinese)", "language": "zh", "gender": "Male"}
]

LANGUAGE_METADATA = [
    {"code": "en", "name": "English (US / Global)", "native": "English"},
    {"code": "en-IN", "name": "English (India)", "native": "Indian English"},
    {"code": "te", "name": "Telugu", "native": "తెలుగు"},
    {"code": "hi", "name": "Hindi", "native": "हिन्दी"},
    {"code": "ta", "name": "Tamil", "native": "தமிழ்"},
    {"code": "kn", "name": "Kannada", "native": "ಕನ್ನಡ"},
    {"code": "ml", "name": "Malayalam", "native": "മലയാളം"},
    {"code": "bn", "name": "Bengali", "native": "বাংলা"},
    {"code": "mr", "name": "Marathi", "native": "मराठी"},
    {"code": "ur", "name": "Urdu", "native": "اردو"},
    {"code": "es", "name": "Spanish", "native": "Español"},
    {"code": "fr", "name": "French", "native": "Français"},
    {"code": "de", "name": "German", "native": "Deutsch"},
    {"code": "ja", "name": "Japanese", "native": "日本語"},
    {"code": "zh", "name": "Chinese (Mandarin)", "native": "中文"}
]

def detect_language(text: str, default: str = "en") -> str:
    """
    Automatically detects spoken/written language from character script unicode ranges.
    """
    if not text:
        return default
    # Telugu: U+0C00 - U+0C7F
    if re.search(r'[\u0C00-\u0C7F]', text):
        return "te"
    # Tamil: U+0B80 - U+0BFF
    if re.search(r'[\u0B80-\u0BFF]', text):
        return "ta"
    # Kannada: U+0C80 - U+0CFF
    if re.search(r'[\u0C80-\u0CFF]', text):
        return "kn"
    # Malayalam: U+0D00 - U+0D7F
    if re.search(r'[\u0D00-\u0D7F]', text):
        return "ml"
    # Bengali: U+0980 - U+09FF
    if re.search(r'[\u0980-\u09FF]', text):
        return "bn"
    # Arabic / Urdu: U+0600 - U+06FF
    if re.search(r'[\u0600-\u06FF]', text):
        return "ur"
    # Japanese: Hiragana, Katakana U+3040 - U+30FF
    if re.search(r'[\u3040-\u30FF]', text):
        return "ja"
    # Chinese: CJK ideographs U+4E00 - U+9FFF
    if re.search(r'[\u4E00-\u9FFF]', text):
        return "zh"
    # Devanagari (Hindi vs Marathi): U+0900 - U+097F
    if re.search(r'[\u0900-\u097F]', text):
        # Check for Marathi specific markers
        if re.search(r'\b(आहे|नाही|करा|म्हणजे|काय)\b', text):
            return "mr"
        return "hi"
    return default

def clean_text_for_speech(text: str) -> str:
    """
    Cleans markdown formatting, citations, and symbols so text sounds
    completely natural when converted to speech.
    """
    if not text:
        return ""
    # Remove markdown headers (### Header)
    t = re.sub(r"#+\s*", "", text)
    # Remove bold and italic markdown (**text** or *text* or _text_)
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"\*([^*]+)\*", r"\1", t)
    t = re.sub(r"__([^_]+)__", r"\1", t)
    t = re.sub(r"_([^_]+)_", r"\1", t)
    # Remove code blocks and inline backticks
    t = re.sub(r"```[\s\S]*?```", "Here is a code example: ", t)
    t = re.sub(r"`([^`]+)`", r"\1", t)
    # Remove markdown links [title](url) -> title
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    # Remove bullet markers (- item or * item)
    t = re.sub(r"^\s*[-*•]\s*", "", t, flags=re.MULTILINE)
    # Remove numbered bullets (1. item)
    t = re.sub(r"^\s*\d+\.\s*", "", t, flags=re.MULTILINE)
    # Replace math symbols with spoken equivalents
    t = t.replace("O(1)", "O of 1")
    t = t.replace("O(n)", "O of n")
    t = t.replace("O(N)", "O of N")
    t = t.replace("O(n log n)", "O of n log n")
    t = t.replace("O(N log N)", "O of N log N")
    t = t.replace("O(n^2)", "O of n squared")
    t = t.replace("!=", " not equal to ")
    t = t.replace("==", " equals ")
    t = t.replace(">=", " greater than or equal to ")
    t = t.replace("<=", " less than or equal to ")
    # Normalize multiple whitespace and newlines
    t = re.sub(r"\n+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


class VoiceService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.is_configured = bool(self.api_key and len(self.api_key.strip()) > 10)
        if self.is_configured:
            try:
                genai.configure(api_key=self.api_key)
                self.chat_model = genai.GenerativeModel("gemini-1.5-flash")
                logger.info("VoiceService: Gemini API configured for voice dialogue.")
            except Exception as e:
                logger.warning(f"VoiceService: Gemini config failed: {e}. Fallback active.")
                self.is_configured = False
        else:
            logger.info("VoiceService: GEMINI_API_KEY not set. Using conversational intelligent fallback.")
        self.voice_map = VOICE_MAP

    async def generate_conversational_reply(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        subject_name: Optional[str] = None,
        language: str = "en"
    ) -> str:
        """
        Generates human-like, conversational response tailored for speech:
        - Concise: 2 to 4 spoken sentences per turn.
        - Engaging, warm, and natural.
        - Remembers context from previous conversation turns.
        - Never outputs markdown tables or unpronounceable syntax.
        - Supports English, Hindi, and Telugu.
        """
        user_msg = message.strip()
        history = conversation_history or []

        # Detect language dynamically if set to auto or message clearly indicates script
        effective_lang = language
        if language in ["auto", "en", ""]:
            detected = detect_language(user_msg, default="en")
            if detected != "en":
                effective_lang = detected

        LANG_GUIDELINES = {
            "en": "Respond in natural spoken English with an encouraging academic tone.",
            "en-IN": "Respond in natural Indian English with clear pronunciation and respectful academic cadence.",
            "te": "Respond in natural, fluent conversational Telugu (Telugu script). Keep core technical terms in English phonetics.",
            "hi": "Respond in natural, fluent conversational Hindi (Devanagari script). Keep core technical terms in English phonetics.",
            "ta": "Respond in natural, fluent conversational Tamil (Tamil script). Keep core technical terms in English phonetics.",
            "kn": "Respond in natural, fluent conversational Kannada (Kannada script). Keep core technical terms in English phonetics.",
            "ml": "Respond in natural, fluent conversational Malayalam (Malayalam script). Keep core technical terms in English phonetics.",
            "bn": "Respond in natural, fluent conversational Bengali (Bengali script). Keep core technical terms in English phonetics.",
            "mr": "Respond in natural, fluent conversational Marathi (Devanagari script). Keep core technical terms in English phonetics.",
            "ur": "Respond in natural, fluent conversational Urdu (Nastaliq/Urdu script). Keep core technical terms in English phonetics.",
            "es": "Respond in natural, fluent conversational Spanish with an academic, encouraging tone.",
            "fr": "Respond in natural, fluent conversational French with an academic, encouraging tone.",
            "de": "Respond in natural, fluent conversational German with precise, clear academic phrasing.",
            "ja": "Respond in natural, polite conversational Japanese (Desu/Masu form) with clear technical vocabulary.",
            "zh": "Respond in natural, standard Mandarin Chinese (Simplified Chinese script) with clear academic explanations."
        }
        lang_instruction = LANG_GUIDELINES.get(effective_lang, LANG_GUIDELINES["en"])

        subject_context = f"The student is currently studying: {subject_name}." if subject_name else "The student is exploring computer science and academic topics."

        system_prompt = f"""You are the EduPath AI Academic Voice Mentor – an ultra-friendly, intelligent, human-like voice assistant similar to ChatGPT Voice Mode.

CRITICAL VOICE CONVERSATION RULES:
1. You are speaking through real-time voice synthesis. Every word you write will be read aloud to the student.
2. DO NOT USE markdown formatting, bold asterisks (**), bullet dashes, numbered lists, or tables.
3. Keep your answers concise, engaging, and spoken-friendly (typically 2 to 4 sentences). If a concept is complex, explain the first step simply, and ask if they'd like to hear the next step.
4. Understand conversational continuity: if the user asks a follow-up like "Can you give an example?" or "Why does that happen?", refer directly to what was previously discussed without asking them to repeat.
5. If the user greets you (e.g. "Hi", "Hello", "How are you?"), greet them warmly and ask what they'd like to learn or practice today.
6. If the user asks for a practice question or interview question, give ONE clear question verbally and ask for their thoughts.
7. {subject_context}
8. Language rule: {lang_instruction}
"""

        # Format history into conversational transcript
        history_lines = []
        for h in history[-8:]:  # Keep last 8 turns for conversational memory
            role = "Student" if h.get("sender_role") == "user" or h.get("role") == "user" else "AI"
            history_lines.append(f"{role}: {h.get('content', '')}")

        formatted_history = "\n".join(history_lines) if history_lines else "No previous messages."

        full_prompt = f"""{system_prompt}

CONVERSATION HISTORY:
{formatted_history}

Student: {user_msg}
AI:"""

        if self.is_configured:
            try:
                response = self.chat_model.generate_content(full_prompt)
                reply = clean_text_for_speech(response.text.strip())
                if reply:
                    return reply
            except Exception as e:
                logger.error(f"VoiceService: Gemini API error: {e}. Falling back to conversational rules.")

        # Intelligent conversational fallback
        return self._fallback_conversational_reply(user_msg, history, subject_name, language)

    def _fallback_conversational_reply(
        self,
        message: str,
        history: List[Dict[str, str]],
        subject_name: Optional[str],
        language: str
    ) -> str:
        """
        High quality, context-aware conversational fallback engine.
        Handles greetings, follow-ups, examples, questions, and concept explanations.
        """
        msg_lower = message.lower().strip()
        last_ai_msg = ""
        for h in reversed(history):
            if h.get("sender_role") == "assistant" or h.get("role") == "assistant":
                last_ai_msg = h.get("content", "").lower()
                break

        # Check for Hindi
        if language == "hi":
            if any(g in msg_lower for g in ["hi", "hello", "namaste", "नमस्ते", "hey"]):
                return f"नमस्ते! मैं आपका EduPath AI वॉइस असिस्टेंट हूँ। आज आप {subject_name or 'कंप्यूटर साइंस'} में क्या समझना या प्रैक्टिस करना चाहेंगे?"
            if "example" in msg_lower or "उदाहरण" in msg_lower:
                return "ज़रूर! मान लीजिए आपके पास एक डिक्शनरी है। जब आप कोई शब्द ढूँढते हैं, तो आप पहले पन्ने से शुरू करने के बजाय बीच से खोलते हैं। यही बाइनरी सर्च का मूल विचार है। क्या यह उदाहरण स्पष्ट है?"
            return f"यह बहुत अच्छा सवाल है। {subject_name or 'कंप्यूटर साइंस'} में यह कॉन्सेप्ट सिस्टम की एफिशिएंसी और डेटा फ्लो को समझने के लिए बहुत ज़रूरी है। क्या आप चाहते हैं कि मैं इसे एक आसान रियल-लाइफ उदाहरण से समझाऊं?"

        # Check for Telugu
        if language == "te":
            if any(g in msg_lower for g in ["hi", "hello", "namaskaram", "నమస్కారం", "hey"]):
                return f"నమస్కారం! నేను మీ EduPath AI వాయిస్ అసిస్టెంట్ ని. ఈరోజు మీరు {subject_name or 'కంప్యూటర్ సైన్స్'} లో ఏమి నేర్చుకోవాలనుకుంటున్నారు?"
            if "example" in msg_lower or "ఉదాహరణ" in msg_lower:
                return "ఖచ్చితంగా! ఒక పెద్ద లైబ్రరీ లో పుస్తకాన్ని వెతకడం అనుకోండి. ప్రతి పుస్తకాన్ని ఒక్కొక్కటిగా చూడటానికి బదులుగా, వర్గాల వారీగా వెతకడం ద్వారా సమయం ఆదా అవుతుంది. ఇదే ఆల్గారిథమ్స్ లో ఆప్టిమైజేషన్. ఇది మీకు అర్థమైందా?"
            return f"చాలా మంచి ప్రశ్న. {subject_name or 'కంప్యూటర్ సైన్స్'} లో ఈ కాన్సెప్ట్ చాలా ప్రాముఖ్యమైనది. దీని గురించి ఒక చిన్న ప్రాక్టికల్ ఉదాహరణతో వివరించమంటారా?"

        # English (Default)
        # 1. Greetings
        if any(msg_lower.startswith(g) for g in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
            subj_hint = f" studying {subject_name}" if subject_name else ""
            return f"Hello there! I am your EduPath AI Voice Assistant. I am ready to help you with concepts, interview prep, or practice questions{subj_hint}. What would you like to explore today?"

        # 2. How are you / identity
        if "how are you" in msg_lower:
            return "I am doing great and excited to help you learn! What topic or concept are you currently working on?"
        if "who are you" in msg_lower or "what can you do" in msg_lower:
            return "I am EduPath AI's conversational voice tutor. You can speak with me naturally to understand difficult subjects, ask follow-up questions, get simple analogies, or practice technical interview problems. What shall we start with?"

        # 3. Follow-up: "Can you give an example?" or "another example"
        if any(phrase in msg_lower for phrase in ["another example", "more examples", "give me an example", "one more example", "can you give an example"]):
            if "machine learning" in last_ai_msg or "data" in last_ai_msg:
                return "Here is another great example. Think of your email inbox. When you mark certain messages as spam, the system observes patterns in words and sender addresses, and automatically filters future spam. That is supervised learning in daily life. Does that make sense?"
            elif "operating system" in last_ai_msg or "process" in last_ai_msg:
                return "Consider a kitchen chef. The chef is the CPU, and each recipe being prepared is a process. When a dish needs to bake in the oven, the chef works on chopping vegetables rather than waiting idly. That is CPU scheduling and non-blocking I/O. Would you like to dive deeper into scheduling algorithms?"
            else:
                return "Sure! Imagine a phone directory. If you look up a name starting with S, you do not start reading from page 1. Instead, you jump straight to the middle and narrow down your search. That is how logarithmic search time works in binary search. How does that sound?"

        # 4. Follow-up: "Why?" or "Explain more" or "Tell me more"
        if any(phrase in msg_lower for phrase in ["why", "tell me more", "explain more", "go on", "what next", "continue"]):
            return "Building on what we just discussed, the key reason this is used is scalability. When data grows from thousands to billions of records, naive methods slow to a crawl, while optimized algorithms keep responses fast and reliable. Would you like to see how this is implemented in code?"

        # 5. Practice question request
        if any(phrase in msg_lower for phrase in ["practice question", "quiz me", "ask me a question", "test my knowledge", "interview question"]):
            if subject_name and "operating" in subject_name.lower():
                return "Here is a classic interview question for you: What is the key difference between a process and a thread, and how does context switching overhead differ between them? Take your time and give it your best shot!"
            elif subject_name and "database" in subject_name.lower() or "dbms" in msg_lower:
                return "Here is a great question for you: Can you explain why a database index speeds up SELECT queries but might slow down INSERT or UPDATE operations? Tell me what you think!"
            else:
                return "Here is a question for you: When would you choose an array over a linked list in terms of memory cache locality and access time? Tell me your thoughts!"

        # 6. Specific Technical Concepts
        if "machine learning" in msg_lower:
            return "Machine learning is a branch of artificial intelligence where computers learn patterns from data instead of following rigid, hardcoded rules. For example, photo apps use machine learning to recognize your friends' faces automatically. Would you like me to explain the difference between supervised and unsupervised learning?"

        if "operating system" in msg_lower or "deadlock" in msg_lower:
            return "In operating systems, a deadlock happens when two or more processes are permanently stuck because each is holding a resource that the other needs. Think of four cars arriving simultaneously at a narrow four-way intersection where no one can move. Would you like to hear the four conditions required for a deadlock to happen?"

        if "database" in msg_lower or "acid" in msg_lower:
            return "In database systems, ACID properties guarantee that database transactions are processed reliably. For example, if you transfer money between two bank accounts, ACID ensures that money is not deducted from one account without successfully reaching the other. Would you like to explore what each letter in ACID stands for?"

        # General conceptual response
        subj_phrase = f"in {subject_name}" if subject_name else "in technical learning"
        return f"That is a great question {subj_phrase}. At its core, it is about balancing performance, memory, and simplicity in system design. Would you like me to walk you through a step-by-step example, or should we look at a real-world scenario?"

    async def synthesize_speech(
        self,
        text: str,
        language: str = "en",
        voice: Optional[str] = None
    ) -> bytes:
        """
        Synthesizes text into high-quality MP3 audio using edge-tts.
        Returns raw MP3 audio bytes.
        """
        clean_text = clean_text_for_speech(text)
        if not clean_text:
            clean_text = "I am listening."

        selected_voice = voice or VOICE_MAP.get(language, "en-US-JennyNeural")

        try:
            communicate = edge_tts.Communicate(clean_text, selected_voice)
            audio_buffer = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer.write(chunk["data"])
            audio_buffer.seek(0)
            return audio_buffer.read()
        except Exception as e:
            logger.error(f"VoiceService: edge-tts synthesis failed: {e}")
            raise e

    def get_available_voices(self) -> List[Dict[str, str]]:
        return AVAILABLE_VOICES


voice_service = VoiceService()
