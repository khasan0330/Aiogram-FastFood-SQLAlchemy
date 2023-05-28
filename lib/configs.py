import os
from dotenv import *

load_dotenv()


user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
ipaddress = os.getenv('DB_ADDRESS')
port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
TOKEN = os.getenv('BOT_TOKEN')
PAYME = os.getenv('PAYMENT')
