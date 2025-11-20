import json
import random
import yaml
import string
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List
from logger import logger

app = FastAPI(title="Megrepper API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Megrepper API initialized")


# リクエスト・レスポンスモデル
class QuestionRequest(BaseModel):
    data: Dict[str, Any]


class Question(BaseModel):
    question_key: str
    correct_answer: Any
    options: List[Any]
    data_format: str  # "json" or "yaml"
    data_display: str


class CheckAnswerRequest(BaseModel):
    correct_answer: Any
    user_answer: Any


class CheckAnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: Any


def extract_leaf_values(data: Any) -> List[Any]:
    """データ構造からリーフノード（スカラー値）のみを抽出"""
    leaf_values = []

    if isinstance(data, dict):
        for value in data.values():
            leaf_values.extend(extract_leaf_values(value))
    elif isinstance(data, list):
        for item in data:
            leaf_values.extend(extract_leaf_values(item))
    else:
        # スカラー値（int, float, str, bool, None）
        leaf_values.append(data)

    return leaf_values


def extract_all_key_paths(data: Any, prefix: str = "") -> List[tuple[str, Any]]:
    """
    データ構造からリーフノード（スカラー値）のキーパス（ドット記法）と値のペアを抽出
    例: {"a": {"b": "c"}} -> [("a.b", "c")]
    """
    paths = []

    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{prefix}.{key}" if prefix else key
            # リーフノード（スカラー値）のみを追加
            if not isinstance(value, (dict, list)):
                paths.append((current_path, value))
            else:
                # ネストされたデータを再帰的に処理
                paths.extend(extract_all_key_paths(value, current_path))
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            current_path = f"{prefix}[{idx}]" if prefix else f"[{idx}]"
            # リーフノード（スカラー値）のみを追加
            if not isinstance(item, (dict, list)):
                paths.append((current_path, item))
            else:
                # ネストされたデータを再帰的に処理
                paths.extend(extract_all_key_paths(item, current_path))

    return paths


def generate_random_key(prefix: str = "") -> str:
    """ランダムなキー名を生成"""
    key_names = [
        "name", "age", "email", "city", "country", "product", "price",
        "user_id", "status", "title", "description", "value", "type",
        "id", "data", "info", "config", "settings", "metadata",
        "attributes", "properties", "result", "message", "timestamp",
        "version", "category", "level", "score"
    ]
    return random.choice(key_names)


def generate_random_data(
    max_depth: int = 3, min_depth: int = 3, current_depth: int = 0
) -> Dict[str, Any]:
    """3階層を限度とするランダムなJSON/YAMLデータを生成"""
    logger.debug(
        f"Generating random data: max_depth={max_depth}, "
        f"min_depth={min_depth}, current_depth={current_depth}"
    )
    data = {}

    # ランダムなキー数（1～5個）を生成
    num_keys = random.randint(1, 5)

    for _ in range(num_keys):
        key = generate_random_key()

        # キーが重複しないようにする
        while key in data:
            key = generate_random_key()

        # 値の種類をランダムに決定
        value_type = random.choice(["string", "number", "boolean", "nested"])

        # 最小階層に達していない場合は必ずネストする
        if current_depth < min_depth - 1:
            value_type = "nested"
        # 最大階層に達したか、ランダムに単純な値を選ぶ
        elif current_depth >= max_depth - 1:
            value_type = random.choice(["string", "number", "boolean"])

        if value_type == "string":
            # 文字列値を生成
            string_types = [
                lambda: ''.join(
                    random.choices(
                        string.ascii_letters, k=random.randint(3, 10)
                    )
                ),
                lambda: f"user_{random.randint(1, 1000)}",
                lambda: random.choice(
                    ["Tokyo", "New York", "London", "Paris", "Sydney"]
                ),
                lambda: random.choice(
                    ["active", "inactive", "pending", "completed"]
                ),
            ]
            data[key] = random.choice(string_types)()

        elif value_type == "number":
            # 数値を生成
            number_type = random.choice(["int", "float"])
            if number_type == "int":
                data[key] = random.randint(0, 1000)
            else:
                data[key] = round(random.uniform(0, 100), 2)

        elif value_type == "boolean":
            # ブール値を生成
            data[key] = random.choice([True, False])

        elif value_type == "nested":
            # ネストされたデータを再帰的に生成
            data[key] = generate_random_data(max_depth, min_depth, current_depth + 1)

    return data


