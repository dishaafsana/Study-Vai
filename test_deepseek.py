"""
Quick test script to verify Deepseek integration works
"""

import os
import sys
import json
import django
from pathlib import Path

# Add the Django project to the path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MyProject.settings")
django.setup()

# Test the AI service
try:
    from services.openai_service import get_openai_quiz_service

    service = get_openai_quiz_service()
    print("✅ AI service created successfully")
    print(f"Using Deepseek: {service.use_deepseek}")
    print(f"OpenAI model: {service.model}")
    print(f"Using modern client: {service.use_modern_client}")

    # Test question generation
    print("\n🚀 Testing question generation with Deepseek...")
    try:
        questions = service.generate_quiz_questions("python", count=1)
        print(f"✅ Generated {len(questions)} questions")
        print(json.dumps(questions, indent=2))
    except Exception as e:
        print(f"❌ Question generation error: {e}")

    # Test explanation
    print("\n🚀 Testing explanation generation with Deepseek...")
    try:
        explanation = service.generate_explanation(
            question="What is Python's primary use?",
            user_answer="Web development",
            correct_answer="General purpose programming",
            is_correct=False,
        )
        print(f"✅ Generated explanation:\n{explanation}")
    except Exception as e:
        print(f"❌ Explanation generation error: {e}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
