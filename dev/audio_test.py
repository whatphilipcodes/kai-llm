import base64
from openai import OpenAI

# 1. Read and encode the local audio file into Base64
file_path = "resources/source-philip.wav"
with open(file_path, "rb") as audio_file:
    encoded_string = base64.b64encode(audio_file.read()).decode("utf-8")

# Format as a Data URI
audio_data_uri = f"data:audio/wav;base64,{encoded_string}"

client = OpenAI(base_url="http://localhost:30000/v1", api_key="EMPTY")

response = client.chat.completions.create(
    model="google/gemma-4-E4B-it",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "audio_url",
                    "audio_url": {"url": audio_data_uri},
                },
                {
                    "type": "text",
                    "text": "Provide a verbatim, word-for-word transcription of the audio in the spoken language.",
                },
            ],
        }
    ],
    max_tokens=512,
)

print(response.choices[0].message.content)
