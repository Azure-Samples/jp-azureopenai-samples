import openai

prompt_template_1 ="""
あなたは家族の料理担当です。
後述の家族のプロフィールに配慮した料理メニューを提案してください。同じ後述の家族の要望も出来る限り取り入れてください。
料理メニューは家族の要望がなければ主菜、副菜、主食、汁物を1品ずつ提案してください。
料理メニューにはそれぞれ消費カロリーをつけてください。
料理メニューの調理に必要な食材をリストアップしてください。
家にある材料をなるべく使い、家に無い材料をリストアップしてください。
家族のプロフィールをどのように配慮して料理メニューを提案したかを記述してください。

家族のプロフィール:${family_profile}
家にある食材:${ingredients_have}
家族の要望:${user_menu_request}

"""

prompt_template_2 ="""
回答は以下のスキーマに沿ったJSONデータを返してください。
・ "menu" キーには料理メニューの一覧をセットしてください。
・ "reason" キーには料理メニューの理由セットしてください。
・ "main_dish" キーには料理メニューのうち主菜の名前をセットしてください。
・ "ingredients_with_amount" キーには料理メニューに必要な材料と分量を、料理ごとにリストでセットしてください。各要素の先頭には・をつけてください。各要素の末尾で改行してください。
・ "recipes" キーには料理の名前とレシピをリスト形式でセットしてください。 "menu" キーは料理の名前です。"step" キーはレシピの手順です。
・ "ingredients_not_have" キーには材料のうち家にないものをリストでセットしてください。各要素の先頭には・をつけてください。各要素の末尾で改行してください。
必ず上記ルールのJSONデータだけを返してください。JSONデータの前と後に平文はつけないでください。
以下はJSONデータの例です。
{
    "menu" : "主菜:鶏の唐揚げ 副菜:ほうれん草のおひたし 主食:ごはん 汁物:みそ汁",
    "main_dish" : "鶏の唐揚げ",
    "ingredients_with_amount" : "・鶏もも肉:200g・たまご(1個)・小麦粉(適量)・サラダ油(適量)・ほうれん草(1束・ごま油(適量)・ごはん(1合・味噌(大さじ1)・だし汁(カップ1/2)",
    "recipes": [
        {
            "menu" : "鶏の唐揚げ",
            "step" : "鶏もも肉を一口大に切り、小麦粉をまぶす。たまごを溶きほぐし、鶏肉にからめる。サラダ油を熱したフライパンで鶏肉を両面こんがりと揚げる。"
        },
        {
            "menu" : "ほうれん草のおひたし",
            "step" : "ほうれん草は根元を切り落とし、軽く塩ゆでして水気を絞る。ごま油を熱したフライパンで炒める。"
        }
    ],
    "ingredients_not_have": "鶏もも肉・小麦粉・サラダ油・ごま油・ねぎ",
    "reason": "鶏もも肉は家にあったので、材料を買いに行く必要がありませんでした。ほうれん草は栄養が豊富なので、副菜にしました。ごはんは主食にしました。みそ汁は汁物にしまし父が好きなので、みそ汁にしました。"
}
"""

def get_food_receipe(completion_deployment, family_profile, ingredients_have, user_menu_request):
    ingredients_have_text = ", ".join(ingredients_have)

    prompt = prompt_template_1.format(family_profile=family_profile, ingredients_have=ingredients_have_text, user_menu_request=user_menu_request) + prompt_template_2

    completion = openai.Completion.create(
        engine=completion_deployment, 
        prompt=prompt, 
        temperature=0.5, 
        max_tokens=1000, 
        n=1)

    return completion