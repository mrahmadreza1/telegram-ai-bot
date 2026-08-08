from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import re
import html

from config import BOT_TOKEN, WEBHOOK_URL,CHANNELS
from database import add_message, get_history
from groq_ai import ask_ai


bot = telegram.Bot(token=BOT_TOKEN)


async def is_user_member(user_id):
    for chanel in CHANNELS:
        try:
            member = await bot.get_chat_member(
                chat_id=chanel,
                user_id=user_id
            )
            if member.status not in [
                "member",
                "administrator",
                "creator"
            ]:
                return False
            

        except Exception:
            return False
    return True


async def send_formatted_message(chat_id, text):
    # پیدا کردن کدهای داخل ``` ```
    parts = re.split(
        r"```(?:python)?\s*\n?(.*?)```",
        text,
        flags=re.DOTALL
    )

    for i, part in enumerate(parts):

        if not part.strip():
            continue

        # بخش کد
        if i % 2 == 1:
            code = html.escape(part.strip())

            await bot.send_message(
                chat_id=chat_id,
                text=f"<pre>{code}</pre>",
                parse_mode="HTML"
            )

        # بخش متن معمولی
        else:
            message = html.escape(part.strip())

            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="HTML"
            )


@asynccontextmanager
async def lifespan(app: FastAPI):

    await bot.set_webhook(
        WEBHOOK_URL + "/webhook"
    )

    yield

    await bot.delete_webhook()


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def webhook(req: Request):

    data = await req.json()

    update = telegram.Update.de_json(
        data,
        bot
    )





    if update.message:

        user_id = update.message.chat.id
        text = update.message.text

        if not await is_user_member(user_id):
        
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                        "📢 عضویت در کانال",
                        url="https://t.me/AIChatgptb"
                    )],

                    [
                        InlineKeyboardButton(
                        "⚽ عضویت در Football Persian",
                        url="https://t.me/FootballPersian"
                        )
                    ]
                

                ])



                await bot.send_message(
                    chat_id=user_id,
                    ext="""
برای استفاده از ربات، لطفاً در هر دو کانال عضو شوید:

📢 کانال اول: AIChatgptb
⚽ کانال دوم: Football Persian

بعد از عضویت، دوباره پیام خود را ارسال کنید 👇
""",
                    reply_markup=keyboard
                )
        
                return {"ok": True}
        add_message(
            user_id,
            "user",
            text
        )

        history = get_history(user_id)

        answer = ask_ai(history)

        add_message(
            user_id,
            "assistant",
            answer
        )

        await send_formatted_message(
            user_id,
            answer
        )

    return {"ok": True}

