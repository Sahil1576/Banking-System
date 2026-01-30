import psycopg2
import os

def get_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set")
    return psycopg2.connect(
        DATABASE_URL
)

if __name__ == "__main__":
    print("Database connected successfully")
    
print("HOST:", os.getenv("DB_HOST"))
print("DB NAME:", os.getenv("DB_NAME"))
print("USER:", os.getenv("DB_USER"))
print("PORT:", os.getenv("DB_PORT"))