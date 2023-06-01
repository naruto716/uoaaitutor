import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog
from tkinter import StringVar, BooleanVar
from tkinter import ttk

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import easyocr

from revChatGPT.V1 import Chatbot
import asyncio
import EdgeGPT
import revChatGPT.V3
import Bard

import pyperclip

import threading
import json

from Config import *
CONFIG = {
        "access_token": CHATGPT_TOKEN,
        "paid": PAID,
        "model": DEFAULT_MODEL, 
        }

class ChatAI:
    def __init__(self):
        if CHATGPT_UNOFFICIAL:
            self.chatgpt = Chatbot(config=CONFIG)

        if BING:
            cookies = json.loads(open("cookies.json", encoding="utf-8").read())
            self.bing = EdgeGPT.Chatbot(cookies=cookies)

        if CHATGPT_OFFICIAL:
            self.chatgpt_official = revChatGPT.V3.Chatbot(api_key=API_KEY)

        if GOOGLE_BARD:
            self.bard = Bard.Chatbot(BARD_TOKEN)
            
        self.prev_text = ""

        self.set_model(DEFAULT_MODEL)
        
    def generate_response(self, message, window, reset, copy_to_clipboard = False, temp_model=""):
        window.insert(tk.END, "AI: ")
        response = self.get_response(message, window, reset, copy_to_clipboard, temp_model)
        window.insert('end', '\n' + '-'*50 + '\n', 'separator')  # Add separation line
        self.prev_text = response
        return response

    def get_response(self, message, window, reset, copy_to_clipboard = False, temp_model=""):
        old_model = self.chatbot
        if temp_model:
            self.set_model(temp_model)
        response = ""
        if self.chatbot == self.chatgpt:
            response = self.ask_gpt(message, window, reset)
        elif self.chatbot == self.bing:
            loop = asyncio.new_event_loop()
            response = loop.run_until_complete(self.ask_bing(message, window, reset)) #Dumb lib no sync version
            loop.close()
        elif self.chatbot == self.chatgpt_official:
            response = self.ask_gpt_official(message, window, reset)
        elif self.chatbot == self.bard:
            response = self.ask_bard(message, window, reset)
        if copy_to_clipboard:
            pyperclip.copy(response)
        self.chatbot = old_model
        return response

    def ask_bard(self, message, window, reset):
        response = self.bard.ask(message)["content"]
        window.insert(tk.END, response)
        window.see(tk.END)
        return response

    def ask_gpt_official(self, message, window, reset):
        if reset:
            self.chatgpt_official.reset()
        response = []
        for data in self.chatbot.ask_stream(message):
            window.insert(tk.END, data)
            response.append(data)
            window.see(tk.END)
        return "".join(response)


    def ask_gpt(self, message, window, reset):
        if reset:
            self.chatgpt.reset_chat()
        response = self.chatbot.ask(message) #Get Response
        prev_text = ""
        for data in response:
            message = data["message"][len(prev_text) :]
            prev_text = data["message"]
            window.insert(tk.END, message)
            window.see(tk.END)
        return prev_text

    def set_model(self, model):
        if model == "bing":
            self.chatbot = self.bing

        elif model == "gpt-4 official":
            self.chatbot = self.chatgpt_official
            self.chatgpt_official.engine = "gpt-4"
        elif model == "gpt-3.5-turbo official":
            self.chatbot = self.chatgpt_official
            self.chatgpt_official.engine = "gpt-3.5-turbo"

        elif model == "gpt-4" or model == "gpt-3.5-turbo":
            self.chatbot = self.chatgpt
            self.chatgpt.config['model'] = model

        elif model == "bard":
            self.chatbot = self.bard

    async def ask_bing(self, prompt, window, reset):
        if reset:
            await self.bing.reset()
        prev_text = ""
        async for final, response in self.bing.ask_stream(prompt=prompt, conversation_style=EdgeGPT.ConversationStyle.creative):
            if not final:
                window.insert(tk.END, response[len(prev_text):])
                window.see(tk.END)
                prev_text = response
        return prev_text
        
