from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
import telegram

from config import BOT_TOKEN, WEBHOOK_URL
from database import add_message, get_history
from groq_ai import ask_ai


bot = telegram.Bot(token=BOT_TOKEN)


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

        await bot.send_message(
            chat_id=user_id,
            text=answer
        )

    return {"ok": True}