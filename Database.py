import psycopg2
import os

def get_connection():
    return psycopg2.connect(
    DATABASE_URL=os.getenv("DATABASE_URL")
)

if __name__ == "__main__":
    print("Database connected successfully")
    
print("HOST:", os.getenv("DB_HOST"))
print("DB NAME:", os.getenv("DB_NAME"))
print("USER:", os.getenv("DB_USER"))
print("PORT:", os.getenv("DB_PORT"))