import base64
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Conversation, ChatMessage, Subject
from app.services.voice_service import voice_service, clean_text_for_speech, VOICE_MAP, LANGUAGE_METADATA

router = APIRouter(prefix="/voice", tags=["Conversational AI Voice Agent"])

class VoiceChatTurn(BaseModel):
    role: str  # user or assistant
    content: str

class VoiceChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    subject_id: Optional[str] = None
    language: str = "en"  # en, hi, te, ta, kn, ml, bn, mr, ur, es, fr, de, ja, zh
    voice: Optional[str] = None
    synthesize_audio: bool = True
    history: Optional[List[VoiceChatTurn]] = None

class VoiceChatResponse(BaseModel):
    conversation_id: str
    reply_text: str
    language: str
    voice: str
    audio_base64: Optional[str] = None
    audio_stream_url: str

class VoiceSynthesizeRequest(BaseModel):
    text: str
    language: str = "en"
    voice: Optional[str] = None

class VoiceInfo(BaseModel):
    id: str
    name: str
    language: str
    gender: str

class LanguageInfo(BaseModel):
    code: str
    name: str
    native: str

@router.get("/languages", response_model=List[LanguageInfo])
async def get_supported_languages():
    """
    Returns the 14 supported languages with native names.
    """
    return LANGUAGE_METADATA

@router.get("/voices", response_model=List[VoiceInfo])
async def get_available_voices():
    """
    Returns available neural voice models across all supported languages.
    """
    return voice_service.get_available_voices()

@router.post("/chat", response_model=VoiceChatResponse)
async def voice_chat(
    req: VoiceChatRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Real-time conversational voice interaction:
    1. Understands student speech, context, follow-ups, and academic intent.
    2. Generates human-like, spoken-friendly responses in English, Hindi, or Telugu.
    3. Synthesizes ultra-realistic neural speech into audio bytes.
    4. Persists the conversation in the student's dashboard history.
    """
    user_msg = req.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Voice message cannot be empty.")

    # 1. Resolve subject if provided
    subject_name = None
    if req.subject_id:
        sub_stmt = select(Subject).where(Subject.id == req.subject_id)
        sub_res = await session.execute(sub_stmt)
        subj = sub_res.scalar_one_or_none()
        if subj:
            subject_name = subj.name

    # 2. Resolve or create Conversation
    conv = None
    if req.conversation_id:
        c_stmt = select(Conversation).where(
            Conversation.id == req.conversation_id,
            Conversation.user_id == current_user.id
        )
        c_res = await session.execute(c_stmt)
        conv = c_res.scalar_one_or_none()

    if not conv:
        snippet = user_msg[:35] + "..." if len(user_msg) > 35 else user_msg
        conv = Conversation(
            user_id=current_user.id,
            subject_id=req.subject_id,
            title=f"Voice: {snippet}"
        )
        session.add(conv)
        await session.flush()

    # 3. Retrieve recent conversation history from DB if not passed
    history_turns = []
    if req.history:
        for turn in req.history:
            history_turns.append({"role": turn.role, "content": turn.content})
    else:
        # Load last 6 messages from DB
        msg_stmt = select(ChatMessage).where(
            ChatMessage.conversation_id == conv.id
        ).order_by(ChatMessage.created_at.desc()).limit(6)
        msg_res = await session.execute(msg_stmt)
        db_msgs = list(reversed(msg_res.scalars().all()))
        for m in db_msgs:
            history_turns.append({"role": m.sender_role, "content": m.content})

    # 4. Generate human-like conversational voice reply
    reply_text = await voice_service.generate_conversational_reply(
        message=user_msg,
        conversation_history=history_turns,
        subject_name=subject_name,
        language=req.language
    )

    # 5. Persist User and Assistant messages to database
    user_chat_msg = ChatMessage(
        conversation_id=conv.id,
        sender_role="user",
        content=user_msg
    )
    ai_chat_msg = ChatMessage(
        conversation_id=conv.id,
        sender_role="assistant",
        content=reply_text
    )
    session.add(user_chat_msg)
    session.add(ai_chat_msg)
    await session.commit()

    # 6. Synthesize speech if requested
    audio_base64 = None
    selected_voice = req.voice or VOICE_MAP.get(req.language, "en-US-JennyNeural")
    if req.synthesize_audio:
        try:
            audio_bytes = await voice_service.synthesize_speech(
                text=reply_text,
                language=req.language,
                voice=selected_voice
            )
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        except Exception as e:
            # If TTS generation encounters temporary network glitch, client can use browser synthesis
            audio_base64 = None

    audio_stream_url = f"/api/voice/synthesize?text={reply_text[:100]}&language={req.language}"

    return VoiceChatResponse(
        conversation_id=conv.id,
        reply_text=reply_text,
        language=req.language,
        voice=selected_voice,
        audio_base64=audio_base64,
        audio_stream_url=audio_stream_url
    )

@router.post("/synthesize")
async def synthesize_audio(
    req: VoiceSynthesizeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Converts text to MP3 audio stream using neural voices.
    """
    clean_text = clean_text_for_speech(req.text)
    if not clean_text:
        clean_text = "I am ready."

    try:
        audio_bytes = await voice_service.synthesize_speech(
            text=clean_text,
            language=req.language,
            voice=req.voice
        )
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis error: {str(e)}"
        )
