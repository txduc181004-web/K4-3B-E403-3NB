import json
from collections import Counter, defaultdict
from pathlib import Path

from app.topic_normalizer import normalize_topic
from app.signal_classifier import classify_signal


INPUT = Path("data/sample/ai_analysis.json")
OUTPUT = Path("data/sample/gap_map.json")


def aggregate():
    print(f"Loading: {INPUT}")

    with INPUT.open("r", encoding="utf-8") as f:
        data = json.load(f)

    results = data.get("results", [])

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    skipped_non_signals = 0
    skipped_none_signals = 0
    skipped_non_learning = Counter()

    # canonical_topic -> list of valid LEARNING_GAP records
    grouped = defaultdict(list)

    # ---------------------------------------------------------
    # Collect valid learning-gap signals
    # ---------------------------------------------------------

    for item in results:

        # -----------------------------------------------------
        # 1. AI does not consider this a signal
        # -----------------------------------------------------
        if not item.get("is_signal", False):
            skipped_non_signals += 1
            continue

        # -----------------------------------------------------
        # 2. Inconsistent case:
        # is_signal=True but signal_type=NONE
        # -----------------------------------------------------
        signal_type = str(
            item.get("signal_type", "")
        ).strip()

        if signal_type == "NONE":
            skipped_none_signals += 1
            continue

        # -----------------------------------------------------
        # 3. Classify signal scope
        # -----------------------------------------------------
        signal_scope = classify_signal(item)

        # Keep the classification in memory for debugging.
        #
        # Possible values:
        # LEARNING_GAP
        # PRODUCT_ISSUE
        # CONTENT_ISSUE
        # OFF_TOPIC
        # INSUFFICIENT_EVIDENCE

        if signal_scope != "LEARNING_GAP":
            skipped_non_learning[signal_scope] += 1
            continue

        # -----------------------------------------------------
        # 4. Extract metadata
        # -----------------------------------------------------

        lecture_code = str(
            item.get("lecture_code", "")
        ).strip()

        lecture_title = str(
            item.get("lecture_title", "")
        ).strip()

        raw_topic = str(
            item.get("topic", "")
        ).strip()

        question = str(
            item.get("student_question", "")
        ).strip()

        # -----------------------------------------------------
        # 5. Normalize topic
        # -----------------------------------------------------

        canonical_topic = normalize_topic(
            raw_topic,
            lecture_title,
            question,
        )

        # -----------------------------------------------------
        # 6. Store learning-gap signal
        # -----------------------------------------------------

        grouped[canonical_topic].append(
            {
                "turn_id": item.get("turn_id"),
                "student": item.get("student"),
                "lecture_code": lecture_code,
                "lecture_title": lecture_title,
                "question": question,
                "signal_type": signal_type,
                "signal_scope": signal_scope,
                "severity": item.get("severity", 0),
                "reason": item.get("reason", ""),
                "raw_topic": raw_topic,
            }
        )

    # ---------------------------------------------------------
    # Build canonical topic records
    # ---------------------------------------------------------

    topics = []

    for canonical_topic, signals in grouped.items():

        # -----------------------------------------------------
        # Unique students
        # -----------------------------------------------------

        students = {
            str(x["student"])
            for x in signals
            if x.get("student")
        }

        # -----------------------------------------------------
        # Signal type distribution
        # -----------------------------------------------------

        signal_types = Counter(
            x["signal_type"]
            for x in signals
            if x.get("signal_type")
        )

        # -----------------------------------------------------
        # Severity
        # -----------------------------------------------------

        severities = [
            float(x["severity"])
            for x in signals
            if isinstance(
                x.get("severity"),
                (int, float),
            )
        ]

        avg_severity = (
            sum(severities) / len(severities)
            if severities
            else 0
        )

        # -----------------------------------------------------
        # Lecture breakdown
        # -----------------------------------------------------

        lecture_groups = defaultdict(list)

        for signal in signals:
            key = (
                signal["lecture_code"],
                signal["lecture_title"],
            )

            lecture_groups[key].append(signal)

        lectures = []

        for (
            lecture_code,
            lecture_title,
        ), lecture_signals in lecture_groups.items():

            lecture_students = {
                str(x["student"])
                for x in lecture_signals
                if x.get("student")
            }

            lecture_severities = [
                float(x["severity"])
                for x in lecture_signals
                if isinstance(
                    x.get("severity"),
                    (int, float),
                )
            ]

            lecture_avg_severity = (
                sum(lecture_severities)
                / len(lecture_severities)
                if lecture_severities
                else 0
            )

            lectures.append(
                {
                    "lecture_code": lecture_code,
                    "lecture_title": lecture_title,
                    "signal_count": len(
                        lecture_signals
                    ),
                    "student_count": len(
                        lecture_students
                    ),
                    "average_severity": round(
                        lecture_avg_severity,
                        2,
                    ),
                }
            )

        # Sort lecture breakdown
        lectures.sort(
            key=lambda x: (
                -x["signal_count"],
                -x["student_count"],
                -x["average_severity"],
            )
        )

        # -----------------------------------------------------
        # Evidence
        # -----------------------------------------------------

        evidence = sorted(
            signals,
            key=lambda x: (
                -float(x["severity"])
                if isinstance(
                    x.get("severity"),
                    (int, float),
                )
                else 0
            ),
        )[:5]

        clean_evidence = []

        for e in evidence:
            clean_evidence.append(
                {
                    "turn_id": e["turn_id"],
                    "student": e["student"],
                    "lecture_code": e["lecture_code"],
                    "lecture_title": e["lecture_title"],
                    "question": e["question"],
                    "signal_type": e["signal_type"],
                    "signal_scope": e["signal_scope"],
                    "severity": e["severity"],
                    "reason": e["reason"],
                }
            )

        # -----------------------------------------------------
        # Topic record
        # -----------------------------------------------------

        topics.append(
            {
                "topic": canonical_topic,
                "signal_count": len(signals),
                "student_count": len(students),
                "average_severity": round(
                    avg_severity,
                    2,
                ),
                "signal_types": dict(signal_types),
                "lectures": lectures,
                "evidence": clean_evidence,
            }
        )

    # ---------------------------------------------------------
    # Sort canonical topics
    # ---------------------------------------------------------

    topics.sort(
        key=lambda x: (
            -x["signal_count"],
            -x["student_count"],
            -x["average_severity"],
        )
    )

    # ---------------------------------------------------------
    # Calculate statistics
    # ---------------------------------------------------------

    valid_signal_results = sum(
        len(x)
        for x in grouped.values()
    )

    total_non_learning = sum(
        skipped_non_learning.values()
    )

    # ---------------------------------------------------------
    # Final output
    # ---------------------------------------------------------

    output = {
        "model": data.get("model"),

        "source_results": len(results),

        "valid_signal_results": valid_signal_results,

        "skipped_non_signals": skipped_non_signals,

        "skipped_none_signals": skipped_none_signals,

        "skipped_non_learning": total_non_learning,

        "non_learning_breakdown": dict(
            skipped_non_learning
        ),

        "total_topics": len(topics),

        "topics": topics,
    }

    # ---------------------------------------------------------
    # Save JSON
    # ---------------------------------------------------------

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2,
        )

    # ---------------------------------------------------------
    # Console output
    # ---------------------------------------------------------

    print()
    print("DONE")
    print(
        f"Canonical learning areas: "
        f"{len(topics)}"
    )

    print(
        f"Output: {OUTPUT}"
    )

    print(
        f"Source results: {len(results)}"
    )

    print(
        f"Valid learning-gap signals: "
        f"{valid_signal_results}"
    )

    print(
        f"Skipped non-signals: "
        f"{skipped_non_signals}"
    )

    print(
        f"Skipped signal_type=NONE: "
        f"{skipped_none_signals}"
    )

    print(
        f"Skipped non-learning signals: "
        f"{total_non_learning}"
    )

    if skipped_non_learning:
        print()
        print("Non-learning breakdown:")

        for scope, count in sorted(
            skipped_non_learning.items(),
            key=lambda x: -x[1],
        ):
            print(
                f"  {scope}: {count}"
            )

    print()
    print("Top learning areas:")

    for i, topic in enumerate(
        topics[:20],
        1,
    ):
        print(
            f"{i}. "
            f"{topic['topic']} | "
            f"signals={topic['signal_count']} | "
            f"students={topic['student_count']} | "
            f"severity={topic['average_severity']}"
        )


if __name__ == "__main__":
    aggregate()
