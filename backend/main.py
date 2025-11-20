import json
import random
import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List

app = FastAPI(title="Megrepper API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ゲームデータを生成する関数
def generate_question(data: Dict[str, Any], data_format: str = "json") -> Question:
    """ランダムなキーを選択して問題を生成"""
    # キーのリストを取得（第一階層のみ）
    keys = list(data.keys())
    if not keys:
        raise ValueError("Data must have at least one key")

    question_key = random.choice(keys)
    correct_answer = data[question_key]

    # 4択の選択肢を生成
    # 同じ値が複数あるかもしれないので、ユニークな値を取得
    all_values = list(data.values())
    unique_values = list(set(
        json.dumps(v, sort_keys=True, default=str) for v in all_values
    ))

    # 正解を含む4つの選択肢を作成
    options_set = set()
    options_set.add(json.dumps(correct_answer, sort_keys=True, default=str))

    # ランダムに他の値を選択
    other_values = [v for v in unique_values
                    if v != json.dumps(correct_answer, sort_keys=True, default=str)]
    random.shuffle(other_values)

    for v in other_values[:3]:
        options_set.add(v)
        if len(options_set) == 4:
            break

    # 選択肢が4つ未満の場合は、ダミー値を追加
    while len(options_set) < 4:
        if isinstance(correct_answer, (int, float)):
            options_set.add(json.dumps(random.randint(0, 100), default=str))
        elif isinstance(correct_answer, str):
            options_set.add(json.dumps(f"dummy_{len(options_set)}", default=str))
        else:
            options_set.add(json.dumps(None, default=str))

    # JSON文字列をパースして、リストに変換
    options = [json.loads(v) for v in list(options_set)]
    random.shuffle(options)

    # データ形式に応じてデータを表示用に変換
    if data_format == "yaml":
        data_display = yaml.dump(data, default_flow_style=False, allow_unicode=True)
    else:
        data_display = json.dumps(data, indent=2, ensure_ascii=False)

    return Question(
        question_key=question_key,
        correct_answer=correct_answer,
        options=options,
        data_format=data_format,
        data_display=data_display
    )

@app.post("/api/question")
async def create_question(request: QuestionRequest):
    """ランダムな問題を生成"""
    # JSONとYAMLをランダムに選択
    data_format = random.choice(["json", "yaml"])
    return generate_question(request.data, data_format)

@app.post("/api/check-answer")
async def check_answer(request: CheckAnswerRequest):
    """回答をチェック"""
    is_correct = request.correct_answer == request.user_answer
    return CheckAnswerResponse(
        is_correct=is_correct,
        correct_answer=request.correct_answer
    )

@app.get("/api/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "ok"}
