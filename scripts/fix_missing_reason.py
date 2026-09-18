import json
from pathlib import Path

INPUT = Path("data/sample/ai_analysis.json")

REASONS = {
    "CONCEPT_CONFUSION": (
        "The question explicitly asks to distinguish, clarify, "
        "or understand a concept."
    ),
    "REQUEST_REEXPLANATION": (
        "The student explicitly requests the concept or material "
        "to be explained again."
    ),
    "WHY_QUESTION": (
        "The student asks for an explanation of why a concept, "
        "method, or behavior works this way."
    ),
    "IMPLEMENTATION_DIFFICULTY": (
        "The question indicates difficulty applying the concept "
        "or completing a practical task."
    ),
    "REPEATED_UNDERSTANDING": (
        "The question contains a repeated or persistent request "
        "for clarification."
    ),
    "NONE": (
        "No specific learning difficulty signal was identified."
    ),
}


def main():
    with open(INPUT, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0

    for item in data["results"]:
        if not item.get("reason"):
            signal_type = item.get("signal_type", "NONE")

            item["reason"] = REASONS.get(
                signal_type,
                "The question contains a learning-related signal "
                "that may require further clarification."
            )

            count += 1

    with open(INPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Fixed missing reasons: {count}")
    print(f"Total results: {len(data['results'])}")


if __name__ == "__main__":
    main()
