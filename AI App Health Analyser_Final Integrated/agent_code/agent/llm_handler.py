from langchain_google_genai import ChatGoogleGenerativeAI


import os
os.environ["GOOGLE_API_KEY"] = "api key here"

def llm_json():
  llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
  return llm


