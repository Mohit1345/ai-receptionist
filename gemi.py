import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


import json
from google.generativeai.types import HarmCategory, HarmBlockThreshold

def llm(query,generation_json,system_prompt):
    if len(generation_json)!=0:
        generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    properties = {
      "response": content.Schema(
        type = content.Type.STRING,enum=generation_json
      ),
    },
  ),
  "response_mime_type": "application/json",
    }
    else:
        generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    properties = {
      "response": content.Schema(
        type = content.Type.STRING
      ),
    },
  ),
  "response_mime_type": "application/json",
    }
    model = genai.GenerativeModel(
    model_name=os.environ['GEMINI_MODEL'],
    generation_config=generation_config,
    system_instruction=f"Act as an AI receptionist and chat with consumer, {system_prompt}",
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
    }
    )

    chat_session = model.start_chat(
    history=[]
    )

    response = chat_session.send_message(query)
    return json.loads(response.text)

import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

def rag_search(emergency_ask):
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    document_1 = Document(
        page_content="""I understand that you are worried that Dr. Adrin will arrive too late,
meanwhile we would suggest that you start CPR, i.e. pushing against the chest of the
patient and blowing air into his mouth in a constant rhythm.""",
    )
    document_2 = Document(
        page_content="""If the patient is not breathing then do CPR i.e. pushing against the chest of the
patient and blowing air into his mouth in a constant rhythm.""",
    )

    documents = [
    document_1,document_2
]
    vector = FAISS.from_documents(documents, embeddings)
    retriever = vector.as_retriever(search_type="mmr",search_kwargs={'k': 1})

    results = retriever.invoke(emergency_ask)
    if len(results)>0:
        final_result = llm(f"""check if the solution is related to query or not
                          #query# : {emergency_ask}
                          #Solution# : {results[0].page_content} 
                          if solution address query then return it as it is , else return blank []""",[],"")
        # print(final_result)
        if final_result['response'] == '[]':
            return []
        return final_result['response']
    return []

# print(type(rag_search("too much fever")))

    