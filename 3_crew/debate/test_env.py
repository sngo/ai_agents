from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env from current or parent directory
print(os.getenv('OPENAI_API_KEY'), os.getenv('ANTHROPIC_API_KEY'))