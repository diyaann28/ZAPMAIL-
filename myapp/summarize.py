import openai
import os
email_text="Dear John, I hope you're doing well. Our meeting is scheduled for Monday at 10 AM..."
# secret in env variable
apikey = os.getenv("OPENAI_API_KEY");



openai.api_key = apikey

response = openai.ChatCompletion.create(
    model="gpt-4",  # or "gpt-3.5-turbo"
    messages=[
        {"role": "system", "content": "Summarize the following email in 3-4 sentences."},
        {"role": "user", "content": "Your email content goes here..."}
    ]
)
print(response["choices"][0]["message"]["content"])


