from database import init_db

def main():
    print("Starting application...")
    try:
        init_db()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Application failed to start: {e}")

if __name__ == "__main__":
    main()
