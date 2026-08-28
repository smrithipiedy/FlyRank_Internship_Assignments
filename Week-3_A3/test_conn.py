import psycopg
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")
print(f"Trying to connect to {url}...")
try:
    with psycopg.connect(url) as conn:
        print("Connected successfully!")
except Exception as e:
    print(f"Failed: {e}")
