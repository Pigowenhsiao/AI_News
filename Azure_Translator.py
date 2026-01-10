import requests, uuid, json

def translate_with_microsoft(text, target_lang='zh-Hant'):
    subscription_key = "2956e36e0b52409aa611f3be4da82a92"
    endpoint = "https://api.cognitive.microsofttranslator.com"
    location = "eastus"

    path = '/translate'
    constructed_url = endpoint + path

    params = {
        'api-version': '3.0',
        'to': [target_lang]
    }
    constructed_url = endpoint + path

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{
        'text': text
    }]

    response = requests.post(constructed_url, params=params, headers=headers, json=body)
    result = response.json()

    return result[0]['translations'][0]['text']
