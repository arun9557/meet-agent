import os
from openai import OpenAI

# You will need to set your OpenAI API key as an environment variable
# export OPENAI_API_KEY="..."

def generate_summary(transcript):
    """
    Generates a summary of the meeting transcript using OpenAI's API.
    """
    if not os.getenv("OPENAI_API_KEY"):
        return "Error: OPENAI_API_KEY not set. Please set it as an environment variable."

    print("Generating meeting summary...")
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes meeting transcripts."},
            {"role": "user", "content": f"Summarize the following meeting transcript:\n\n{transcript}"}
        ],
        temperature=0
    )

    summary = response.choices[0].message.content
    return summary

def extract_key_takeaways(transcript):
    """
    Extracts key takeaways from the meeting transcript using OpenAI's API.
    """
    if not os.getenv("OPENAI_API_KEY"):
        return "Error: OPENAI_API_KEY not set."

    print("Extracting key takeaways...")
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant tasked with identifying key takeaways from meeting transcripts. Focus on decisions made, action items assigned, and important conclusions."
            },
            {
                "role": "user",
                "content": f"Identify the key takeaways from this meeting transcript:\n\n{transcript}"
            }
        ],
        temperature=0
    )

    takeaways = response.choices[0].message.content
    return takeaways

def answer_question(transcript, question):
    """
    Answers a question based on the meeting transcript using OpenAI's API.
    """
    if not os.getenv("OPENAI_API_KEY"):
        return "Error: OPENAI_API_KEY not set. Please set it as an environment variable."

    print(f"Answering question: {question}")
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions about meeting transcripts."
            },
            {
                "role": "user",
                "content": f"Use the following meeting transcript to answer the question.\n\nTranscript:\n{transcript}\n\nQuestion: {question}"
            }
        ],
        temperature=0
    )
    
    answer = response.choices[0].message.content
    return answer