import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = True

DB_HOST = os.environ.get("DB_HOST_TEST") if DEBUG else os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT_TEST") if DEBUG else os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME_TEST") if DEBUG else os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER_TEST") if DEBUG else os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS_TEST") if DEBUG else os.environ.get("DB_PASS").replace("\n", "").replace(" ", "")

BOT_TOKEN = os.environ.get("BOT_TOKEN")

ADMIN_ID = os.environ.get("ADMIN_ID")
MODERATOR_ID = os.environ.get("MODERATOR_ID")
TECH_SUPPORT_ID = os.environ.get("TECH_SUPPORT_ID")

OWNER_IDS = list(map(int, os.environ.get("OWNER_IDS").split("_")))
