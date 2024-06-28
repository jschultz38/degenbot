from openai import OpenAI

import credentials


def ai_chirp(user):
    client = OpenAI(api_key=credentials.open_ai_key)

    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "You're a drunk, foul mouthed hockey player who is a jerk, talking to someone who thinks they are good but they aren't try to keep all of your chirps unique"},
        {"role": "user", "content": f"Chirp {user}, who is a low skill beer league player, and include the name I give you"}
      ]
    )
    chirp = completion.choices[0].message.content
    print(completion.choices[0].message)
    return chirp
