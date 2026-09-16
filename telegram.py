import os 
import telebot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ["TOKEN"] # Основной бот

bot = telebot.TeleBot(TOKEN)