"""
Quick test script to verify OpenAI integration works
"""

import os
import sys
import django
from pathlib import Path

# Add the Django project to the path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MyProject.settings")
django.setup()

# Test the OpenAI service
try:
    from services.openai_service import get_openai_quiz_service

    service = get_openai_quiz_service()
    print("✅ OpenAI service created successfully")
    print(f"Client status: {'Available' if service.client else 'Not initialized (fallback mode)'}")

    # Test fallback questions
    fallback_questions = service._get_fallback_questions("python")
    print(f"✅ Fallback questions available: {len(fallback_questions)}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
