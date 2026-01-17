import os
from langchain_huggingface import HuggingFaceEndpoint
from langchain_huggingface import ChatHuggingFace
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.callbacks import get_openai_callback # Works for tracking some HF usage too
import json
import pandas as pd
import traceback
from langchain_huggingface import ChatHuggingFace
from langchain.chains import LLMChain

#importing necessary packages from langchain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import SequentialChain
#Importing the dotenv package to manage environment variables
from dotenv import load_dotenv
from regex import TEMPLATE
load_dotenv()  # take environment variables from .env.

key=os.getenv("HUGGINGFACEHUB_API_TOKEN")

llm = HuggingFaceEndpoint(
                        huggingfacehub_api_token=key,
                        repo_id="HuggingFaceH4/zephyr-7b-beta",
                        temperature=0.3,
                        max_new_tokens=512,
                        timeout=600,           # Prevents ReadTimeout errors
                        stop_sequences=["\n\n"]
                          )

chat_model = ChatHuggingFace(llm=llm)

template="""
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz  of {number} multiple choice questions for {subject} students in {tone} tone. 
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like  RESPONSE_JSON below  and use it as a guide. \
Ensure to make {number} MCQs
### RESPONSE_JSON
{response_json}

"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template=template
    )
quiz_chain=LLMChain(llm=chat_model, prompt=quiz_generation_prompt, output_key="quiz", verbose=True)


template2="""
You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity analysis. 
if the quiz is not at per with the cognitive and analytical abilities of the students,\
update the quiz questions which needs to be changed and change the tone such that it perfectly fits the student abilities
Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""
quiz_evaluation_prompt = PromptTemplate(
    input_variables=["quiz", "subject"],
    template=template2
    )
review_chain=LLMChain(llm=chat_model, prompt=quiz_evaluation_prompt, output_key="reviewed_quiz", verbose=True)

#generate_quiz_chain 
generate_evaluate_chain = SequentialChain(
    chains=[quiz_chain, review_chain], input_variables=["text", "number", "subject", "tone", "response_json"],
    output_variables=["quiz", "reviewed_quiz"], verbose=True,)

# Rename these at the end of mcqgenerator.py
generate_quiz_chain = quiz_chain