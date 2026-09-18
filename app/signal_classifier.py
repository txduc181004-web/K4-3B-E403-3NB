"""
Classify VLearn chatlog signals into learning/non-learning scopes.

Scopes:
- LEARNING_GAP
- PRODUCT_ISSUE
- CONTENT_ISSUE
- OFF_TOPIC
- INSUFFICIENT_EVIDENCE

Principle:
A question is considered a LEARNING_GAP only when there is
reasonable evidence that the student is asking about a
course concept, technical topic, or learning procedure.

We intentionally keep vague questions as INSUFFICIENT_EVIDENCE.
"""


# =========================================================
# PRODUCT / SYSTEM ISSUES
# =========================================================

PRODUCT_PATTERNS = [
    "reading progress",
    "đã đọc nhưng",
    "đọc bài mà",
    "homepage",
    "không thấy slide",
    "không thấy bài giảng",
    "không thể tóm tắt tài liệu",
    "tại sao bạn không thể tóm tắt",
    "lỗi đóng gói",
    "nộp bài",
    "loading",
    "api error",
    "lỗi hiển thị",
    "hiển thị sai",
    "không load",
    "không tải được",
    "404 not found",
    "404",
    "chưa được cấp quyền",
    "không có quyền vào github",
    "cấp quyền vào github",
]


# =========================================================
# OFF-TOPIC
# =========================================================

OFF_TOPIC_PATTERNS = [
    "con chó là con gì",
    "chó vs mèo",
    "chó và mèo khác nhau",
]


# =========================================================
# CONTENT / MATERIAL ISSUES
# =========================================================

CONTENT_PATTERNS = [
    "slide này bị sai",
    "slide bị sai",
    "dẫn chứng ở đâu để cho là đúng",
]


# =========================================================
# CLEAR LEARNING TOPICS
# =========================================================

