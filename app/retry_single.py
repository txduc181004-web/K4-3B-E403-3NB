import json
import os
import time

import ollama
import pandas as pd
from dotenv import load_dotenv

from app.prompts import SYSTEM_PROMPT


load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

INPUT_FILE = "data/sample/candidate_questions.csv"
ANALYSIS_FILE = "data/sample/ai_analysis.json"

client = ollama.Client(host=HOST)


def build_prompt(row):
    question = str(row["student_question"])[:800]

    return f"""
Phân tích đúng MỘT câu hỏi học viên.

DATA:
turn_id: {row["turn_id"]}
lecture_code: {row["lecture_code"]}
lecture_title: {row["lecture_title"]}
student_question: {question}

Trả về JSON duy nhất:

{{
  "turn_id": "{row["turn_id"]}",
  "is_signal": true,
  "signal_type": "CONCEPT_CONFUSION",
  "topic": "topic name",
  "severity": 3,
  "reason": "short reason"
}}
"""


def analyze(row):

    response = client.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": build_prompt(row),
            },
        ],
        format="json",
        options={
            "temperature": 0,
            "num_ctx": 4096,
            "num_predict": 300,
        },
    )

    return json.loads(
        response["message"]["content"]
    )


def main():

    df = pd.read_csv(INPUT_FILE)

    with open(
        ANALYSIS_FILE,
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    existing = data["results"]

    processed_ids = {
        str(x["turn_id"])
        for x in existing
    }

    missing = df[
        ~df["turn_id"].astype(str).isin(
            processed_ids
        )
    ]

    print(
        f"Missing: {len(missing)}"
    )

    for _, row in missing.iterrows():

        turn_id = str(row["turn_id"])

        print(
            f"\nProcessing {turn_id}..."
        )

        success = False

        for attempt in range(3):

            try:

                result = analyze(row)

                result["student"] = str(
                    row["student"]
                )

                result["lecture_code"] = str(
                    row["lecture_code"]
                )

                result["lecture_title"] = str(
                    row["lecture_title"]
                )

                result["student_question"] = str(
                    row["student_question"]
                )

                existing.append(result)

                print("  SUCCESS")

                success = True
                break

            except Exception as e:

                print(
                    f"  Attempt {attempt + 1}: {e}"
                )

                time.sleep(1)

        if not success:
            print("  FAILED")

    data["total_results"] = len(existing)

    with open(
        ANALYSIS_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(
        f"\nDONE: {len(existing)} results"
    )


if __name__ == "__main__":
    main()