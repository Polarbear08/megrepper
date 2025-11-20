# Megrepper

JSON/YAML データから値を推測するブラウザベースのゲーム。React、Python FastAPI、AWS を使用した フルスタックアプリケーション。

## 📋 プロジェクト構成

```
megrepper/
├── frontend/              # React + TypeScript フロントエンド
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── backend/               # Python FastAPI バックエンド
│   ├── main.py
│   └── requirements.txt
├── infrastructure/        # AWS CDK インフラストラクチャ
│   ├── lib/
│   ├── package.json
│   ├── tsconfig.json
│   └── cdk.json
└── README.md
```

## 🏗️ アーキテクチャ

```
ユーザー (ブラウザ)
         ↓
   CloudFront (共通CDN)
    /        \
   /          \
S3 (静的)    API Gateway
(フロント)      ↓
             Lambda
             ↓
           DynamoDB
```

### フロントエンド
- **React + TypeScript**: ゲームUI
- **Vite**: ビルドツール
- **AWS S3**: 静的ファイル保存
- **AWS CloudFront**: CDN配信

### バックエンド
- **Python FastAPI**: REST API
- **AWS Lambda**: サーバーレス実行
- **AWS API Gateway**: API エンドポイント
- **AWS DynamoDB**: データストア (将来用途)

### インフラストラクチャ
- **AWS CDK (TypeScript)**: Infrastructure as Code

## 🚀 デプロイ手順

### 前提条件

```bash
# AWS CLIのインストール
aws --version

# AWS認証情報の設定
aws configure

# Node.jsのインストール（CDKと フロントエンド用）
node --version  # v18以上推奨

# Pythonのインストール（バックエンド用）
python --version  # v3.9以上推奨
```

### 1️⃣ インフラストラクチャのセットアップ

インフラストラクチャを最初にデプロイすることで、API Gateway URLなどの情報を取得します。

```bash
# infrastructure ディレクトリに移動
cd infrastructure

# 依存パッケージをインストール
npm install

# CDK スタックを構築
npm run build

# CDK スタック情報を表示
npm run cdk:synth

# AWS にデプロイ（初回）
npm run cdk:deploy
# プロンプトで "y" を入力して確認

# デプロイ完了後、Outputs に以下の情報が表示されます：
# - ApiEndpoint: API Gateway のエンドポイント
# - FrontendBucketName: フロントエンド用 S3 バケット名
# - CloudFrontDomain: CloudFront ドメイン名
```

**出力例：**
```
Outputs:
ApiEndpoint: https://xxxx.execute-api.ap-northeast-1.amazonaws.com/prod
FrontendBucketName: megrepper-frontend-bucket-xxxxx
CloudFrontDomain: dxxxxx.cloudfront.net
```

### 2️⃣ バックエンドのビルド・デプロイ

Lambda にデプロイ可能なコンテナイメージを作成します。

```bash
# backend ディレクトリに移動
cd ../backend

# Dockerfile を作成（下記参照）
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# コンテナイメージをビルド
docker build -t megrepper-backend:latest .

# AWS ECR にログイン（AWS アカウント ID とリージョンに置き換え）
aws ecr get-login-password --region ap-northeast-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.ap-northeast-1.amazonaws.com

# ECR リポジトリにイメージをプッシュ
docker tag megrepper-backend:latest \
  123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/megrepper-backend:latest

docker push 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/megrepper-backend:latest

# Lambda 関数を更新
# CDKで自動管理されている場合は、CDK再デプロイでも可
npm run cdk:deploy  # infrastructure ディレクトリから
```

### 3️⃣ フロントエンドのビルド・デプロイ

React アプリをビルドしてS3にアップロードします。

```bash
# frontend ディレクトリに移動
cd ../frontend

# 環境変数を設定（API エンドポイント）
export VITE_API_URL=https://xxxx.execute-api.ap-northeast-1.amazonaws.com/prod

# 依存パッケージをインストール
npm install

# ビルド
npm run build

# S3 にアップロード（バケット名は CDK デプロイ時の出力から）
aws s3 sync dist/ s3://megrepper-frontend-bucket-xxxxx/ \
  --delete \
  --cache-control "public, max-age=3600"

# index.html のみキャッシュ時間を短くする（頻繁に更新される）
aws s3 cp dist/index.html s3://megrepper-frontend-bucket-xxxxx/index.html \
  --cache-control "public, max-age=60" \
  --content-type "text/html"

# CloudFront キャッシュを無効化（新しいコンテンツをすぐに配信）
aws cloudfront create-invalidation \
  --distribution-id dxxxxx \
  --paths "/*"
```

### 🔄 デプロイフロー全体

```bash
# 1. インフラストラクチャ
cd infrastructure && npm install && npm run build && npm run cdk:deploy

# 2. バックエンド（必要な場合）
cd ../backend && docker build -t megrepper-backend:latest . && \
  docker push 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/megrepper-backend:latest

# 3. フロントエンド
cd ../frontend && npm install && npm run build && \
  aws s3 sync dist/ s3://megrepper-frontend-bucket-xxxxx/ --delete
```

## 🛑 リソースの削除

AWS のリソースを削除して料金がかからないようにします。

```bash
# infrastructure ディレクトリから
cd infrastructure

# CDK スタックを削除
npm run cdk:destroy

# プロンプトで削除を確認
# Are you sure you want to delete: MegrepperStack (y/n)? → y
```

## 📝 開発環境での実行

### ローカル開発（フロント + バック同時実行）

```bash
# ターミナル 1: バックエンド
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000

# ターミナル 2: フロントエンド
cd frontend
npm install
npm run dev
# ブラウザで http://localhost:3000 を開く
```

Vite の `proxy` 設定により、`/api` リクエストが自動的に `localhost:8000` に転送されます。

## 🧪 テスト

```bash
# フロントエンドのテスト
cd frontend
npm test

# インフラストラクチャのテスト
cd infrastructure
npm test
```

## 📚 ファイル構成説明

### frontend/
| ファイル | 説明 |
|---|---|
| `src/main.tsx` | React アプリケーション エントリーポイント |
| `src/App.tsx` | メインゲームコンポーネント |
| `src/App.css` | ゲームUI スタイル |
| `vite.config.ts` | Vite ビルド設定とAPI プロキシ設定 |

### backend/
| ファイル | 説明 |
|---|---|
| `main.py` | FastAPI サーバーとゲームロジック |
| `requirements.txt` | Python 依存パッケージ |

### infrastructure/
| ファイル | 説明 |
|---|---|
| `lib/index.ts` | CDK App エントリーポイント |
| `lib/megrepper-stack.ts` | AWS リソース定義 |
| `cdk.json` | CDK 設定ファイル |

## 🔧 トラブルシューティング

### CDK デプロイが失敗する場合

```bash
# 認証情報を確認
aws sts get-caller-identity

# CDK bootstrap が必要な場合
cd infrastructure
npx cdk bootstrap aws://ACCOUNT-ID/REGION
```

### S3 アップロードが失敗する場合

```bash
# バケット名を確認
aws s3 ls | grep megrepper

# IAM ポリシーを確認
aws iam get-user
```

### Lambda が起動しない場合

```bash
# CloudWatch ログを確認
aws logs tail /aws/lambda/megrepper-backend --follow
```

## 📖 参考リンク

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/latest/guide/home.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/latest/userguide/)

## 📄 ライセンス

MIT

