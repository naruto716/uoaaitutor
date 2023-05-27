# UOA COMPSCI230 Cope Hard I Cry
Leveraging cutting-edge technology, this tool is your personal companion for deciphering the most unnecessarily confusing lectures, those that have stumped others before. 
![image](https://github.com/naruto716/uoaaitutor/assets/79365555/454e0248-9caa-450e-972a-a494bda17753)

# Description:
As none of my friends found the the lectures understandable due to the way some concepts are explained (I am struggling a lot with understanding some very simple ideas from the lectures as well), I tried several approaches and found AIs very helpful with the comprehension of badly explained ideas. You might also want to use it for other unnecessarily confusing papers.

# Features:
1. Empowered by the latest AI technology, this tool reads the relevant transcription of the lecture recording being currently played and uses an OCR to extract visual information from it, which would then be combined into a prompt and sent to LLMs (Large Language Models) asking for better explanation. 

2. Allow you to ask AI questions in the context of the current lecture.

3. You are able to switch between several language models including GPT-4/ChatGPT(GPT3.5)/Microsoft Bing/Google Bard.

4. For ChatGPT, you can choose to use the official API (paid) and an unofficial API (free but not as stable). According to my test, Microsoft Bing is overall the best option as it internally uses GPT-4 and the usage is almost unlimited, albeit being continously nerfed by Microsoft. GPT3.5 and Bard are not very good. GPT-4 is impressive but the usage might be limited unelss you are a rich boi.

# Installation Instructions

This guide is intended for users running the Windows operating system. For Mac users, I personally never used MacOS and can't really help you with using it.

## Dependencies

Install Python Libs:

1. First, ensure Python and pip (Python's package installer) are installed on your system. You can download Python, which comes with pip, from the official website: https://www.python.org/downloads/.

2. Download the `requirements.txt` file from this repository.

3. Open the Command Prompt. You can do this by searching for `cmd` in the Start menu.

4. Navigate to the directory containing the `requirements.txt` file using the `cd` command. For example, if the file is in your Downloads folder, you would type:

```
cd Downloads
pip install -r requirements.txt
```

# Edge WebDriver (Every modern window computer comes with this browser, so you probably already have it installed)
This tool uses the Edge browser for its operations. Therefore, it is necessary to install the corresponding WebDriver, EdgeDriver. Here are the installation steps:

Visit the following link to download the latest EdgeDriver: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/

Once the download is complete, open the location of the downloaded file.

Extract the contents of the downloaded file.

We recommend creating a dedicated directory for your WebDriver, such as C:\WebDriver. Move the extracted msedgedriver.exe file to this directory.

Next, you need to add the WebDriver's location to your System's PATH:

Open the Start menu, search for 'Environment Variables', and select 'Edit the system environment variables'.

In the System Properties window that appears, click on the 'Environment Variables' button.

In the Environment Variables window, under 'System variables', find and select the 'Path' variable, then click on 'Edit'.

In the Edit Environment Variable window, click on 'New', then type in the path to your WebDriver directory, for example, C:\WebDriver.

Click 'OK' in all windows to save your changes.

To verify that the installation was successful, open a new Command Prompt window and type:
```
msedgedriver --version
```
If the installation was successful, you should see the version information for EdgeDriver.

Please ensure the EdgeDriver version matches the version of the Edge browser installed on your system.

# AI Configuration
Bing:
1. Open bing.com/chat
2. If you see a chat feature, you are good to continue...
3. Install the cookie editor extension for your browser (You can google this). Bing is the best engine for this tool overall.
4. Go to bing.com
5. Open the extension
6. Click "Export" on the bottom right, then "Export as JSON" (This saves your cookies to clipboard)
7. Paste your cookies into a file cookies.json and put it under the same folder as the python file

Google Bard:
1. Go to https://bard.google.com/
2. F12 for console
3. Go to Application → Cookies → __Secure-1PSID. Copy the value of that cookie and put it in Config.py

ChatGPT Unofficial:
1. Create account on OpenAI's ChatGPT
2. Save your email and password
3. Copy your access token https://chat.openai.com/api/auth/session from this page.
4. Change CHATGPT_TOKEN to your token in Config.py
5. Make sure you set PAID to false if you don't have chatgpt plus

ChatGPT Official:
1. https://platform.openai.com/account/api-keys Go to OpenAI's website to get your API token, you might need to set up a billing profile to get it.
2. Put it in API_KEY in Config.py

# Use
1. Run the tool in python, everything is put in one file to avoid unnecessary confusion for some people.
2. If you successfully installed the dependencies, you will see a browser popping up. Log in to your SCHOOL account and navigate to the lecture you want to watch.
3. HIT THE CAPTION BUTTON on the left of the webpage as shown below:
4. ![image](https://github.com/naruto716/uoaaitutor/assets/79365555/ac5735e2-0669-4b00-a2da-826bff9aa37c)
5. Wait a few seconds, if everything's going well, you will see a GUI
6. Now watch the lecture recordings as usual, when in doubt, CLICK ON THE SEND BUTTON WITHOUT TYPING IN ANYTHING IN THE MESSAGE BOX, the tool will send the relevant context to AI and by default the AI will extract and explain the key points for you. You can ask it anything you are confused about regarding the lecture content.
7. Do step 6 again for another topic/slide in the lecture
8. If you want to use OCR, make sure you tick the OCR checkbox:
![image](https://github.com/naruto716/uoaaitutor/assets/79365555/32f7d6fb-6858-4f52-87be-1a277fc1da35)
If you encounter any issues, feel free to open an issue on this GitHub repository, and we will do our best to assist you. Enjoy using the tool!
