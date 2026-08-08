import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN=os.getenv("BOT_TOKEN")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
MODEL=os.getenv("MODEL")
WEBHOOK_URL=os.getenv("WEBHOOK_URL")
CHANNELS= [
    "@AIChatgptb",
    "@FotballPersian"
]
