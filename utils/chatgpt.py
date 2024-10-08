from openai import OpenAI
import random
import tiktoken
import credentials

#Initialize OpenAI Client
client = OpenAI(api_key=credentials.open_ai_key)


def ai_chirp(user, teams):
    client = OpenAI(api_key=credentials.open_ai_key)
    player_teams = []
    for team in teams:
        if user in team['players']:
            player_teams.append(team['name'])

    chirp = build_chirp(client, user, player_teams)

    print(chirp.choices[0].message)
    return chirp.choices[0].message.content

def summarize(messages):
    chunks = chunk_conversation(messages)
    summaries= []

    for chunk in chunks:
        conversation = "\n".join(chunk)
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a helpful AI assistant, helping people catch up on what they missed in a social chat"},
                {"role": "user",
                 "content": f"Summarize what we missed in this conversation: {conversation}"}
            ]
        )
        summaries.append(completion.choices[0].message.content)

    return "\n".join(summaries)  # Combine all summaries into a single response

def build_chirp(user, player_teams):
    if not player_teams:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You're a drunk, foul mouthed hockey player who is a jerk, talking to someone who thinks they are good but they aren't try to keep all of your chirps unique"},
                {"role": "user",
                 "content": f"Chirp {user}, you don't necessarily have to talk about hockey, you can insult them on their hygiene, looks, intelligence, or general skills too. Do not be racist, sexist, or make jokes about suicide. Try to use their name in the chirp as well."}
            ]
        )
    else:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You're a drunk, foul mouthed hockey player who is a jerk, talking to someone who thinks they are good but they aren't try to keep all of your chirps unique"},
                {"role": "user",
                 "content": f"Chirp {user}, who is a low skill rec league hockey player playing for {random.choice(player_teams)},"
                 f" include the name I give you in the chirp. Also try to remain topical using the players team if possible to insult them. "
                 f"You can talk about how they are the reason their team is bad, or loses games, or how they do great without them around"
                 f"Don't be too mean and encourage people to quit though."}
            ]
        )

    return completion

# dealing with the token limit for chatgpt
def count_tokens(text):
    """Count the number of tokens in a given text."""
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoding.encode(text))

# when messages reach the token limit, break it up into multiple requests
def chunk_conversation(messages, max_tokens=3500):
    """Breaks messages into chunks that fit within the token limit."""
    chunks = []
    current_chunk = []
    current_length = 0

    for message in messages:
        message_tokens = count_tokens(message)

        # Check if adding this message exceeds the limit
        if current_length + message_tokens <= max_tokens:
            current_chunk.append(message)
            current_length += message_tokens
        else:
            # If it does, save the current chunk and start a new one
            chunks.append(current_chunk)
            current_chunk = [message]
            current_length = message_tokens

    # Don't forget to add the last chunk if it has content
    if current_chunk:
        chunks.append(current_chunk)
    return chunks
