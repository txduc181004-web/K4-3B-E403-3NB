import json
from pathlib import Path

INPUT = Path("data/sample/ai_analysis.json")

REQUIRED = [
    "turn_id",
    "is_signal",
    "signal_type",
    "topic",
    "severity",
    "reason",
    "student",
    "lecture_code",
    "lecture_title",
    "student_question",
]


def main():
    with open(INPUT, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = data["results"]

    fixed = []
    wrapped_fixed = 0

    for item in results:
        # Trường hợp retry_single.py lưu:
        # {
        #   "results": [{ actual_result }],
        #   "student": ...,
        #   ...
        # }
        if "results" in item and isinstance(item["results"], list):
            nested = item["results"]

            if len(nested) == 1 and isinstance(nested[0], dict):
                actual = nested[0].copy()

                # Metadata lấy từ outer object
                for key in [
                    "student",
                    "lecture_code",
                    "lecture_title",
                    "student_question",
                ]:
                    if key in item:
                        actual[key] = item[key]

                fixed.append(actual)
                wrapped_fixed += 1
                continue

        fixed.append(item)

    data["results"] = fixed

    with open(INPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Fixed wrapped records: {wrapped_fixed}")
    print(f"Total results: {len(fixed)}")


if __name__ == "__main__":
    main()
