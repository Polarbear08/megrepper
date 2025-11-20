#!/bin/bash

# setup-env.sh
# セットアップ用のスクリプト - 全モジュール共通の環境変数をロード
#
# Usage:
#   source ./setup-env.sh
#   または
#   bash ./setup-env.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env.local"
ENV_SHARED_FILE="$SCRIPT_DIR/.env.shared"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Megrepper 環境変数セットアップ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""

# Check if .env.local or .env.shared exists
if [ ! -f "$ENV_FILE" ] && [ ! -f "$ENV_SHARED_FILE" ]; then
  echo -e "${YELLOW}⚠️  警告: 環境変数ファイルが見つかりません${NC}"
  echo ""
  echo "以下のいずれかを実行してください:"
  echo ""
  echo "  1. .env.shared.example から .env.shared を作成:"
  echo "     cp .env.shared.example .env.shared"
  echo "     # エディタで .env.shared を開いて値を入力"
  echo ""
  echo "  2. または .env.local を直接作成:"
  echo "     cp .env.shared.example .env.local"
  echo "     # エディタで .env.local を開いて値を入力"
  echo ""
  exit 1
fi

# Load environment variables
if [ -f "$ENV_FILE" ]; then
  echo "✓ $ENV_FILE から環境変数をロード"
  export $(cat "$ENV_FILE" | grep -v '^#' | grep -v '^$' | xargs)
elif [ -f "$ENV_SHARED_FILE" ]; then
  echo "✓ $ENV_SHARED_FILE から環境変数をロード"
  export $(cat "$ENV_SHARED_FILE" | grep -v '^#' | grep -v '^$' | xargs)
fi

echo ""
echo -e "${GREEN}✓ 環境変数をロード完了${NC}"
echo ""
echo "現在の設定:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  AWS_REGION:     ${AWS_REGION:-未設定}"
echo "  AWS_ACCOUNT_ID: ${AWS_ACCOUNT_ID:-未設定}"
echo "  APP_ENV:        ${APP_ENV:-未設定}"
echo "  APP_NAME:       ${APP_NAME:-未設定}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verify critical variables
if [ -z "$AWS_REGION" ]; then
  echo -e "${YELLOW}⚠️  警告: AWS_REGION が設定されていません${NC}"
fi

if [ -z "$AWS_ACCOUNT_ID" ] || [ "$AWS_ACCOUNT_ID" = "123456789012" ]; then
  echo -e "${YELLOW}⚠️  警告: AWS_ACCOUNT_ID が設定されていません${NC}"
fi

echo -e "${GREEN}セットアップ完了!${NC}"
echo ""
echo "次のステップ:"
echo "  1. frontend:    cd frontend && npm install"
echo "  2. backend:     cd backend && pip install -r requirements.txt"
echo "  3. infrastructure: cd infrastructure && npm install"
echo ""
