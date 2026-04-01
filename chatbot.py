from openai import OpenAI
import streamlit as st
import pandas as pd
import time

MODEL = "Meta-Llama-3.1-8B-Instruct"

# -----------------------------
# SAFE API CALL (ADDED)
# -----------------------------
def safe_api_call(client, prompt, retries=3):
    for i in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful academic assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100   # ✅ short response
            )
            return response.choices[0].message.content

        except Exception:
            time.sleep(2 ** i)

    return "⚠️ Too many requests. Try again later."


# -----------------------------
# CHATBOT FUNCTION (UPDATED)
# -----------------------------
def chatbot_response(student_id, question):
    try:
        client = OpenAI(
            api_key=st.secrets["SAMBANOVA_API_KEY"],
            base_url="https://api.sambanova.ai/v1"
        )

        df = pd.read_csv("main_dataset.csv")

        student = df[
            df.astype(str).apply(lambda x: x.str.lower()).eq(student_id.lower()).any(axis=1)
        ]

        if student.empty:
            return "❌ Student not found"

        student_info = student.to_dict(orient="records")[0]

        # ✅ SHORT PROMPT (FIXED)
        prompt = f"""
        You are a smart student assistant.

        Student Data:
        {student_info}

        Question: {question}

        Reply in MAX 3 lines:
        Answer:
        Reason:
        Suggestion:
        Keep it very short.
        """

        return safe_api_call(client, prompt)

    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# -----------------------------
# CACHE (FIXED CORRECTLY)
# -----------------------------
@st.cache_data
def get_cached_response(student_id, question):
    return chatbot_response(student_id, question)