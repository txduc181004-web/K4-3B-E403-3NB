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

    # ========================================================
    # 1. REACT / TOOL CALLING / AGENT ARCHITECTURE
    # ========================================================

    react_keywords = [
        "react",
        "re-act",
        "tool calling",
        "function calling",
        "tool call",
        "mcp",
        "model context protocol",
        "multi-agent",
        "multi agent",
        "multi-agent",
        "langgraph",
        "agent architecture",
        "agent architectures",
        "agent design",
        "agentic agent",
        "autonomy in agent",
        "full autonomy",
        "idempotency in agent",
        "agent loop",
        "agent loop",
        "orchestration",
        "scaffolding",
        "parallelization",
        "parallelization giúp",
        "agent gọi tool",
        "gọi tool liên tục",
        "tool liên tục",
        "action input",
        "action: <name>",
        "tool calling",
        "rule, workflow, hay agent",
    ]

    if any(keyword in combined for keyword in react_keywords):
        return "ReAct & Tool Calling"


    # ========================================================
    # 2. MEMORY
    # ========================================================

    memory_keywords = [
        "memory system",
        "memory systems",
        "long-term memory",
        "short-term memory",
        "long term memory",
        "short term memory",
        "episodic memory",
        "semantic memory",
        "working memory",
        "sliding window",
        "memory for agents",
    ]

    if any(keyword in combined for keyword in memory_keywords):
        return "Memory Systems"


    # ========================================================
    # 3. RAG / KNOWLEDGE SYSTEMS
    # ========================================================

    rag_keywords = [
        "rag",
        "retrieval augmented",
        "retrieval-augmented",
        "retrieval",
        "embedding",
        "embeddings",
        "vector database",
        "vector store",
        "vector search",
        "qdrant",
        "chroma",
        "chromadb",
        "reranker",
        "reranking",
        "knowledge graph",
        "ann",
        "knn",
        "similarity search",
    ]

    if any(keyword in combined for keyword in rag_keywords):
        return "RAG & Knowledge Systems"


    # ========================================================
    # 4. FINE-TUNING
    # ========================================================

    finetune_keywords = [
        "fine-tuning",
        "fine tuning",
        "finetuning",
        "lora",
        "qlora",
        "dpo",
        "orpo",
        "rlhf",
        "sft",
        "alignment",
    ]

    if any(keyword in combined for keyword in finetune_keywords):
        return "Fine-tuning & Alignment"


    # ========================================================
    # 5. DATA PIPELINE
    # ========================================================

    pipeline_keywords = [
        "data pipeline",
        "data pipelines",
        "etl",
        "elt",
        "cdc",
        "debezium",
        "kafka",
        "spark",
        "duckdb",
        "dbt",
        "ingestion",
        "replication slot",
        "replication",
        "log-based",
        "log based",
        "data ingestion",
        "data replication",
        "arrow",
    ]

    if any(keyword in combined for keyword in pipeline_keywords):
        return "Data Pipeline Engineering"


    # ========================================================
    # 6. DATA LAKEHOUSE
    # ========================================================

    lakehouse_keywords = [
        "data lake",
        "data lakehouse",
        "lakehouse",
        "medallion architecture",
        "bronze",
        "silver",
        "gold layer",
        "delta lake",
        "iceberg",
    ]

    if any(keyword in combined for keyword in lakehouse_keywords):
        return "Data Lakehouse"


    # ========================================================
    # 7. OBSERVABILITY
    # ========================================================

    observability_keywords = [
        "observability",
        "monitoring",
        "logging",
        "tracing",
        "telemetry",
        "metrics",
        "error taxonomy",
        "error matrix",
        "distributed tracing",
        "harness",
        "trace mọi thứ",
        "trace",
    ]

    if any(keyword in combined for keyword in observability_keywords):
        return "Observability & Monitoring"


    # ========================================================
    # 8. MLOPS / EVALUATION
    # ========================================================

    mlops_keywords = [
        "mlops",
        "evaluation",
        "evaluator",
        "benchmark",
        "ground truth",
        "test set",
        "testset",
        "accuracy",
        "precision",
        "recall",
        "f1",
        "latency",
        "goodput",
        "inference optimization",
        "kv cache",
        "ci/cd",
        "retry",
        "backoff",
        "experiment",
        "control group",
        "treatment group",
        "a/b test",
        "ab test",
    ]

    if any(keyword in combined for keyword in mlops_keywords):
        return "MLOps & AI Evaluation"


    # ========================================================
    # 9. CLOUD / INFRASTRUCTURE
    # ========================================================

    cloud_keywords = [
        "cloud infrastructure",
        "cloud",
        "infrastructure",
        "docker",
        "linux",
        "windows",
        "deployment",
        "production environment",
        "production",
        "high availability",
        "disaster recovery",
        "circuit breaker",
        "caching",
        "paas",
        "platform engineering",
        "migration",
        "virtual environment",
        "venv",
        "github",
        "repository",
        "repo",
        "colab",
    ]

    if any(keyword in combined for keyword in cloud_keywords):
        return "Cloud & Infrastructure"


    # ========================================================
    # 10. AI SAFETY / SECURITY
    # ========================================================

    safety_keywords = [
        "guardrail",
        "guardrails",
        "ai safety",
        "ai security",
        "prompt injection",
        "jailbreak",
        "privacy",
        "governance",
        "opa",
        "audit",
        "access token",
        "security policy",
        "human in the loop",
        "hitl",
    ]

    if any(keyword in combined for keyword in safety_keywords):
        return "AI Safety & Security"


    # ========================================================
    # 11. PROMPT ENGINEERING
    # ========================================================

    prompt_keywords = [
        "prompt engineering",
        "prompt",
        "system prompt",
        "zero-shot",
        "zero shot",
        "one-shot",
        "one shot",
        "few-shot",
        "few shot",
        "temperature",
        "top-k",
        "top k",
        "top-p",
        "top p",
        "tiktoken",
        "tokenization",
        "context window",
        "lost in the middle",
        "cot",
        "chain of thought",
        "overkill",
    ]

    if any(keyword in combined for keyword in prompt_keywords):
        return "Prompt Engineering"


    # ========================================================
    # 12. AI PRODUCT / UX
    # ========================================================

    product_keywords = [
        "ai product management",
        "ai product manager",
        "ai product",
        "product discovery",
        "product thinking",
        "user story",
        "user stories",
        "jtbd",
        "jobs to be done",
        "persona",
        "acceptance criteria",
        "requirement quality",
        "value clarity",
        "leap of faith",
        "business problem",
        "problem statement",
        "mvp",
        "agile",
        "story point",
        "functional và non-functional",
        "functional vs non-functional",
        "augmentation",
        "automation",
        "pair",
        "quyết định dùng ai",
        "functional và non-functional",
        "functional vs non-functional",
        "augmentation và automation",
        "augmentation vs automation",
    ]

    if any(keyword in combined for keyword in product_keywords):
        return "AI Product & UX"


    # ========================================================
    # 13. MACHINE LEARNING / COMPUTER VISION
    # ========================================================

    ml_cv_keywords = [
        "machine learning",
        "deep learning",
        "cnn",
        "rnn",
        "svm",
        "kernel trick",
        "object detection",
        "object tracking",
        "bytetrack",
        "yolo",
        "iou",
        "cuboid",
        "lidar",
        "pose",
        "keypoint",
        "ultralytics",
        "classification",
        "convolution",
        "attention",
        "train và model đoán sai",
        "tinh chỉnh model",
        "dữ liệu chuẩn",
        "dữ liệu train",
        "dữ liệu đó đi hỏi lại ai",
        "chọn đặc trưng",
        "tự tìm ra đặc trưng",
        "gắn nhãn",
        "multi-object tracking",
        "multiframe tracking",
        "multi frame tracking",
        "mota",
        "track prediction",
        "dự đoán track",
    ]

    if any(keyword in combined for keyword in ml_cv_keywords):
        return "Machine Learning & Computer Vision"


    # ========================================================
    # 14. LLM / GENERATIVE AI
    # ========================================================

    llm_keywords = [
        "llm",
        "large language model",
        "generative ai",
        "generative model",
        "gpt",
        "chatgpt",
        "claude",
        "transformer",
        "decoder",
        "encoder",
        "model weights",
        "model weight",
        "pretraining",
        "pre-train",
        "pretrain",
        "text generation",
        "token selection",
        "randomness",
        "foundation model",
        "core model",
        "model comparison",
        "model decision",
        "openai",
        "model cốt lõi",
        "model core",
        "tính ngẫu nhiên của văn bản",
        "token có xác suất cao nhất",
        "tính sáng tạo của văn bản",
    ]

    if any(keyword in combined for keyword in llm_keywords):
        return "LLM & Generative AI"


    # ========================================================
    # 15. CHATBOT / AI AGENT
    # ========================================================

    chatbot_keywords = [
        "chatbot",
        "conversational ai",
        "virtual assistant",
        "ai assistant",
    ]

    if any(keyword in combined for keyword in chatbot_keywords):
        return "Chatbot & AI Agent"


    # ========================================================
    # 16. AI FUNDAMENTALS
    # ========================================================

    fundamentals_keywords = [
        "artificial intelligence",
        "ai fundamentals",
        "machine intelligence",
        "expert system",
        "expert systems",
        "ai winter",
        "winter of ai",
        "ai history",
        "ai levels",
        "discriminative ai",
        "othello",
        "game rules",
        "ván cờ",
        "luật chơi",
        "mùa đông ai",
        "ai, ml và dl",
        "ai ml dl",
    ]

    if any(keyword in combined for keyword in fundamentals_keywords):
        return "AI Fundamentals"


    # ========================================================
    # 17. FALLBACK
    # ========================================================

    return "Other"