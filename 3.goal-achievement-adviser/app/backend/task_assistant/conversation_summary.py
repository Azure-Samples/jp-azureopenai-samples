prompt_system = """
あなたはHTMLで文章を作成するアシスタントです。
"""

prompt_user = """
ユーザーは以下の目標を持っています。
{theme}

私たちはこの目標を達成するための手順と詳細をユーザーとディスカッションしてきました。

ディスカッションに含まれるJSONデータは以下の構成です。
・'steps' リストの各要素は、1番目が'step_num', 2番目が'content', 3番目が'variable_name', 4番目が'value'というキー。
・テーブル出力用に日本語列名を記述したheadersという配列。
・変数名は英語
・手順以外の文章は'answer'または'support'キーにセット
・'situation'はユーザーが与えた現在の状況の要約
・'support'はユーザーの回答に助けになる情報
・'answer'はユーザーに回答してもらいたい回答
・それ以外の文章は'answer'にセット

いままでのやりとりを文章にして議事録形式でHTMLで出力してください。上記のJSONフォーマットでは出力しないでください。

HTMLには以下の内容を含めてください。
・タイトル: お客様の目標のサマリ。20文字以内で。
・目標: お客様の目標
・目標達成までの手順と各手順をなるべく詳細に記載してください。
・具体的なアクション。スケジュールが設定されている場合はタイムラインも含む。

HTMLデータの前と後に文章はつけず、必ずHTMLデータだけ返してください。HTMLタグ <html>,<head><body>を含めたフルセットのHTMLにしてください。
HTMLにはJSONデータに含まれていた'変数名'は含めないでください。
HTMLタグは全て小文字にしてください。HTMLは白い背景で、テーブルを使う場合はヘッダーの背景色は薄いグレーにしてください。
"""


def get_comversation_summary_prompt(theme, messages):
    prompt_user_formatted = prompt_user.format(theme=theme)

    return [
        {"role": "system", "content": prompt_system},
        {"role": "user", "content": prompt_user_formatted},
    ] + messages
