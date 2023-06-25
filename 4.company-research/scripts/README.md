# ナレッジベースに企業の最新情報を登録
ローカル PC から実行してナレッジベースに企業の最新情報を登録します。
- PC から Redis Cache のポート 10000 にアクセスできる必要があります。
- 実行前に Azure Open AI (モデルもデプロイ済み) および ナレッジベースである Azure Redis Enterprise (RediSearch 有効化) が事前にデプロイされている必要があります。

## Python ライブラリのインストール
### Condaを使う手法
本アプリケーションの開発では [Miniconda 3](https://docs.conda.io/en/latest/miniconda.html) で Python 3.10 の仮想環境を作りました。

Anaconda/Miniconda の仮想環境の作成例です。
```bash
cd scripts
conda create -n gpt-console python=3.10
conda activate gpt-console
pip install -r requirements.txt
```

### VS CodeでDevelopment containerを使う手法
1. VS Codeを起動します。
2. 「View」メニューを開き、「Command Palette」を選択します。
3. 「Command Palette」にて、「Remote-Containers: Open Folder in Container...」を入力し、リストから選択します。
4. ファイルダイアログが表示されるので、Dev Containerの設定が含まれているフォルダ（.devcontainer ディレクトリが存在する場所）を選択します。
5. VS Codeが新しいウィンドウを開き、選択したフォルダのDev Container内で開きます。初回起動時は、Dockerfileに基づいてコンテナのビルドが行われます。

## .env の変更
[.env.template](.env.template) を .env に変更します。
```bash
cp .env.template .env
```

そして以下の項目を設定します。
| Key | Value |
|------|------|
| AZURE_OPENAI_API_TYPE | azure |
| AZURE_OPENAI_SERVICE | Your endpoint for Azure Open AI 例: `https://youropenai.openai.azure.com/` |
| AZURE_OPENAI_API_KEY | Your API KEY for Azure Open AI |
| AZURE_OPENAI_VERSION | 2023-05-15 |
| AZURE_OPENAI_EMBEDDING_DEPLOYMENT | Your deployed text-embedding-ada-002 based model name |
| REDIS_NAME | Your endpoint for Redis Enterprise e.g. yourredis.southcentralus.redisenterprise.cache.azure.net |
| REDIS_KEY | Your KEY for Redis Enterprise |
| REDIS_INDEX_CATEGORY | company |
| REDIS_INDEX_NAME | embedding_index |
| REDIS_CATEGORY_COMMON | company_common |
| REDIS_CATEGORY_TOPICS | company_topics |

RediSearch のインデックス名は [REDIS_INDEX_CATEGORY]_[REDIS_INDEX_NAME] になります。
例: company_embedding_index

## データソースの確認
### サンプルデータ
本レポジトリには以下のサンプルデータが含まれており、こちらがナレッジベースに登録されます
- [企業の基本情報](company_common.json)
- [トピック別追加情報（日本語）](company_topics_ja.jsonl)
- [トピック別追加情報（英語）](company_topics_en.jsonl)

### データソース追加（任意）
取り込みたい企業情報を各種データソースから収集して JSON ファイルに追加してください。

企業情報が載っているデータソースは DBMS, HTML, PDF, 音声 など多様であり、この JSON のように整形されているとは限りませんので、DBMS, OCR, Speech  といった様々な技術を組み合わせてデータを収集する必要があります。

文章からデータを抽出/加工/要約する場合 Azure Open AI 自身も有用なソリューションです。

以下は企業データ (JSON) の主な要素です。必須項目はアプリケーションが必ず参照するものです。その他の項目はインダストリに合わせて自由に編集できます(例: 配送所の所有トラック数、工場の 製造ライン情報、POS の機種番号 など)。

|要素|役割|
|------|------|
|name(必須)|企業名|
|locale(必須)|企業の所在地 (例 en-us, ja-jp)。Web UIはこのロケールから表のラベルや ChatGPT に質問する言語を変更します|
|revenue|売上高。過去3年分を登録します。画面には最新の値 (company_data.jsでは2022年が最新)が表示されます。その他の総売上高といった数値データも同様の動きです |
|competitors|競合企業。この情報を元に競合企業を検索します|
|data_source(必須)|label: 画面表示時のラベル, url: 参照元|

## 企業情報テキストの確認（任意）
[gpt_locale.py](gpt_locale.py) の get_company_description 関数は対象企業の情報を日本語や英語の文章に整形して返します。この文章はナレッジストアに保存され、ChatGPT との会話前に知識として渡されます。そのため ChatGPT に認識させたい情報がある場合は、この関数を編集してください。この関数が返した文章は Redis Cache の内部に "text" という要素で保存されます。

## アプリケーションの実行
.env と企業データ(company_data.json)の変更後, gpt_manage_embedding.py を実行すると、ナレッジベース(RediSearch)に企業データと検索用の Embedding が登録されます。

スクリプト作成者のAzure OpenAI Serviceには、最大1分に1回の呼出し制限がかかっているため、`time.sleep(60)`を入れており、6社+169トピックの情報を登録するのに約175分(約3時間)の時間がかかります。

gpt_manage_embedding.py は以下の機能を提供します。

| 関数 | 役割 |
|------|------|
| clear_cache | Redis のキャッシュデータを全て削除します|
| register_cache_index | Redis のキャッシュインデックスを再作成します|
| register_companies |JSON ファイル(.json)に登録された企業情報を Embedding データと合わせて Redis Cache に登録します|
| query all| Redis Cache のすべての Embedding データを取得します|
| query |キーワードにヒットする Embedding データを取得します|
| get_gpt_token_count |文字列に対するトークンサイズを取得します(Azure OpenAI には接続しないため、実投入前のドライランとして利用できます)|