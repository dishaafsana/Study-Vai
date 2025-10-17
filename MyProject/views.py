from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from services.openai_service import openai_quiz_service

logger = logging.getLogger(__name__)


# Home Page View
def home(request):
    return render(request, "home.html")


# Log In Page View
def login(request):
    return render(request, "auth/login.html")


# Sign Up Page View
def signup(request):
    return render(request, "auth/signup.html")


# Quiz Page View
def quiz(request):
    return render(request, "quiz.html")


# AI-Powered Quiz API Endpoints


@csrf_exempt
@require_http_methods(["POST"])
def generate_quiz_questions(request):
    """
    API endpoint to generate AI-powered quiz questions

    Expected JSON payload:
    {
        "category": "python|web-development|sql|php",
        "difficulty": "beginner|intermediate|advanced",
        "count": 5
    }
    """
    try:
        data = json.loads(request.body)
        category = data.get("category", "python")
        difficulty = data.get("difficulty", "intermediate")
        count = data.get("count", 5)

        # Validate inputs
        valid_categories = ["python", "web-development", "sql", "php"]
        valid_difficulties = ["beginner", "intermediate", "advanced"]

        if category not in valid_categories:
            return JsonResponse({"error": "Invalid category"}, status=400)

        if difficulty not in valid_difficulties:
            return JsonResponse({"error": "Invalid difficulty"}, status=400)

        if not (1 <= count <= 10):
            return JsonResponse({"error": "Count must be between 1 and 10"}, status=400)

        # Generate questions using OpenAI
        questions = openai_quiz_service.generate_quiz_questions(category, difficulty, count)

        logger.info(f"Generated {len(questions)} questions for {category} ({difficulty})")

        return JsonResponse(
            {
                "success": True,
                "questions": questions,
                "category": category,
                "difficulty": difficulty,
                "count": len(questions),
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)
    except Exception as e:
        logger.error(f"Error in generate_quiz_questions: {str(e)}")
        return JsonResponse({"error": "Internal server error"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_explanation(request):
    """
    API endpoint to generate AI-powered explanations for quiz answers

    Expected JSON payload:
    {
        "question": "The quiz question",
        "user_answer": "User's selected answer",
        "correct_answer": "The correct answer",
        "is_correct": true/false
    }
    """
    try:
        data = json.loads(request.body)
        question = data.get("question", "")
        user_answer = data.get("user_answer", "")
        correct_answer = data.get("correct_answer", "")
        is_correct = data.get("is_correct", False)

        if not all([question, user_answer, correct_answer]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Generate explanation using OpenAI
        explanation = openai_quiz_service.generate_explanation(
            question, user_answer, correct_answer, is_correct
        )

        return JsonResponse({"success": True, "explanation": explanation, "is_correct": is_correct})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)
    except Exception as e:
        logger.error(f"Error in generate_explanation: {str(e)}")
        return JsonResponse({"error": "Internal server error"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_performance_assessment(request):
    """
    API endpoint to generate AI-powered performance assessments

    Expected JSON payload:
    {
        "score": 4,
        "total": 5,
        "category": "python",
        "time_taken": 120  // optional, in seconds
    }
    """
    try:
        data = json.loads(request.body)
        score = data.get("score", 0)
        total = data.get("total", 5)
        category = data.get("category", "python")
        time_taken = data.get("time_taken", None)

        if not isinstance(score, int) or not isinstance(total, int):
            return JsonResponse({"error": "Score and total must be integers"}, status=400)

        if score < 0 or total <= 0 or score > total:
            return JsonResponse({"error": "Invalid score/total values"}, status=400)

        # Generate assessment using OpenAI
        assessment = openai_quiz_service.generate_performance_assessment(
            score, total, category, time_taken
        )

        return JsonResponse(
            {
                "success": True,
                "assessment": assessment,
                "score": score,
                "total": total,
                "percentage": round((score / total) * 100),
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)
    except Exception as e:
        logger.error(f"Error in generate_performance_assessment: {str(e)}")
        return JsonResponse({"error": "Internal server error"}, status=500)
