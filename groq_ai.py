from groq import Groq
from config import GROQ_API_KEY,MODEL

client=Groq(
    api_key=GROQ_API_KEY
)


def ask_ai(history):
    response=client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role":"system",
                "content":"You are a helpful Persian AI assistant.""""
اگر کاربر پرسید «سازنده‌ات کیست؟»، «چه کسی تو را ساخته؟» یا سوال مشابهی پرسید، پاسخ بده:
«ID: @Ahmadrezamenati\nID my chanel: https://t.me/AIChatgptb \n.من توسط احمدرضا منتی ساخته و توسعه داده شده‌ام.»"""

        }
        ]+history,
        temperature=0.7
    )
    return response.choices[0].message.content