class OCR:
    def __init__(self):
        self.reader = easyocr.Reader(['en']) # this needs to run only once to load the model into memory
    
    def get_text(self, image_path):
        result = self.reader.readtext(image_path, detail=0)
        return " ".join(result)

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = tk.Toplevel(self.widget, border=1, relief="solid")
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(self.tooltip, text=self.text)
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class ChatClient(ttk.Frame):
    def __init__(self, link, parent=None, **kwargs):
        self.lecture_mode = False
        if link != None:
            self.browser = BrowserInteraction(link)
            self.ocr = OCR()
            self.lecture_mode = True
        self.chatAI = ChatAI()

        ttk.Frame.__init__(self, parent, **kwargs)
        
        self.parent = parent
        self.parent.geometry('1200x600')
        self.parent.minsize(1200, 600)
        self.parent.iconbitmap('icon.ico')
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.columnconfigure(1, weight=2)

        self.mainpanel = tk.Frame(master=self.parent, width=1200, height=600, bg='white')
        self.mainpanel.grid_columnconfigure(0, weight=3)  # Make the main window responsive horizontally
        self.mainpanel.grid_columnconfigure(1, weight=2)  # Make the system prompt responsive horizontally
        self.mainpanel.grid_rowconfigure(1, weight=1)    # Make the main window responsive vertically
        self.mainpanel.grid(row=0, column=1, sticky='nsew')
        
        self.leftpanel = tk.Frame(master=self.parent, width=200, height=600, bg='white')
        self.leftpanel.grid_columnconfigure(0, weight=1)  # Make the left panel responsive horizontally
        self.leftpanel.grid_rowconfigure((0, 2), weight=1)     # Make the left panel responsive vertically
        self.leftpanel.grid_rowconfigure(1, weight=35)     # Make the left panel responsive vertically
        self.leftpanel.grid(row=0, column=0, sticky='nsew')

        self.initialize_user_interface()

    def handle_engine(self, event):
        self.chatAI.set_model(self.gpt_combobox.get())

    def initialize_user_interface(self):
        style = ttk.Style()
        style.configure("White.TEntry", fieldbackground="white")
        style.configure("White.TButton", background="white")
        style.configure("White.TCheckbutton", background="white")
        style.configure("White.TFrame", background="white")
        style.configure("White.TLabel", background="white")
        
        # Create labels for widgets
        ttk.Label(self.mainpanel, text='System Prompt:', background='white', padding=10).grid(column=1, row=0, sticky='w')
        ttk.Label(self.mainpanel, text='Message Input:', background='white', padding=10).grid(column=0, row=2, sticky='ws')

        # Define the system prompt input field
        self.right_panel = ttk.Frame(self.mainpanel, style="White.TFrame")
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(0, weight=5) 
        self.right_panel.grid_rowconfigure(1, weight=3)
        self.right_panel.grid_rowconfigure(1, weight=1)
        
        self.system_prompt = scrolledtext.ScrolledText(self.right_panel, height=15, width=25, font=("Serif", 12), borderwidth=1, relief="solid")
        self.system_prompt.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")
        
        self.user_prompt_label = ttk.Label(self.right_panel, text='AI Prompt:', style="White.TLabel")
        self.user_prompt_label.grid(column=0, row=1, sticky='ws')
        
        self.user_prompt = scrolledtext.ScrolledText(self.right_panel, height=10, width=25, font=("Serif", 12), borderwidth=1, relief="solid")
        self.user_prompt.insert(tk.END, MESSAGE)
        self.user_prompt.grid(column=0, row=2, padx=10, pady=10, sticky="nsew")
        self.right_panel.grid(column=1, row=1, rowspan=5, padx=10, pady=10, sticky="nsew")

        # Define the chat history box
        self.chat_history = scrolledtext.ScrolledText(self.mainpanel, height=15, width=50)
        self.chat_history.grid(column=0, row=1, padx=10, pady=10, sticky="nsew")
        self.chat_history.config(state='disabled', bg='#E8F5E9')  # Initially, this is not editable
        self.chat_history.configure(font=("Arial", 12))  # Change the font to Arial with size 12


        # Define the message input field
        self.message_input = scrolledtext.ScrolledText(self.mainpanel, height=8, width=50)
        self.message_input.grid(column=0, row=3, padx=10, pady=10, sticky="ew")
        self.message_input.config(bg='#FFF9C4')

        # Define the timestamp input field
        self.timestamp_frame = tk.Frame(self.mainpanel, background="white")
        self.timestamp_frame.columnconfigure([0, 1, 2, 3], weight=1)
        self.timestamp_frame.columnconfigure(4, weight=2)
        
        ttk.Label(self.timestamp_frame, text='Timestamp:', background='white', padding=10).grid(column=0, row=0, sticky='e')
        self.timestamp = ttk.Entry(self.timestamp_frame, width=20, style="White.TEntry")
        self.timestamp.grid(column=1, row=0, padx=10, pady=5, sticky="we")
        # Adding a text entry field for 'time span' inside the frame
        ttk.Label(self.timestamp_frame, text='Time Span:', background='white', padding=10).grid(column=2, row=0, sticky='e')
        self.time_span = ttk.Entry(self.timestamp_frame, width=20, style="White.TEntry")
        self.time_span.insert(0, '180')
        self.time_span.grid(column=3, row=0, padx=10, pady=5, sticky="we")
        
        # Define the send message button
        self.send_button = ttk.Button(self.timestamp_frame, text="Send", command=lambda: threading.Thread(target=self.send_message).start(), style="White.TButton")
        self.send_button.grid(column=4, row=0, padx=10, pady=10, sticky="we")

        self.timestamp_frame.grid(column=0, row=5, padx=10, pady=10, sticky="w")

        # Create a frame for the new widgets
        self.extra_options_frame = tk.Frame(self.mainpanel, background="white")
        self.extra_options_frame.grid_columnconfigure((0,1,2), weight=1)
        ttk.Label(self.extra_options_frame, text='Chat History:', background='white', padding=10).grid(column=0, row=0, sticky='w')
        ttk.Label(self.extra_options_frame, text='Engine:', background='white', padding=10).grid(column=1, row=0, sticky='e')
        # Adding a combobox for choosing GPT model inside the frame
        self.gpt_model = StringVar()
        self.gpt_combobox = ttk.Combobox(self.extra_options_frame, textvariable=self.gpt_model, state="readonly")
        self.gpt_combobox['values'] = ('gpt-4', 'gpt-3.5-turbo', 'bing', 'gpt-4 official', 'gpt-3.5-turbo official', 'bard')
        self.gpt_combobox.set(DEFAULT_MODEL)
        self.gpt_combobox.grid(column=2, row=0, padx=10, pady=5, sticky="we")
        self.gpt_combobox.bind("<<ComboboxSelected>>", self.handle_engine)  # Bind the event handler method

        # Adding a checkbox for OCR inside the frame
        self.ocr_value = BooleanVar()
        self.ocr_checkbox = ttk.Checkbutton(self.extra_options_frame, text='OCR', variable=self.ocr_value, style="White.TCheckbutton")
        self.ocr_checkbox.grid(column=3, row=0, padx=10, pady=5, sticky="we")

        # Adding a checkbox for reset inside the frame
        self.reset_chat = BooleanVar(value=False)
        self.reset_chat_box = ttk.Checkbutton(self.extra_options_frame, text='Reset', variable=self.reset_chat, style="White.TCheckbutton")
        Tooltip(self.reset_chat_box, "Reset the chatbot's memory each time you hit send without a message\nThis may be required for bing to work properly as it might terminate conversations occasionally")
        self.reset_chat_box.grid(column=4, row=0, padx=10, pady=5, sticky="we")

        # Adding a checkbox for copy inside the frame
        self.copy_response = BooleanVar(value=True)
        self.copy_response_box = ttk.Checkbutton(self.extra_options_frame, text='Copy', variable=self.copy_response, style="White.TCheckbutton")
        Tooltip(self.copy_response_box, "Copy the response to clipboard after each message for fast note-taking.\nYou can paste it to Notion or alike tools for better readability")
        self.copy_response_box.grid(column=5, row=0, padx=10, pady=5, sticky="we")

        self.extra_options_frame.grid(column=0, row=0, padx=10, pady=10, columnspan=1, sticky="nsew")
        
        #Left Panel
        separator = ttk.Separator(self.leftpanel, orient='vertical')
        separator.grid(column=1, row=0, rowspan=3, sticky='ens', padx=12, pady=22)
        
        # Define the summarization label
        self.summarization_label = ttk.Label(self.leftpanel, text='Summary:', style="White.TLabel")
        self.summarization_label.grid(column=0, row=0, padx=10, pady=10, sticky="nw")        

        # Define a panel for the summarization and options
        self.summarization_panel = tk.Frame(self.leftpanel, background="white")
        self.summarization_panel.grid_columnconfigure((0,1,2,3), weight=1)
        self.summarization_panel.grid(column=0, row=2, padx=10, pady=10, sticky="wes")
        
        # Define the summarization engine label
        self.summarization_engine_label = ttk.Label(self.summarization_panel, text='Engine:', background='white')
        self.summarization_engine_label.grid(column=1, row=1, sticky='e')
        
        #define the summarization engine combobox
        self.summarization_value = StringVar()
        self.summarization_box = ttk.Combobox(self.summarization_panel, textvariable=self.summarization_value, state="readonly")
        self.summarization_box["values"] = ('gpt-4', 'gpt-3.5-turbo', 'bing', 'gpt-4 official', 'gpt-3.5-turbo official', 'bard')
        self.summarization_box.set("gpt-3.5-turbo")
        self.summarization_box.grid(column=2, row=1, padx=10, pady=5, sticky="we")
        
        #define the always summarize checkbox
        self.summarize_checkbox_value = BooleanVar(value=True)
        self.summarize_checkbox = ttk.Checkbutton(self.summarization_panel, text='Always', variable=self.summarize_checkbox_value, style="White.TCheckbutton")
        self.summarize_checkbox.grid(column=3, row=1, padx=10, pady=5, sticky="we")
        
        #define the summarization button
        self.summarization_button = ttk.Button(self.summarization_panel, text='Summarize', command=lambda: threading.Thread(target=self.summarize).start(), style="White.TButton")
        self.summarization_button.grid(column=0, columnspan=4, row=0, padx=10, pady=5, sticky="we")
        
        #define the summarization text box
        self.summarization_textbox = tk.Text(self.leftpanel, height=10, width=50, wrap='word', borderwidth=1, relief='solid', padx=5, pady=5, font=("Helvetica", 10))
        self.summarization_textbox.grid(column=0, row=1, padx=10, pady=5, sticky="nswe")
        
    def summarize(self):
        self.summarization_button.config(state = "disabled")
        self.summarization_textbox.config(state = "normal")
        message = self.chatAI.prev_text
        if message == "":
            self.summarization_textbox.delete('1.0', 'end')
            self.summarization_textbox.insert('1.0', message)
        else:
            self.summarization_textbox.delete('1.0', 'end')
            self.chatAI.get_response(message + "\n" + SUMMARY_MESSAGE, self.summarization_textbox, self.copy_response.get(), self.reset_chat.get(), self.summarization_box.get())
        self.summarization_button.config(state = "enabled")
        return
    
    def retrieve_timestamp(self):
        timestamp = self.browser.retrieve_current_timestamp_from_div()
        self.timestamp.delete(0, 'end')
        self.timestamp.insert(0, timestamp)
        return timestamp

    def get_ocr_prompt(self):
        self.browser.screenshot()
        image_path = "screenshot.png"
        return self.ocr.get_text(image_path)
    
    def timestamp_to_int(self, timestamp):
        if ':' in timestamp:
            mm, ss = timestamp.split(':')
            return int(mm) * 60 + int(ss)
        else:
            return 0 #for cases without a timestamp, which usually occurs at the beginning of the video

    def get_relevant_transcription_from_timestamp(self, timestamp, timespanValue):
        text_list = []
        int_timestamp = self.timestamp_to_int(timestamp)
        for time, text in self.browser.timestamp_data.items():
            int_time = self.timestamp_to_int(time)
            if abs(int_timestamp - int_time) < timespanValue and text != None:
                text_list.append(f"{text} [{time}]\n")
        return " ".join(text_list)

    def construct_prompt(self):
        prompt = ""
        if self.ocr_value.get():
            self.system_prompt.insert('end', "Running OCR...\n")
            self.system_prompt.see(tk.END)
            prompt += "[OCR]\n" + self.get_ocr_prompt()
        prompt += "\n" + "[TRANSCRIPTION]\n" + self.get_relevant_transcription_from_timestamp(self.retrieve_timestamp(), int(self.time_span.get())) + "\n" + self.user_prompt.get("1.0", tk.END) + "\nCurrent timestamp: " + self.retrieve_timestamp() + "\n"
        prompt = self.replace_text(prompt)
        self.system_prompt.insert('end', prompt)
        self.system_prompt.see(tk.END)
        return prompt

    def summary_query(self, text):
        response = ""
        for data in self.chatAI.chatgpt.ask(text):
            response = data["message"]
        return response

    def replace_text(self, text):
        if CURRENT_CONTENT in text:
            prompt = self.get_relevant_transcription_from_timestamp(self.retrieve_timestamp(), TIME_SPAN_CURRENT_CONTENT) + "\n" + CURRENT_CONTENT_PROMPT
            print("Replace text inquiry: " + prompt)
            prompt = self.summary_query(prompt)
            print("Replaced", prompt)
            text = text.replace(CURRENT_CONTENT, prompt)
        return text

    def send_message(self):
        self.send_button.config(state="disabled")
        self.chat_history.config(state='normal')  # Make it editable
        success = True
      # Get the current message
        try:
            message = self.message_input.get("1.0", 'end-1c')
            if self.lecture_mode: #Lecture Mode
                if message:  #if message is not empty
                    if message.startswith("/reload"):
                        self.message_input.delete("1.0", 'end')  # Clear the input field
                        self.system_prompt.insert('end', "Reloading transcription...\n")
                        self.browser.load_transcription()
                        self.system_prompt.insert('end', "Reloaded!\n")
                    else:
                        self.message_input.delete("1.0", 'end')  # Clear the input field

                        # Add the message to the chat history
                        self.chat_history.insert('end', "You: " + message + '\n')
                        self.chat_history.tag_config('separator', foreground='grey')

                        #Send message
                        self.chatAI.generate_response(message, self.chat_history, False, self.copy_response.get())

                else:
                    self.chatAI.generate_response(self.construct_prompt(), self.chat_history, self.reset_chat.get(), self.copy_response.get())
            else:#Chat Mode
                if message:
                    self.message_input.delete("1.0", 'end')  # Clear the input field
                    # Add the message to the chat history
                    self.chat_history.insert('end', "You: " + message + '\n')
                    self.chat_history.tag_config('separator', foreground='grey')

                    #Send message
                    self.chatAI.generate_response(message, self.chat_history, self.reset_chat.get(), self.copy_response.get())

                else:
                    success = False
                    self.system_prompt.insert('end', "Please enter a message\n")  
        except Exception as e:
            self.chat_history.insert('end', f"Error: {repr(e)} \nYou might want to try other models for now, and make sure you update all dependencies of this program. The official models are stable yet cost you money.\n")
            self.system_prompt.insert('end', f"Error: {repr(e)}\n")
        
        self.chat_history.config(state='disabled')
        self.send_button.config(state="normal")
        if success and self.summarize_checkbox_value.get():
            self.summarize()
            
