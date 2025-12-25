from openai import OpenAI

openai_client = OpenAI()


def llm(prompt, model='gpt-4o-mini'):
    messages = [
        {"role": "user", "content": prompt}
    ]

    response = openai_client.responses.create(
        model='gpt-4o-mini',
        input=messages
    )

    return response.output_text