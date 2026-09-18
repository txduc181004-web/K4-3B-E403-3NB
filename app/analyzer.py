import json
import os
import time

import pandas as pd
import ollama

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv():
        return False

from app.prompts import SYSTEM_PROMPT


load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

INPUT_FILE = "data/sample/candidate_questions.csv"
OUTPUT_FILE = "data/sample/ai_analysis.json"

BATCH_SIZE = 10


client = ollama.Client(host=HOST)


def build_prompt(rows):
    questions = []

    for _, row in rows.iterrows():
        questions.append(
            {
                "turn_id": str(row["turn_id"]),
                "lecture_code": str(row["lecture_code"]),
                "lecture_title": str(row["lecture_title"]),
                "student_question": str(row["student_question"])[:2000],
            }
        )

    return f"""
Hãy phân tích các câu hỏi học viên dưới đây.

Chỉ sử dụng thông tin có trong DATA.

DATA:
{json.dumps(questions, ensure_ascii=False, indent=2)}

Hãy trả về JSON đúng format đã yêu cầu.
"""


def analyze_batch(rows):
    prompt = build_prompt(rows)

    response = client.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        format="json",
        options={
            "temperature": 0,
            "num_predict": 400,
        },
        keep_alive="10m",
    )

    content = response["message"]["content"]

    return json.loads(content)


def main():
    print(f"Loading: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows: {len(df)}")
    print(f"Model: {MODEL}")
    print(f"Batch size: {BATCH_SIZE}")

    all_results = []

    total_batches = (len(df) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_number, start in enumerate(
        range(0, len(df), BATCH_SIZE),
        start=1,
    ):
        end = min(start + BATCH_SIZE, len(df))

        batch = df.iloc[start:end]

        print(
            f"\n[{batch_number}/{total_batches}] "
            f"Analyzing rows {start + 1}-{end}..."
        )

        try:
            result = analyze_batch(batch)

            results = result.get("results", [])
            metadata = {
                str(row["turn_id"]): {
                    "student": str(row["student"]),
                    "lecture_code": str(row["lecture_code"]),
                    "lecture_title": str(row["lecture_title"]),
                    "student_question": str(row["student_question"]),
                }
                for _, row in batch.iterrows()
            }

            for item in results:
                turn_id = str(item.get("turn_id"))

                if turn_id in metadata:
                    item.update(metadata[turn_id])

            all_results.extend(results)

            print(f"  Received: {len(results)} results")

            # Save after every batch
            with open(
                OUTPUT_FILE,
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(
                    {
                        "model": MODEL,
                        "total_results": len(all_results),
                        "results": all_results,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

        except Exception as e:
            print(f"  ERROR: {e}")
            print("  Skipping this batch...")

        time.sleep(0.2)

    print("\nDONE")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Results: {len(all_results)}")


if __name__ == "__main__":
    main()