class attribute_to_be(object):
    def __init__(self, locator, attribute, value):
        self.locator = locator
        self.attribute = attribute
        self.value = value

    def __call__(self, driver):
        element = driver.find_element(*self.locator)   # Finding the referenced element
        if element.get_attribute(self.attribute) == self.value:
            return element
        else:
            return False

class BrowserInteraction:
    def __init__(self, link):
        # Create a new instance of the Edge driver
        self.driver = webdriver.Edge()
        self.timestamp_data = {}  # Dictionary to store timestamp data
        self.get_transcription(link)

    def get_transcription(self, link):
        # Load the webpage
        self.driver.get(link)# Replace with the URL of the webpage
        self.load_transcription()

    def load_transcription(self):
        # Wait for "aria-selected" attribute of the element with id "transcriptTabHeader" to be "true"
        print("Waiting for the Caption tab to be selected...")
        wait = WebDriverWait(self.driver, 120)  # Maximum wait time of 120 seconds
        caption_selected = attribute_to_be((By.ID, 'transcriptTabHeader'), 'aria-selected', 'true')
        wait.until(caption_selected)

        # Wait until the elements with class "index-event-row" are present
        wait = WebDriverWait(self.driver, 120)  # Maximum wait time of 120 seconds
        elements_present = EC.presence_of_all_elements_located((By.CLASS_NAME, 'index-event-row'))
        wait.until(elements_present)

        # Find all the elements with class "index-event-row"
        elements = self.driver.find_elements(By.CLASS_NAME, 'index-event-row')

        self.timestamp_data.clear()
        print("Getting Transcription")
        # Iterate over the elements
        for element in elements:
            try:
                # Extract the text
                event_text_element = element.find_element(By.CLASS_NAME, 'event-text')
                # Extract the timestamp
                event_time_element = element.find_element(By.CLASS_NAME, 'event-time')
                if event_text_element.text and event_time_element.text:
                    text = event_text_element.text
                    timestamp = event_time_element.text
                    print(text, timestamp)
                    # Store the text and timestamp in the dictionary
                    self.timestamp_data[timestamp] = text
            except Exception as e:
                print(f"An error occurred: {e}")

    def retrieve_current_timestamp_from_div(self):
        try:
            # Find the element with id "timeElapsed"
            timestamp_element = self.driver.find_element(By.ID, 'timeElapsed')
            # Extract the timestamp from the element
            timestamp = timestamp_element.text

            # Store the timestamp in the dictionary
            self.timestamp_data[timestamp] = None

            return timestamp
        except Exception as e:
            print(f"Error occurred while retrieving timestamp: {e}")
            return None

    def screenshot(self, filename = "screenshot.png"):
        # find the video element
        video_element = self.driver.find_element(By.ID, 'primaryVideo')
        image = video_element.screenshot_as_png
        with open(filename, 'wb') as file:
            file.write(image)
        

    def close_browser(self):
        # Close the browser
        self.driver.quit()

def main():
    link = simpledialog.askstring("Input", "Please enter the link to the lecture recording (Select cancel for chatting):")
    root = tk.Tk()
    root.title("Cope Hard I Cry")
    ChatClient(link, root)
    root.mainloop()

if __name__ == "__main__":
    main()