def generate_question(data_format: str = "json") -> Question:
    """ランダムなキーを選択して問題を生成（3階層に限定）"""
    logger.debug(f"Generating question with format: {data_format}")
    # ランダムにデータを生成（max_depth=3で3階層に限定）
    data = generate_random_data(max_depth=3, min_depth=3)

    # すべてのキーパス（ドット記法）を取得
    all_key_paths = extract_all_key_paths(data)
    if not all_key_paths:
        raise ValueError("Data must have at least one key")

    question_key, correct_answer = random.choice(all_key_paths)

    # 4択の選択肢を生成
    # リーフノードのみを抽出し、ユニークな値を取得
    all_leaf_values = extract_leaf_values(data)
    unique_values = list(set(
        json.dumps(
            v, sort_keys=True, default=str
        ) for v in all_leaf_values
    ))

    # 正解を含む4つの選択肢を作成
    options_set = set()
    correct_answer_json = json.dumps(
        correct_answer, sort_keys=True, default=str
    )
    options_set.add(correct_answer_json)

    # ランダムに他の値を選択
    other_values = [
        v for v in unique_values if v != correct_answer_json
    ]
    random.shuffle(other_values)

    for v in other_values[:3]:
        options_set.add(v)
        if len(options_set) == 4:
            break

    # 選択肢が4つ未満の場合は、ダミー値を追加
    while len(options_set) < 4:
        if isinstance(correct_answer, (int, float)):
            options_set.add(
                json.dumps(random.randint(0, 100), default=str)
            )
        elif isinstance(correct_answer, str):
            options_set.add(
                json.dumps(f"dummy_{len(options_set)}", default=str)
            )
        else:
            options_set.add(json.dumps(None, default=str))

    # JSON文字列をパースして、リストに変換
    options = [json.loads(v) for v in list(options_set)]
    random.shuffle(options)

    # データ形式に応じてデータを表示用に変換
    if data_format == "yaml":
        data_display = yaml.dump(
            data, default_flow_style=False, allow_unicode=True
        )
    else:
        data_display = json.dumps(
            data, indent=2, ensure_ascii=False
        )

    return Question(
        question_key=question_key,
        correct_answer=correct_answer,
        options=options,
        data_format=data_format,
        data_display=data_display
    )


@app.post("/api/question")
async def create_question(request: QuestionRequest = None):
    """ランダムな問題を生成"""
    logger.info("Request received: /api/question")
    try:
        # JSONとYAMLをランダムに選択
        data_format = random.choice(["json", "yaml"])
        question = generate_question(data_format)
        logger.info(
            f"Question generated successfully: "
            f"key={question.question_key}, format={data_format}"
        )
        return question
    except Exception as e:
        logger.error(f"Error generating question: {str(e)}", exc_info=True)
        raise


@app.post("/api/check-answer")
async def check_answer(request: CheckAnswerRequest):
    """回答をチェック"""
    logger.info("Request received: /api/check-answer")
    try:
        is_correct = request.correct_answer == request.user_answer
        if is_correct:
            logger.info(f"Correct answer received: {request.user_answer}")
        else:
            logger.warn(
                f"Incorrect answer received: user_answer="
                f"{request.user_answer}, correct_answer="
                f"{request.correct_answer}"
            )
        return CheckAnswerResponse(
            is_correct=is_correct,
            correct_answer=request.correct_answer
        )
    except Exception as e:
        logger.error(f"Error checking answer: {str(e)}", exc_info=True)
        raise


@app.get("/api/health")
async def health_check():
    """ヘルスチェック"""
    logger.debug("Health check requested")
    return {"status": "ok"}
