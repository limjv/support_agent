"""
original.py

A Python script to classify and summarize a problem using Azure OpenAI. 
Fill in your Azure OpenAI endpoint and API key in the placeholders below.
"""

import os
import requests

# Placeholders for Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT = "<YOUR_AZURE_OPENAI_ENDPOINT>"
AZURE_OPENAI_API_KEY = "<YOUR_AZURE_OPENAI_API_KEY>"
DEPLOYMENT_NAME = "<YOUR_DEPLOYMENT_NAME>"  # e.g., 'gpt-35-turbo'


def classify_and_summarize(problem_text):
    """
    Sends the problem text to Azure OpenAI for classification and summarization.
    """
    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version=2023-03-15-preview"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_API_KEY
    }
    data = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that classifies and summarizes problems. Respond in JSON with 'summary' and 'category' fields."},
            {"role": "user", "content": problem_text}
        ],
        "max_tokens": 256,
        "temperature": 0.3
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        import json as _json
        content = result['choices'][0]['message']['content']
        try:
            return _json.loads(content)
        except Exception:
            return {"summary": content, "category": "Unknown"}
    else:
        raise Exception(f"Request failed: {response.status_code} {response.text}")


if __name__ == "__main__":
    sample_ticket = """
    Hi, I updated the app yesterday and now it crashes every time I try to open it.
    Please fix this as soon as possible.
    """
    # You can use sample_ticket as the input, or uncomment the next line to use manual input
    # problem = input("Enter the problem to classify and summarize: ")
    # Use sample_ticket as the input
    try:
        output = classify_and_summarize(sample_ticket)
        if output:
            print("Summary:", output.get("summary", output))
            print("Category:", output.get("category", "Unknown"))
    except Exception as e:
        print("Error:", e)
