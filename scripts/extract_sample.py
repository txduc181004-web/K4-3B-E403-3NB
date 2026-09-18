from pathlib import Path
import pandas as pd
import re


INPUT = Path("data/vlearn-pack/chatlog/tutor_turns.csv")
OUTPUT = Path("data/sample/candidate_questions.csv")


def contains_signal(text: str) -> bool:
    """
    Heuristic filter:
    giữ lại những câu hỏi có dấu hiệu người học đang
    chưa hiểu, nhầm khái niệm hoặc cần giải thích lại.
    """

    if not isinstance(text, str):
        return False

    text = text.lower()

    signal_patterns = [
        # Không hiểu / chưa hiểu
        r"\bkhông hiểu\b",
        r"\bchưa hiểu\b",
        r"\bkhó hiểu\b",
        r"\bchưa rõ\b",
        r"\bkhông rõ\b",

        # Hỏi lại
        r"\bgiải thích lại\b",
        r"\bgiải thích rõ\b",
        r"\bnói rõ hơn\b",
        r"\bcó thể giải thích\b",

        # Nhầm lẫn
        r"\bkhác nhau\b",
        r"\bkhác gì\b",
        r"\bphân biệt\b",
        r"\bcó phải.*không\b",
        r"\bvậy.*hay.*\b",

        # Xác nhận khái niệm
        r"\bý là\b",
        r"\bnghĩa là\b",
        r"\btại sao\b",
        r"\bvì sao\b",
        r"\bnhư thế nào\b",

        # Implementation problem
        r"\blỗi\b",
        r"\berror\b",
        r"\bkhông chạy\b",
        r"\bkhông hoạt động\b",
        r"\bsai\b",
    ]

    return any(re.search(pattern, text) for pattern in signal_patterns)


def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Không tìm thấy dataset: {INPUT}"
        )

    print("Loading dataset...")

    df = pd.read_csv(INPUT)

    print(f"Records loaded: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    # --------------------------------------------------
    # 1. Loại câu hỏi preset
    # --------------------------------------------------

    df = df[df["is_preset"] == False].copy()

    print(f"After removing preset: {len(df):,}")

    # --------------------------------------------------
    # 2. Loại câu hỏi rỗng
    # --------------------------------------------------

    df["student_question"] = (
        df["student_question"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df = df[df["student_question"].str.len() > 0].copy()

    # --------------------------------------------------
    # 3. Heuristic signal detection
    # --------------------------------------------------

    df["heuristic_signal"] = df["student_question"].apply(
        contains_signal
    )

    candidates = df[df["heuristic_signal"]].copy()

    print(f"Heuristic candidates: {len(candidates):,}")

    # --------------------------------------------------
    # 4. Giới hạn kích thước sample
    # --------------------------------------------------

    # Giữ tối đa 500 câu để đưa sang bước AI.
    #
    # stratify tương đối theo lecture để tránh
    # một bài chiếm toàn bộ sample.

    if len(candidates) > 500:
        # Lấy mẫu tối đa 500 câu.
        # Không dùng groupby().apply() để tránh làm mất lecture_code
        # khỏi columns trong một số phiên bản Pandas.

        candidates = candidates.sample(
            n=500,
            random_state=42
        ).copy()

    # --------------------------------------------------
    # 5. Chỉ giữ các field cần cho AI
    # --------------------------------------------------

    output_columns = [
        "turn_id",
        "asked_at_vn",
        "student",
        "lecture_code",
        "lecture_title",
        "student_question",
        "tutor_reply",
        "move_used",
        "rating",
        "heuristic_signal",
    ]

    candidates = candidates[output_columns]

    # --------------------------------------------------
    # 6. Save
    # --------------------------------------------------

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    candidates.to_csv(
        OUTPUT,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print("=" * 50)
    print("DONE")
    print("=" * 50)
    print(f"Output: {OUTPUT}")
    print(f"Rows: {len(candidates):,}")

    print()
    print("Preview:")
    print(
        candidates[
            [
                "turn_id",
                "student",
                "lecture_code",
                "student_question"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()