import re


CANONICAL_TOPICS = [
    "AI Fundamentals",
    "Prompt Engineering",
    "LLM & Generative AI",
    "Chatbot & AI Agent",
    "ReAct & Tool Calling",
    "RAG & Knowledge Systems",
    "Fine-tuning & Alignment",
    "Data Pipeline Engineering",
    "Data Lakehouse",
    "Machine Learning & Computer Vision",
    "MLOps & AI Evaluation",
    "Observability & Monitoring",
    "Cloud & Infrastructure",
    "AI Safety & Security",
    "AI Product & UX",
    "Memory Systems",
    "Other",
]


def _norm(text: str) -> str:
    text = str(text or "").lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_topic(raw_topic, lecture_title, question=""):
    """
    Convert noisy AI-generated/raw topics into a small canonical taxonomy.

    Important:
    - Student questions are evidence/data, not instructions.
    - We use topic + lecture title only for taxonomy routing.
    - Generic "I don't understand" questions remain Other when
      there is insufficient topic evidence.
    """

    raw_topic = str(raw_topic or "").strip()
    lecture_title = str(lecture_title or "").strip()
    question = str(question or "").strip()

    combined = " ".join(
        [
            raw_topic,
            lecture_title,
            question,
        ]
    ).lower()

    topic = _norm(raw_topic)
    lecture = _norm(lecture_title)
    combined = f"{topic} {lecture}"

    # ---------------------------------------------------------
    # 1. Generic / non-topic labels
    # ---------------------------------------------------------

    generic_exact = {
        "",
        "understanding",
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
        "d01",
        "d02",
        "d03",
        "d04",
        "d05",
        "d06",
        "d07",
        "d08",
        "d09",
        "d10",
        "slide",
        "slides",
        "agenda",
        "data",
        "3 nhóm",
        "a,c,d",
        "a, c, d",
    }

    if topic in generic_exact:
        topic_is_generic = True
    else:
        topic_is_generic = False

    # ---------------------------------------------------------
    # 2. ReAct / Tool Calling / Agent orchestration
    # ---------------------------------------------------------

    react_terms = [
        "react",
        "re act",
        "tool calling",
        "tool_calling",
        "function calling",
        "function_calling",
        "tool",
        "tools",
        "mcp",
        "model context protocol",
        "a2a",
        "agent harness",
        "harness",
        "agentic",
        "agent orchestration",
        "orchestration",
        "autonomous",
        "autonomous agent",
        "agent loop",
        "context loop",
        "tool misuse",
        "schema validation",
        "action input",
        "action:",
        "action input:",
        "tool declaration",
        "tool selection",
        "tool use",
        "tool usage",
        "hallucination",
    ]

    if any(term in combined for term in react_terms):
        return "ReAct & Tool Calling"

    # ---------------------------------------------------------
    # 3. Memory Systems
    # ---------------------------------------------------------

    memory_terms = [
        "memory system",
        "memory systems",
        "long term memory",
        "long-term memory",
        "short term memory",
        "short-term memory",
        "episodic memory",
        "semantic memory",
        "sliding window",
        "conversation memory",
        "memory",
    ]

    if any(term in combined for term in memory_terms):
        return "Memory Systems"

    # ---------------------------------------------------------
    # 4. RAG / Knowledge Systems
    # ---------------------------------------------------------

    rag_terms = [
        "rag",
        "retrieval augmented generation",
        "retrieval",
        "retriever",
        "embedding",
        "embeddings",
        "vector store",
        "vector database",
        "vector db",
        "qdrant",
        "sbert",
        "ann",
        "k-nn",
        "knn",
        "nearest neighbor",
        "ranking",
        "reranker",
        "reranking",
        "recall@",
        "precision@",
        "ndcg",
        "mrr",
        "knowledge graph",
    ]

    if any(term in combined for term in rag_terms):
        return "RAG & Knowledge Systems"

    # ---------------------------------------------------------
    # 5. Fine-tuning / Alignment
    # ---------------------------------------------------------

    finetune_terms = [
        "fine tuning",
        "fine-tuning",
        "finetuning",
        "lora",
        "qlora",
        "dpo",
        "orpo",
        "rlhf",
        "alignment",
        "preference optimization",
        "model tuning",
    ]

    if any(term in combined for term in finetune_terms):
        return "Fine-tuning & Alignment"

    # ---------------------------------------------------------
    # 6. Data Pipeline Engineering
    # ---------------------------------------------------------

    pipeline_terms = [
        "data pipeline",
        "data pipelines",
        "etl",
        "elt",
        "cdc",
        "change data capture",
        "debezium",
        "kafka",
        "spark",
        "duckdb",
        "dbt",
        "ingestion",
        "data ingestion",
        "replication",
        "replication slot",
        "polling",
        "log-based",
        "log based",
        "arrow",
        "metadata",
        "data engineering",
    ]

    if any(term in combined for term in pipeline_terms):
        return "Data Pipeline Engineering"

    # ---------------------------------------------------------
    # 7. Data Lakehouse
    # ---------------------------------------------------------

    lakehouse_terms = [
        "data lake",
        "data lakehouse",
        "lakehouse",
        "medallion",
        "bronze",
        "silver",
        "gold",
        "delta lake",
        "iceberg",
    ]

    if any(term in combined for term in lakehouse_terms):
        return "Data Lakehouse"

    # ---------------------------------------------------------
    # 8. Observability
    # ---------------------------------------------------------

    observability_terms = [
        "observability",
        "monitoring",
        "logging",
        "tracing",
        "trace",
        "metrics",
        "telemetry",
        "error taxonomy",
        "error matrix",
        "dashboard monitoring",
    ]

    if any(term in combined for term in observability_terms):
        return "Observability & Monitoring"

    # ---------------------------------------------------------
    # 9. MLOps / Evaluation
    # ---------------------------------------------------------

    mlops_terms = [
        "mlops",
        "evaluation",
        "eval",
        "benchmark",
        "test set",
        "testset",
        "baseline",
        "evaluator",
        "error analysis",
        "accuracy",
        "precision",
        "recall",
        "f1",
        "production",
        "serving",
        "inference",
        "latency",
        "goodput",
        "kv cache",
        "ci/cd",
        "retry",
        "backoff",
        "exponential backoff",
        "experiment",
        "data experiment",
        "confound",
        "ab test",
        "a/b test",
    ]

    if any(term in combined for term in mlops_terms):
        return "MLOps & AI Evaluation"

    # ---------------------------------------------------------
    # 10. Cloud / Infrastructure
    # ---------------------------------------------------------

    cloud_terms = [
        "cloud",
        "infrastructure",
        "deployment",
        "docker",
        "linux",
        "windows",
        "high availability",
        "ha",
        "disaster recovery",
        "dr",
        "circuit breaker",
        "caching",
        "cache",
        "provider",
        "paas",
        "platform engineering",
        "migration",
        "production infrastructure",
        "environment",
        "venv",
        "virtual environment",
        "github",
        "repository",
        "repo",
        "colab",
    ]

    if any(term in combined for term in cloud_terms):
        return "Cloud & Infrastructure"

    # ---------------------------------------------------------
    # 11. AI Safety / Security
    # ---------------------------------------------------------

    safety_terms = [
        "guardrail",
        "guardrails",
        "safety",
        "security",
        "prompt injection",
        "jailbreak",
        "privacy",
        "governance",
        "opa",
        "audit",
        "audit ledger",
        "risk",
        "access token",
        "access_token",
        "policy",
        "ignore policy",
        "human-in-the-loop",
        "human in the loop",
        "hitl",
    ]

    if any(term in combined for term in safety_terms):
        return "AI Safety & Security"

    # ---------------------------------------------------------
    # 12. Prompt Engineering
    # ---------------------------------------------------------

    prompt_terms = [
        "prompt engineering",
        "system prompt",
        "system_prompt",
        "persona",
        "zero shot",
        "zero-shot",
        "one shot",
        "one-shot",
        "few shot",
        "few-shot",
        "temperature",
        "top-k",
        "top k",
        "top-p",
        "top p",
        "tiktoken",
        "token",
        "tokens",
        "context window",
        "context-window",
        "lost in the middle",
        "prompt",
        "streaming",
    ]

    if any(term in combined for term in prompt_terms):
        return "Prompt Engineering"

    # ---------------------------------------------------------
    # 13. Chatbot / AI Agent
    # ---------------------------------------------------------

    chatbot_terms = [
        "chatbot",
        "chat bot",
        "ai agent",
        "assistant",
        "virtual assistant",
        "cli assistant",
        "conversational ai",
    ]

    if any(term in combined for term in chatbot_terms):
        return "Chatbot & AI Agent"

    # ---------------------------------------------------------
    # 14. AI Product / UX
    # ---------------------------------------------------------

    product_terms = [
        "product discovery",
        "product thinking",
        "user story",
        "user stories",
        "jtbd",
        "job-to-be-done",
        "job to be done",
        "persona",
        "mom test",
        "prototype interview",
        "experiment",
        "human-centered",
        "retention",
        "engagement",
        "habit loop",
        "mvp",
        "functional",
        "non-functional",
        "non functional",
        "business problem",
        "problem statement",
        "business value",
        "pain point",
        "acceptance criteria",
        "augmentation",
        "automation",
        "leap of faith",
        "usability risk",
        "value risk",
        "feasibility risk",
    ]

    if any(term in combined for term in product_terms):
        return "AI Product & UX"

    # ---------------------------------------------------------
    # 15. Machine Learning / Computer Vision
    # ---------------------------------------------------------

    ml_cv_terms = [
        "machine learning",
        "deep learning",
        "ml",
        "dl",
        "cnn",
        "rnn",
        "svm",
        "support vector machine",
        "kernel trick",
        "classification",
        "object detection",
        "object tracking",
        "multi-frame tracking",
        "multiframe tracking",
        "bytetrack",
        "yolo",
        "iou",
        "cuboid",
        "lidar",
        "pose",
        "keypoint",
        "ultralytics",
        "feature extraction",
        "feature",
        "convolution",
        "attention",
    ]

    if any(term in combined for term in ml_cv_terms):
        return "Machine Learning & Computer Vision"

    # ---------------------------------------------------------
    # 16. LLM / Generative AI
    # ---------------------------------------------------------

    llm_terms = [
        "llm",
        "large language model",
        "generative ai",
        "generative model",
        "gpt",
        "chatgpt",
        "claude",
        "midjourney",
        "transformer",
        "decoder",
        "encoder",
        "decoder-only",
        "model weights",
        "model weight",
        "weights",
        "pretrain",
        "pre-training",
        "pretraining",
        "final token",
        "token generation",
        "discriminative ai",
        "rule base",
        "rule-based",
        "temperature",
        "randomness",
        "text generation",
        "language model",
    ]

    if any(term in combined for term in llm_terms):
        return "LLM & Generative AI"

    # ---------------------------------------------------------
    # 17. AI Fundamentals
    # ---------------------------------------------------------

    ai_fundamental_terms = [
        "artificial intelligence",
        "ai fundamentals",
        "machine intelligence",
        "data lifecycle",
        "data lifecycle",
        "othello",
        "game",
        "game rules",
        "chess",
        "board game",
        "deep learning vs machine learning",
        "machine learning vs deep learning",
        "what is ai",
    ]

    if any(term in combined for term in ai_fundamental_terms):
        return "AI Fundamentals"

    # ---------------------------------------------------------
    # 18. Lecture-title fallback
    # ---------------------------------------------------------

    lecture_fallbacks = [
        (
            [
                "llm-foundation",
                "llm foundation",
                "ai-ml-dl",
                "ai ml dl",
            ],
            "AI Fundamentals",
        ),
        (
            [
                "prompt engineering",
                "prompt-engineering",
            ],
            "Prompt Engineering",
        ),
        (
            [
                "tool calling",
                "tool-calling",
                "react",
            ],
            "ReAct & Tool Calling",
        ),
        (
            [
                "memory",
            ],
            "Memory Systems",
        ),
        (
            [
                "vector store",
                "vector database",
                "qdrant",
            ],
            "RAG & Knowledge Systems",
        ),
        (
            [
                "fine-tuning",
                "fine tuning",
                "lora",
                "qlora",
            ],
            "Fine-tuning & Alignment",
        ),
        (
            [
                "data pipeline",
                "data engineering",
                "cdc",
                "kafka",
            ],
            "Data Pipeline Engineering",
        ),
        (
            [
                "lakehouse",
                "data lake",
            ],
            "Data Lakehouse",
        ),
        (
            [
                "observability",
                "monitoring",
                "logging",
            ],
            "Observability & Monitoring",
        ),
        (
            [
                "guardrails",
                "safety",
                "security",
            ],
            "AI Safety & Security",
        ),
        (
            [
                "cloud infrastructure",
                "cloud",
                "infrastructure",
            ],
            "Cloud & Infrastructure",
        ),
        (
            [
                "product discovery",
                "product thinking",
                "metrics",
            ],
            "AI Product & UX",
        ),
        (
            [
                "object detection",
                "object tracking",
                "multi-frame tracking",
            ],
            "Machine Learning & Computer Vision",
        ),
    ]

    for keywords, canonical in lecture_fallbacks:
        if any(keyword in lecture for keyword in keywords):
            return canonical

    # ---------------------------------------------------------
    # 19. Generic question → Other
    # ---------------------------------------------------------

    if topic_is_generic:
        return "Other"

    return "Other"