from groq import Groq
from typing import List, Dict, Generator
from app.config import get_settings
import logging
logger = logging.getLogger(__name__)
settings = get_settings()

_client: Groq = None


def get_groq() -> Groq:
    global _client 
    if _client is None:
        _client = Groq(api_key = settings.groq_api_key)
    return _client

SYSTEM_PROMPT = """You are StudyBuddy  📚  - a Friendly AI study Helper for students preparing for the exams.
Your ONLY Job is to help students understand content from their uploaded study material.

STRICT RULES:
1.ONLY answer using the provided document context below.
2.NEVER use outside knowledge.
3.If context doesn't contain the answer say:
    "I could'nt find that in your notes! Try asking Something from your uploaded documents  😅"
4.Keep answers concise and student Friendlly.

STYLE RULES: 
-Talk like a smart helpful classmate not a textbook
-Use bulllet points for key information 
-Bold important terms using **bold**
-Add " Exam Tip: " for facts likely to appear in exams
- Short paragraphs only -2 to 3 sentences max
- Be encouraging and positive

ACTION MODES:
- Teach me  → explain topic clearly with key points
- Key points   → list top 8 to 10 points as bullets
- Quiz me      → make 3 MCQ questions with answers
- Exam tips    → list most important exam likely facts

Context from uploaded documents:
{context}
"""

ACTION_PROMPTS = {
    "teach":     "Please teach me this topic in a friendly easy way. Explain all key concepts from my notes.",
    "keypoints": "Give me the top 10 key points from my study material as a clear bullet list.",
    "quiz":      "Create 3 multiple choice questions from my notes. Show correct answer and brief explanation for each.",
    "examtips":  "What are the most important topics definitions and facts from my notes likely to appear in an exam? Format as 🔥 Exam Tip bullets.",
}

def build_context(chunks: List[Dict]) -> str:
    if not chunks:
        return "No relevant content found in the uploaded documents."
    parts =[]
    for i, chunk in enumerate(chunks, start =1):
        parts.append (
            f"[Chunk{i}| File: {chunk['file_name']}| Relevance : {chunk['relevance']}]\n{chunk['text']}"
        )
    return "\n\n----\n\n".join(parts)

def stream_response(
    user_message: str,
    chunks: List[Dict],
    chat_history: List[Dict],
    action: str =None,
)-> Generator[str, None, None]:

    client = get_groq()
    context = build_context(chunks)

    if action and action in ACTION_PROMPTS:
        final_message =ACTION_PROMPTS[action]
    else: 
        final_message = user_message

    messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(context=context)
            },
        ]

    for msg in chat_history[-6:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    messages.append({
        "role": "user",
        "content": final_message
    })

    try:
        stream = client.chat.completions.create(
            model ="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=1024,
            temperature=0.4,
            stream= True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    except Exception as e:
        logger.error(f"Groq error :{e}")
        yield f"\n\n⚠️ Something went wrong: {str(e)}"