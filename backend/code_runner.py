import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY not set")

client = OpenAI(api_key=api_key)


def run_code(code: str, input_data: str) -> dict:
    system_prompt = (
        "You are a C interpreter. Compile and run the given C program. "
        "If there is a compilation error, start your reply with 'Compilation error:'. "
        "Respond only with the program output."
    )

    user_prompt = (
        f"Here is a C program:\n{code}\n\n"
        f"Here is the input:\n{input_data}\n\n"
        "Run the program and return only the output."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
        )

        answer = response.choices[0].message.content.strip()

        if answer.lower().startswith("compilation error"):
            return {"output": "", "error": answer}

        return {"output": answer, "error": ""}

    except Exception as exc:
        return {"output": "", "error": f"OpenAI API call failed: {exc}"}
