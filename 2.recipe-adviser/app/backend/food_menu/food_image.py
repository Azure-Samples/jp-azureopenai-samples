import requests
import time
import openai

prompt_template = """
以下を英訳してください。
{food_name} のテーブルの皿に盛られた美味しそうな写真。料理ごとに別々の皿で。
"""

def get_food_image(api_service, api_key, api_version, completion_deployment, food_name):
    # url = "https://{api_service}.openai.azure.com/dalle/text-to-image?api-version={api_version}".format(api_service=api_service, api_version=api_version)
    url = f"https://{api_service}.openai.azure.com/openai/images/generations:submit?api-version={api_version}"

    prompt_translate = prompt_template.format(food_name=food_name)
    completion = openai.Completion.create(
        engine=completion_deployment, 
        prompt=prompt_translate, 
        temperature=0, 
        max_tokens=100,
        n=1)
    prompt = completion.choices[0]['text']

    headers= {
        "api-key": api_key, 
        "Content-Type": "application/json" 
    }
    body = {
        "prompt": prompt,
        "resolution": "256x256"
    }
    submission = requests.post(url, headers=headers, json=body)

    print(submission.json(), flush=True)

    operation_location = submission.headers['Operation-Location']

    # retry_after = submission.headers['Retry-after']

    status = ""
    while (status != "succeeded"):
        # TODO retry afterがレスポンスから無いため、仮で0.5sごとにアクセス
        time.sleep(0.5)
        response = requests.get(operation_location, headers=headers)
        status = response.json()['status']

    image_url = response.json()['result']['data'][0]['url']

    return image_url