LEARNING_PATTERNS = [
    # -----------------------------------------------------
    # AI Fundamentals
    # -----------------------------------------------------
    "artificial intelligence",
    "ai fundamentals",
    "machine intelligence",
    "expert system",
    "expert systems",
    "ai winter",
    "mùa đông ai",
    "ai history",
    "ai, ml và dl",
    "ai ml dl",
    "discriminative ai",

    # -----------------------------------------------------
    # Prompt Engineering
    # -----------------------------------------------------
    "prompt engineering",
    "system prompt",
    "zero-shot",
    "zero shot",
    "one-shot",
    "one shot",
    "few-shot",
    "few shot",
    "chain of thought",
    "cot",
    "temperature",
    "top-k",
    "top k",
    "top-p",
    "top p",
    "tokenization",
    "context window",
    "lost in the middle",
    "overkill",

    # -----------------------------------------------------
    # LLM / Generative AI
    # -----------------------------------------------------
    "llm",
    "large language model",
    "generative ai",
    "gpt",
    "chatgpt",
    "claude",
    "transformer",
    "decoder",
    "encoder",
    "model cốt lõi",
    "model cốt lỗi",
    "model core",
    "foundation model",
    "model weights",
    "token có xác suất cao nhất",
    "tính ngẫu nhiên của văn bản",
    "attention",
    "lstm",
    "rnn",
    "gru",
    "rlhf",

    # -----------------------------------------------------
    # ReAct / Agents / Tool Calling
    # -----------------------------------------------------
    "react",
    "re act",
    "tool calling",
    "function calling",
    "action input",
    "action:",
    "gọi tool",
    "agent gọi tool",
    "gọi tool liên tục",
    "tool liên tục",
    "mcp",
    "multi-agent",
    "langgraph",
    "agent architecture",
    "agent design",
    "agent loop",
    "orchestration",
    "parallelization",
    "workflow",
    "agent",
    "thinking verifier",
    "prm",

    # -----------------------------------------------------
    # RAG / Search
    # -----------------------------------------------------
    "rag",
    "retrieval augmented generation",
    "embedding",
    "vector database",
    "vector db",
    "vector store",
    "reranker",
    "retrieval",
    "chunking",
    "ai search",

    # -----------------------------------------------------
    # Fine-tuning
    # -----------------------------------------------------
    "fine-tuning",
    "fine tuning",
    "qlora",
    "lora",
    "peft",
    "sft",
    "alignment",

    # -----------------------------------------------------
    # Data Pipeline
    # -----------------------------------------------------
    "data pipeline",
    "data pipeline engineering",
    "etl",
    "elt",
    "data ingestion",
    "data processing",
    "streaming",
    "retry",
    "backoff",
    "exponential backoff",
    "dbt",

    # -----------------------------------------------------
    # Data Lakehouse
    # -----------------------------------------------------
    "data lakehouse",
    "lakehouse",
    "metadata",
    "metadata là gì",
    "metadata quan trọng",

    # -----------------------------------------------------
    # ML / CV
    # -----------------------------------------------------
    "machine learning",
    "computer vision",
    "classification",
    "regression",
    "object detection",
    "multi-object tracking",
    "multi-frame tracking",
    "multiframe tracking",
    "mota",
    "track prediction",
    "dự đoán track",
    "gradient",
    "đạo hàm",
    "feature",
    "label",
    "gán nhãn",
    "dataset",
    "training data",
    "train data",

    # -----------------------------------------------------
    # MLOps / Evaluation
    # -----------------------------------------------------
    "mlops",
    "evaluation",
    "eval",
    "benchmark",
    "metric",
    "precision",
    "recall",
    "f1",
    "error matrix",

    # -----------------------------------------------------
    # Observability
    # -----------------------------------------------------
    "observability",
    "tracing",
    "trace",
    "harness",
    "monitoring",
    "logging",

    # -----------------------------------------------------
    # Cloud / Infrastructure
    # -----------------------------------------------------
    "docker",
    "kubernetes",
    "cloud",
    "deployment",
    "deploy",
    "infrastructure",
    "ci/cd",
    "ram",
    "vram",

    # -----------------------------------------------------
    # Security
    # -----------------------------------------------------
    "security",
    "prompt injection",
    "guardrail",
    "authentication",
    "authorization",
    "privacy",
    "vượt rào",
    "quá quyền",

    # -----------------------------------------------------
    # Memory
    # -----------------------------------------------------
    "long-term memory",
    "short-term memory",
    "memory system",
    "memory",

    # -----------------------------------------------------
    # AI Product / Product Management
    # -----------------------------------------------------
    "ai product",
    "ai product management",
    "business problem",
    "problem scoping",
    "problem scope",
    "baseline",
    "persona",
    "jtbd",
    "jobs to be done",
    "business value",
    "kpi",
    "augmentation",
    "automation",
    "prd",
    "ai capability",
]


# =========================================================
# LEARNING LANGUAGE
# =========================================================

LEARNING_LANGUAGE_PATTERNS = [
    "không hiểu",
    "chưa hiểu",
    "vẫn không hiểu",
    "không hiểu gì",
    "giải thích",
    "giải thích lại",
    "giải thích rõ",
    "giải thích thêm",
    "cho ví dụ",
    "ví dụ",
    "phân biệt",
    "khác nhau",
    "tại sao",
    "vì sao",
    "như thế nào",
    "hoạt động như thế nào",
    "ý nghĩa là gì",
    "là gì",
    "có nghĩa là gì",
    "nghĩa là",
    "thế nào",
    "hợp lí không",
    "có đúng không",
    "vì sao cần",
    "tại sao cần",
    "tại sao không",
]


# =========================================================
# GENERIC / TOO VAGUE
# =========================================================

GENERIC_ONLY_PATTERNS = [
    "tôi không hiểu",
    "mình không hiểu",
    "em không hiểu",
    "chưa hiểu",
    "vẫn không hiểu",
    "tôi vẫn không hiểu",
    "tôi không hiểu gì",
    "giải thích lại giúp mình phần mà mình hay thấy khó",
    "tôi không hiểu phần này",
    "giải thích phần này",
    "giải thích slide này",
    "giải thích trang này",
    "giải thích slide",
    "giải thích trang",
    "tại sao?",
    "tại sao",
    "vì sao",
    "khác nhau như nào",
    "nghĩa là gì",
]


# =========================================================
# GENERIC TOPIC LABELS
# =========================================================

