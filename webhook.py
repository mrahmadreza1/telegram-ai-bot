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
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(
                chat_id=channel,
                user_id=user_id
            )

            print(
                f"CHANNEL: {channel} | "
                f"USER: {user_id} | "
                f"STATUS: {member.status}"
            )

            if member.status not in ["member", "administrator", "creator"]:
                return False

        except Exception as e:
            print(
                f"MEMBERSHIP ERROR: {channel} | {e}"
            )
            return False

    return True


async def send_formatted_message(chat_id, text):

    parts = re.split(
        r"```(?:python)?\s*\n?(.*?)```",
        text,
        flags=re.DOTALL
    )

    for i, part in enumerate(parts):

        if not part.strip():
            continue

        # CODE
        if i % 2 == 1:

            code = html.escape(part.strip())

            for start in range(0, len(code), 3500):

                chunk = code[start:start + 3500]

                await bot.send_message(
                    chat_id=chat_id,
                    text=f"<pre>{chunk}</pre>",
                    parse_mode="HTML"
                )

        # NORMAL TEXT
        else:

            message = html.escape(part.strip())

            for start in range(0, len(message), 3500):

                chunk = message[start:start + 3500]

                await bot.send_message(
                    chat_id=chat_id,
                    text=chunk,
                    parse_mode="HTML"
                )


@asynccontextmanager
async def lifespan(app: FastAPI):

    await bot.set_webhook(
        WEBHOOK_URL + "/webhook"
    )

    yield




app = FastAPI(lifespan=lifespan)

@app.get("/")
async def home():
    return {
        "status": "online",
        "message": "Telegram AI Bot is running"
    }
@app.post("/webhook")
async def webhook(req: Request):

    data = await req.json()

    update = telegram.Update.de_json(
        data,
        bot
    )



    # -----------------

    if update.callback_query:

        query = update.callback_query

        user_id = query.from_user.id

        if query.data == "check_membership":

            member_status = await is_user_member(user_id)

            if not member_status:

                await query.answer(
                    "❌ هنوز در هر دو کانال عضو نیستید.",
                    show_alert=True
                )

                return {"ok": True}

            await query.answer(
                "✅ عضویت شما تأیید شد!"
            )

            await bot.send_message(
                chat_id=user_id,
                text=(
                    "🎉 خوش آمدید!\n\n"
                    "عضویت شما با موفقیت تأیید شد. ✅\n"
                    "از حالا می‌توانید از ربات استفاده کنید. 🤖\n\n"
                    "پیام خود را ارسال کنید..."
                )
            )

            return {"ok": True}
# ---------------

    if update.message:

        user_id = update.message.chat.id
        text = update.message.text

        member_status = await is_user_member(user_id)

        print(
            f"USER: {user_id} | MEMBER: {member_status}"
        )

        if not member_status:

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "📢 عضویت در AIChatgptb",
                        url="https://t.me/AIChatgptb"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⚽ عضویت در Football Persian",
                        url="https://t.me/FotballPersian"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "✅ تأیید عضویت",
                        callback_data="check_membership"
                    )
                ]
            ])

            await bot.send_message(
                chat_id=user_id,
                text=(
                    "🚫 برای استفاده از ربات باید عضو هر دو کانال باشید.\n\n"
                    "📢 کانال اول: AIChatgptb\n"
                    "⚽ کانال دوم: Football Persian\n\n"
                    "بعد از عضویت دوباره پیام بدهید."
                ),
                reply_markup=keyboard
            )

            return {"ok": True}

        # فقط کاربران عضو به این قسمت می‌رسند
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