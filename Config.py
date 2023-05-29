#Set the engines you want to use to True
#Go to the Github Page for more information

#MESSAGE = "This guy is talking about: \n{CurrentContent}\n explain it to me in details using bullet points. Use your own knowledge when necessary\n"
MESSAGE = "Find what this guy is talking about at the current timestamp and explain it to me using bullet points."
SUMMARY_MESSAGE = "Summarize this using bullet points"
DEFAULT_MODEL = "bing" #default model, make sure you enable the default model below
#Unofficial ChatGPT, you can use it for free
CHATGPT_UNOFFICIAL = True
PAID = True #True if you have chatgpt plus, false otherwise
CHATGPT_TOKEN = "<Your Chat GPT Token>"
#Official ChatGPT, you need to pay for it
CHATGPT_OFFICIAL = True
API_KEY = "<Your OpenAI API token>"
#Google Bard
GOOGLE_BARD = True
BARD_TOKEN = "<Your Google Bard Token>"
#Microsoft Bing
BING = True
#Make sure you put cookies.json in the same folder as this file for bing to work

CURRENT_CONTENT = "{CurrentContent}" #Use gpt-3.5-turbo to replace this with the current content, make sure you turn gpt3.5 on
TIME_SPAN_CURRENT_CONTENT = 60 #Time span for the current content in seconds
CURRENT_CONTENT_PROMPT = "Find the topic of the transcription. No more than 100 words."
