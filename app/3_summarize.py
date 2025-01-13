from sympy import true
from openai import OpenAI
import os

def get_gpt4_response(prompt, api_key, model="gpt-4o"):
    """
    Uses OpenAI's GPT-4 API to generate a response to a custom prompt.

    Args:
        prompt (str): The custom prompt to send to GPT-4.
        api_key (str): Your OpenAI API key.
        model (str): The model to use (default is 'gpt-4').

    Returns:
        str: The generated response text.
    """
    # Set the API key for OpenAI
    client = OpenAI(api_key=api_key)

    try:
        # Call the OpenAI API
        completion = client.chat.completions.create(
            model="gpt-4o",
            store=True,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]
        )

        # Extract the generated text from the response
        return completion.choices[0].message.content

    except Exception as e:
        return f"An error occurred: {e}"

# Example usage:

if __name__ == "__main__":
    with open("openAI_apiKey.txt", "r") as file:
        api_key = file.read().strip()
    prompt = "What are the benefits of regular exercise?"
    response = get_gpt4_response(prompt, api_key)
    print(response)
