from code_analysis import analyze_code
from question_generator import generate_questions
from test_generator import generate_tests
import json

def process_code(code):

    analysis = analyze_code(code)

    return analysis
