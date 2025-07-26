import os
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain.docstore.document import Document
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# You will need to set your OpenAI API key as an environment variable
# export OPENAI_API_KEY="..."

def generate_summary(transcript):
    """
    Generates a summary of the meeting transcript using LangChain and an LLM.
    """
    if not os.getenv("OPENAI_API_KEY"):
        return "Error: OPENAI_API_KEY not set. Please set it as an environment variable."

    print("Generating meeting summary with LangChain...")
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    
    docs = [Document(page_content=transcript)]
    chain = load_summarize_chain(llm, chain_type="stuff")

    summary = chain.run(docs)
    return summary

def extract_key_takeaways(transcript):
    """
    Extracts key takeaways from the meeting transcript using LangChain.
    """
    if not os.getenv("OPENAI_API_KEY"):
        return "Error: OPENAI_API_KEY not set."

    print("Extracting key takeaways with LangChain...")
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

    prompt_template = """
    You are an AI assistant tasked with identifying key takeaways from a meeting transcript.
    Focus on decisions made, action items assigned, and important conclusions.
    
    Transcript:
    {transcript}
    
    Key Takeaways:
    """
    
    prompt = PromptTemplate(template=prompt_template, input_variables=["transcript"])
    chain = LLMChain(llm=llm, prompt=prompt)
    
    takeaways = chain.run(transcript=transcript)
    return takeaways

def answer_question(transcript, question):
    """
    Answers a question based on the meeting transcript using LangChain.
    """
    if not os.getenv("OPENAI_API_KEY"):
        return "Error: OPENAI_API_KEY not set. Please set it as an environment variable."

    print(f"Answering question with LangChain: {question}")
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    
    docs = [Document(page_content=transcript)]
    chain = load_qa_chain(llm, chain_type="stuff")
    
    answer = chain.run(input_documents=docs, question=question)
    return answer 