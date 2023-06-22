import openai

prompt_template_1 ="""
あなたは家族の料理担当です。家族のプロフィールと不足している栄養に基づいて、以下の質問を家族に話すようにフランクわかりやすく回答してください。

家族のプロフィール:${family_profile}
不足している栄養素:${missing_nutrient}

"""

prompt_template_2 ="""
・不足している栄養素が必要な理由
・不足している栄養素の補給に必要な食材を5つ
・食材が栄養素の補給に有効な理由
・栄養素の補給に必要な食材の効果的な調理方法

回答は以下のようなJSONデータにしてください。
"recommend_reason" キーには不足している栄養素が必要な理由をセットしてください。
"recommended_ingredients" キーには不足している栄養素の補給に必要な食材を5つのリストをセットしてください。各食材の先頭には・を付けてください。
"recommend_ingredients_reason" 食材が不足している栄養素の補給に有効な理由。
"recommend_ingredients_cooking" キーには栄養素の補給に必要な食材の効果的な調理方法をセットしてください。

以下のJSONデータの例です。
{
    "recommend_reason" : "タンパク質は体を作るのに有効です",
    "recommended_ingredients" : "・鶏のむね肉・大豆",
    "recommend_ingredients_reason" : "鶏のむね肉には豊富なタンパク質が含まれており、脂肪分も少なくヘルシーです。大豆も植物性タンパク質が豊富に含まれています。",
    "recommend_ingredients_cooking": "鶏のむね肉は蒸すとヘルシーです。大豆は醤油とみりんで煮ると効果的です"
}

必ず上記JSONデータを返し、JSONデータの前と後に文章はつけず、必ずJSONデータだけ返してください。
"""

def get_food_advisory(completion_deployment, family_profile, missing_nutrient):

    prompt = prompt_template_1.format(family_profile=family_profile, missing_nutrient=missing_nutrient) + prompt_template_2

    completion = openai.Completion.create(
        engine=completion_deployment, 
        prompt=prompt, 
        temperature=0.5, 
        max_tokens=1000, 
        n=1)

    return completion