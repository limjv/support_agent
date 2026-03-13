
"""
original.py

A Python script to classify and summarize a problem using Azure OpenAI.
Configuration is read from environment variables:
    AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, DEPLOYMENT_NAME

Usage:
    python original.py [--file input.txt]
    (If --file is not provided, prompts for input.)
"""


import os
import sys
import argparse
import requests
import json as _json
from typing import Dict, Any

# Read configuration from environment variables
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")

def check_config():
    missing = []
    if not AZURE_OPENAI_ENDPOINT:
        missing.append("AZURE_OPENAI_ENDPOINT")
    if not AZURE_OPENAI_API_KEY:
        missing.append("AZURE_OPENAI_API_KEY")
    if not DEPLOYMENT_NAME:
        missing.append("DEPLOYMENT_NAME")
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")



def classify_and_summarize(problem_text: str) -> Dict[str, Any]:
    """
    Sends the problem text to Azure OpenAI for classification and summarization.
    Returns a dict with 'summary' and 'category'.
    Raises Exception on failure.
    """
    check_config()
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
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"Network or HTTP error: {e}\nRequest data: {data}")
    try:
        result = response.json()
        content = result['choices'][0]['message']['content']
        try:
            return _json.loads(content)
        except Exception:
            return {"summary": content, "category": "Unknown"}
    except Exception as e:
        raise Exception(f"Failed to parse response: {e}\nRaw response: {response.text}")



def main():
    """
    Main entry point. Accepts input from stdin or a file, prints pretty output.
    """
    parser = argparse.ArgumentParser(description="Classify and summarize a support ticket using Azure OpenAI.")
    parser.add_argument('--file', type=str, help='Input file containing the problem text.')
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                problem = f.read()
        except Exception as e:
            print(f"Failed to read file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Enter the problem to classify and summarize (end with Ctrl+D/Ctrl+Z):")
        problem = sys.stdin.read()

    if not problem.strip():
        print("No input provided.", file=sys.stderr)
        sys.exit(1)

    try:
        output = classify_and_summarize(problem)
        print("\nResult:")
        print(_json.dumps(output, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
