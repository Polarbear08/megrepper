import json
import random
import os
import boto3
from typing import Any, Dict, List

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'GameDataTable'))


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for Megrepper API"""
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')
    body = json.loads(event.get('body', '{}')) if event.get('body') else {}

    try:
        if path == '/api/question' and http_method == 'POST':
            return handle_question(body)
        elif path == '/api/check-answer' and http_method == 'POST':
            return handle_check_answer(body)
        elif path == '/api/health' and http_method == 'GET':
            return handle_health()
        else:
            return error_response(404, 'Endpoint not found')
    except Exception as e:
        print(f'Error: {str(e)}')
        return error_response(500, str(e))


def handle_question(body: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a question from the provided data"""
    data = body.get('data', {})
    if not data:
        return error_response(400, 'Data is required')

    data_format = random.choice(['json', 'yaml'])

    # キーのリストを取得
    keys = list(data.keys())
    if not keys:
        return error_response(400, 'Data must have at least one key')

    # ランダムにキーを選択
    question_key = random.choice(keys)
    correct_answer = data[question_key]

    # 4択の選択肢を生成
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

    # 選択肢が4つ未満の場合はダミー値を追加
    while len(options_set) < 4:
        if isinstance(correct_answer, (int, float)):
            options_set.add(json.dumps(random.randint(0, 100), default=str))
        elif isinstance(correct_answer, str):
            options_set.add(json.dumps(f'dummy_{len(options_set)}', default=str))
        else:
            options_set.add(json.dumps(None, default=str))

    # JSON文字列をパースして、リストに変換
    options = [json.loads(v) for v in list(options_set)]
    random.shuffle(options)

    # データ形式に応じてデータを表示用に変換
    if data_format == 'yaml':
        try:
            import yaml
            data_display = yaml.dump(data, default_flow_style=False, allow_unicode=True)
        except ImportError:
            # yamlがない場合はJSONで対応
            data_display = json.dumps(data, indent=2, ensure_ascii=False)
    else:
        data_display = json.dumps(data, indent=2, ensure_ascii=False)

    return success_response({
        'question_key': question_key,
        'correct_answer': correct_answer,
        'options': options,
        'data_format': data_format,
        'data_display': data_display,
    })


def handle_check_answer(body: Dict[str, Any]) -> Dict[str, Any]:
    """Check if the answer is correct"""
    correct_answer = body.get('correct_answer')
    user_answer = body.get('user_answer')

    if correct_answer is None or user_answer is None:
        return error_response(400, 'correct_answer and user_answer are required')

    is_correct = correct_answer == user_answer

    return success_response({
        'is_correct': is_correct,
        'correct_answer': correct_answer,
    })


def handle_health() -> Dict[str, Any]:
    """Health check endpoint"""
    return success_response({'status': 'ok'})


def success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Return a successful response"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(data),
    }


def error_response(status_code: int, message: str) -> Dict[str, Any]:
    """Return an error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps({'error': message}),
    }
