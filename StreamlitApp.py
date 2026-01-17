import os 
import json
import traceback
import pandas as pd

from dotenv import load_dotenv
from src.mcgenerator.mcqgenerator import quiz_chain, review_chain, generate_evaluate_chain
from src.mcgenerator.util import read_file, get_table_data
import streamlit as st
#from langchain.callbacks import get_openai_callback
from langchain_community.callbacks.manager import get_openai_callback
from src.mcgenerator.logger import logging

load_dotenv()  # take environment variables from .env.
#load json file
with open( r'C:\Users\Admin\Desktop\genai project1\response.json') as file:
    RESPONSE_JSON = json.load(file)

st.title("MCQ Generator Application")

#create a form using st.form
with st.form("user_input"):
    #fileupload
    uploaded_file=st.file_uploader("Upload your file here", type=["pdf","txt"])
    #input fields
    mcq_count=st.number_input("No of MCQs",min_value=5, max_value=50)
    #subject
    subject=st.text_input("insert subject",max_chars=20)
    #quiz tone
    tone=st.text_input("insert quiz tone",max_chars=20, placeholder="e.g., easy, medium, hard")
    #add button
    button=st.form_submit_button("Generate MCQs")
    #check if the button is clicked and all fields have input

    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading..."):
            try:
                
                text = read_file(uploaded_file)
                #Count tokens and the cost of api call
                with get_openai_callback() as cb:
                    # Change this line
                    response = generate_evaluate_chain.invoke({
                        "text": text, 
                        "number": mcq_count,
                        "subject": subject, 
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON)
                    })

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("error")
                    
            else:
                print(f"Total Tokens: {cb.total_tokens}")
                print(f"Prompt Tokens: {cb.prompt_tokens}")
                print(f"Completion Tokens: {cb.completion_tokens}")
                print(f"Total Cost (USD): ${cb.total_cost}")
                if isinstance(response, dict):
                    #extract the quiz data from response
                    quiz_data = response.get("quiz", None)
                    if quiz_data is not None:
                        st.write("Debug - Raw AI Output:", quiz_data) 
                        table_data = get_table_data(quiz_data)
                        if table_data:#is not None:
                            df=pd.DataFrame(table_data)
                            df.index=df.index+1
                            st.table(df)
                            #display thr review in a text book as well
                            # Change 'review' to 'reviewed_quiz' to match your chain's output_key
                            st.text_area(label="Review", value=response['reviewed_quiz'])
                        else:
                            st.error("Error in the table data")
                else:
                    st.write (response)

            
