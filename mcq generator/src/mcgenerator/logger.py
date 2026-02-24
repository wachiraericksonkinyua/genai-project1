import logging
import os
from datetime import datetime
#This line uses datetime.now() to fetch the exact moment the code is executed.
#: The strftime method formats the date and time as Month_Day_Year_Hour_Minute_Second to ensure every execution has a unique filename
LOG_FILE=f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

#creating the path for log directory
#os.getcwd(): This retrieves the current working directory where the project is running
#This combines the working directory with a new folder named "logs" and the previously created filename
logs_path=os.path.join(os.getcwd(),"logs",)
os.makedirs(logs_path,exist_ok=True)#This command physically creates the "logs" folder. The exist_ok=True parameter ensures that if the folder already exists, the code will not crash


LOG_FILE_PATH=os.path.join(logs_path,LOG_FILE)
#This combines the path to the "logs" folder with the unique filename to create a complete absolute path where the file will be saved

#logging.basicConfig: This is the primary method used to configure the logging system
#level=logging.INFO: This sets the logging level to INFO, meaning that all messages at this level and above (WARNING, ERROR, CRITICAL) will be captured
#filename=LOG_FILE_PATH: This specifies the file where the log messages will be stored, using the complete path created earlier
#format='[%(asctime)s] %(levelname)s - %(message)s': This defines the format of the log messages, including a timestamp, the severity level of the log, and the actual log message
logging.basicConfig(level=logging.INFO,
                    filename=LOG_FILE_PATH,
                    format='[%(asctime)s] %(levelname)s - %(message)s',
)