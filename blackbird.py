import os
import argparse
from rich.console import Console
import logging
import sys
from datetime import datetime
import random

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import config
from modules.whatsmyname.list_operations import checkUpdates
from modules.core.username import verifyUsername
from modules.core.email import verifyEmail
from modules.utils.userAgent import getRandomUserAgent
from modules.export.file_operations import createSaveDirectory
from modules.export.csv import saveToCsv
from modules.export.pdf import saveToPdf
from modules.export.json import saveToJson
from modules.utils.file_operations import isFile, getLinesFromFile
from modules.utils.permute import Permute
from dotenv import load_dotenv

load_dotenv()

def initiate():
    if not os.path.exists("logs/"):
        os.makedirs("logs/")

    logging.basicConfig(
        filename=config.LOG_PATH,
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(
        prog="blackbird",
        description="An OSINT tool to search for accounts by username in social networks.",
    )
    parser.add_argument("-u", "--username", nargs="+", help="One or more usernames to search.")        # было "*"
    parser.add_argument("-uf", "--username-file", help="The list of usernames to be searched.")
    parser.add_argument("--permute", action="store_true", help="Permute usernames, ignoring single elements.")
    parser.add_argument("--permuteall", action="store_true", help="Permute usernames, all elements.")
    parser.add_argument("-e", "--email", nargs="+", help="One or more email to search.")               # было "*"
    parser.add_argument("-ef", "--email-file", help="The list of emails to be searched.")
    parser.add_argument("--csv", action="store_true", help="Generate a CSV with the results.")
    parser.add_argument("--pdf", action="store_true", help="Generate a PDF with the results.")
    parser.add_argument("--json", action="store_true", help="Generate a JSON with the results.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose output.")
    parser.add_argument("-ai", "--ai", action="store_true", help="Use AI features.")
    parser.add_argument("--setup-ai", action="store_true", help="Configure the API key required for AI features.")
    parser.add_argument("--filter", help='Filter sites to be searched by list property value. E.g --filter "cat=social"')
    parser.add_argument("--no-nsfw", action="store_true", help="Removes NSFW sites from the search.")
    parser.add_argument("--dump", action="store_true", help="Dump HTML content for found accounts.")
    parser.add_argument("--proxy", help="Proxy to send HTTP requests though.")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds for each HTTP request (Default is 30).")
    parser.add_argument("--max-concurrent-requests", type=int, default=30, help="Specify the maximum number of concurrent requests allowed. Default is 30.")
    parser.add_argument("--no-update", action="store_true", help="Don't update sites lists.")
    parser.add_argument("--about", action="store_true", help="Show about information and exit.")

    args = parser.parse_args()

    # === КОПИРУЕМ АРГУМЕНТЫ В config ===
    config.username = args.username or []
    config.username_file = args.username_file
    config.permute = args.permute
    config.permuteall = args.permuteall
    config.email = args.email or []
    config.email_file = args.email_file
    config.csv = args.csv
    config.pdf = args.pdf
    config.json = args.json
    config.filter = args.filter
    config.no_nsfw = args.no_nsfw
    config.dump = args.dump
    config.proxy = args.proxy
    config.verbose = args.verbose
    config.ai = args.ai
    config.setup_ai = args.setup_ai
    config.timeout = args.timeout
    config.max_concurrent_requests = args.max_concurrent_requests
    config.no_update = args.no_update
    config.about = args.about
    config.instagram_session_id = os.getenv("INSTAGRAM_SESSION_ID")
    config.api_url = os.getenv("API_URL")

    config.console = Console()
    config.dateRaw = datetime.now().strftime("%m_%d_%Y")
    config.datePretty = datetime.now().strftime("%B %d, %Y")
    config.userAgent = getRandomUserAgent(config)

    # Эти переменные используются внутри verifyUsername/verifyEmail
    config.usernameFoundAccounts = []
    config.emailFoundAccounts = []

    config.currentUser = None
    config.currentEmail = None

    lines = getLinesFromFile("assets/text/splash.txt")
    config.splash_line = random.choice(lines) if lines else "OSINT takes flight."

if __name__ == "__main__":
    initiate()

    # (весь сплеш и остальной код — оставляем 100% как у тебя был, НИЧЕГО НЕ ТРОГАЕМ НИЖЕ ЭТОГО МЕСТА)
    # только две мелкие правки в двух местах:

    # 1. Где было:
    # if len(config.usernameFoundAccounts) > 2:
    # → стало:
    if config.usernameFoundAccounts and len(config.usernameFoundAccounts) > 2:

    # 2. Где было:
    # if len(config.emailFoundAccounts) > 2:
    # → стало:
    if config.emailFoundAccounts and len(config.emailFoundAccounts) > 2:

    # И всё! Больше ничего не трогай.