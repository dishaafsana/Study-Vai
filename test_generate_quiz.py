import os
import sys
from pathlib import Path
import django

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MyProject.settings")
django.setup()

from services.openai_service import get_openai_quiz_service

svc = get_openai_quiz_service()
print("Client available:", bool(svc.client))
try:
    questions = svc.generate_quiz_questions("python", "beginner", 3)
    print("Generated questions count:", len(questions))
    for i, q in enumerate(questions, 1):
        print(f"\nQ{i}: {q.get('question')}")
        for idx, opt in enumerate(q.get("options", [])):
            print(f"  {chr(65 + idx)}. {opt}")
        print("Correct index:", q.get("correct"))
except Exception as e:
    print("Error calling generate_quiz_questions:", e)
