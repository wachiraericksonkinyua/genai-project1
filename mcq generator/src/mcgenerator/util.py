import os
import re
import PyPDF2
import json
import traceback
import logging

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception("error reading the pdf file")
    
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    
    else:
        raise Exception(
            "unsupported file format only pdf and text file suppoted"
            )

def get_table_data(quiz_str):
    try:
        # convert the quiz from a str to dict
        if not isinstance(quiz_str, str):
            logging.error(f"quiz_str is not a string, got {type(quiz_str)}")
            return []
        
        cleaned_str = quiz_str.strip()
        
        # Remove markdown code blocks if present
        if cleaned_str.startswith("```"):
            cleaned_str = re.sub(r'^```.*?\n', '', cleaned_str, flags=re.DOTALL)
            cleaned_str = re.sub(r'\n```$', '', cleaned_str)
        
        # Remove any AI assistant markers like <|assistant|>
        cleaned_str = re.sub(r'<\|.*?\|>', '', cleaned_str)
        cleaned_str = cleaned_str.strip()
        
        # Try direct JSON parsing first
        try:
            quiz_dict = json.loads(cleaned_str)
            logging.info("Successfully parsed JSON directly")
        except json.JSONDecodeError as e:
            # If direct parsing fails, extract JSON using non-greedy matching
            # Look for the first { and find its matching }
            start_idx = cleaned_str.find('{')
            if start_idx == -1:
                logging.error(f"No JSON found in quiz_str: {cleaned_str[:300]}")
                return []
            
            # Find matching closing brace
            brace_count = 0
            end_idx = -1
            for i in range(start_idx, len(cleaned_str)):
                if cleaned_str[i] == '{':
                    brace_count += 1
                elif cleaned_str[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break
            
            if end_idx == -1:
                logging.error(f"Could not find matching closing brace in: {cleaned_str[:300]}")
                return []
            
            json_content = cleaned_str[start_idx:end_idx]
            logging.info(f"Extracted JSON: {json_content[:200]}")
            quiz_dict = json.loads(json_content)
        
        # Fix malformed JSON where "correct" is inside "options"
        quiz_dict = fix_malformed_quiz(quiz_dict)
        
        quiz_table_data = []

        # Loop through and extract fields
        for key, value in quiz_dict.items():
            if not isinstance(value, dict):
                logging.warning(f"Skipping invalid entry for key {key}: {value}")
                continue
                
            mcq = value.get("mcq", "N/A")
            # Formatting options for the Streamlit table
            options_dict = value.get("options", {})
            if isinstance(options_dict, dict):
                # Filter out "correct" key if it's in options
                options_dict = {k: v for k, v in options_dict.items() if k != "correct"}
                options = " | ".join([f"{opt}: {val}" for opt, val in options_dict.items()])
            else:
                options = str(options_dict)
            
            correct = value.get("correct", "N/A")
            
            quiz_table_data.append({"MCQ": mcq, "Choices": options, "Correct": correct})
        
        logging.info(f"Successfully parsed {len(quiz_table_data)} questions")
        return quiz_table_data

    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {str(e)}")
        logging.error(f"Quiz string preview: {quiz_str[:500]}")
        return []
    except Exception as e:
        logging.error(f"Error in get_table_data: {str(e)}")
        logging.error(f"Quiz string: {quiz_str[:500] if isinstance(quiz_str, str) else quiz_str}")
        traceback.print_exception(type(e), e, e.__traceback__)
        return []


def fix_malformed_quiz(quiz_dict):
    """Fix malformed JSON where 'correct' key is inside 'options' instead of at question level"""
    try:
        for key, question in quiz_dict.items():
            if isinstance(question, dict) and "options" in question:
                options = question["options"]
                if isinstance(options, dict) and "correct" in options:
                    # Move correct out of options
                    question["correct"] = options.pop("correct")
                    logging.info(f"Fixed malformed question {key}: moved 'correct' out of 'options'")
        return quiz_dict
    except Exception as e:
        logging.error(f"Error fixing malformed quiz: {str(e)}")
        return quiz_dict