GENERIC_TOPICS = {
    "",
    "day01",
    "day02",
    "day03",
    "day04",
    "day05",
    "day06",
    "day07",
    "day08",
    "day09",
    "day10",
    "day11",
    "day12",
    "day13",
    "day14",
    "day15",
    "day16",
    "day17",
    "day18",
    "day19",
    "day20",
    "day21",
    "day22",
    "day23",
    "understanding",
    "slide",
    "data",
    "agenda",
    "reading progress",
    "ai lỗi",
    "lỗi",
    "d01",
    "d02",
    "d03",
    "d04",
    "d05",
    "d06",
    "d07",
}


def _contains_pattern(
    text: str,
    patterns: list[str],
) -> bool:
    """
    Case-insensitive substring matching.
    """

    text = text.lower()

    return any(
        pattern.lower() in text
        for pattern in patterns
    )


def _has_clear_topic(
    raw_topic: str,
    lecture_title: str,
) -> bool:
    """
    Determine whether topic metadata gives enough
    information to identify a learning subject.
    """

    raw = raw_topic.lower().strip()
    lecture = lecture_title.lower().strip()

    # A known technical topic is strong evidence.
    if _contains_pattern(
        f"{raw} {lecture}",
        LEARNING_PATTERNS,
    ):
        return True

    # Reject completely generic labels.
    if raw in GENERIC_TOPICS:
        return False

    # If lecture title itself is a meaningful technical
    # course title, it can provide supporting evidence.
    if _contains_pattern(
        lecture,
        LEARNING_PATTERNS,
    ):
        return True

    # A non-generic topic label can be useful when combined
    # with a learning-style question.
    if len(raw) >= 5:
        return True

    return False


def classify_signal(item: dict) -> str:
    """
    Classify one AI-analysis result.

    Returns:
        LEARNING_GAP
        PRODUCT_ISSUE
        CONTENT_ISSUE
        OFF_TOPIC
        INSUFFICIENT_EVIDENCE
    """

    question = str(
        item.get("student_question", "")
    ).strip()

    raw_topic = str(
        item.get("topic", "")
    ).strip()

    lecture_title = str(
        item.get("lecture_title", "")
    ).strip()

    # ---------------------------------------------------------
    # 1. Product / system issue
    # ---------------------------------------------------------

    if _contains_pattern(
        question,
        PRODUCT_PATTERNS,
    ):
        return "PRODUCT_ISSUE"

    # ---------------------------------------------------------
    # 2. Off-topic
    # ---------------------------------------------------------

    if _contains_pattern(
        question,
        OFF_TOPIC_PATTERNS,
    ):
        return "OFF_TOPIC"

    # ---------------------------------------------------------
    # 3. Content/material issue
    # ---------------------------------------------------------

    if _contains_pattern(
        question,
        CONTENT_PATTERNS,
    ):
        return "CONTENT_ISSUE"

    # ---------------------------------------------------------
    # 4. Explicit technical topic in question
    # ---------------------------------------------------------

    if _contains_pattern(
        question,
        LEARNING_PATTERNS,
    ):
        return "LEARNING_GAP"

    # ---------------------------------------------------------
    # 5. Learning language + clear topic metadata
    #
    # Example:
    #
    # raw_topic = "RNN"
    # question = "điểm hạn chế của nó là gì?"
    #
    # raw_topic provides the missing topic evidence.
    # ---------------------------------------------------------

    has_learning_language = _contains_pattern(
        question,
        LEARNING_LANGUAGE_PATTERNS,
    )

    has_clear_topic = _has_clear_topic(
        raw_topic,
        lecture_title,
    )

    if (
        has_learning_language
        and has_clear_topic
    ):
        return "LEARNING_GAP"

    # ---------------------------------------------------------
    # 6. Generic "I don't understand"
    # ---------------------------------------------------------

    if _contains_pattern(
        question,
        GENERIC_ONLY_PATTERNS,
    ):
        return "INSUFFICIENT_EVIDENCE"

    # ---------------------------------------------------------
    # 7. Conservative default
    # ---------------------------------------------------------

    return "INSUFFICIENT_EVIDENCE"
