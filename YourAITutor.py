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

        self.set_model(DEFAULT_MODEL)
        
    def generate_response(self, message, window, reset, copy_to_clipboard = False):
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

        return response

    def ask_bard(self, message, window, reset):
        window.config(state='normal')  # Make it editable
        window.insert(tk.END, "AI (Bard):\n")
        window.see(tk.END)
        response = self.bard.ask(message)["content"]
        window.insert(tk.END, response)
        window.insert('end', '\n' + '-'*50 + '\n', 'separator')  # Add separation line
        window.see(tk.END)
        window.config(state='disabled')  # Make it read only
        return response

    def ask_gpt_official(self, message, window, reset):
        if reset:
            self.chatgpt_official.reset()
        response = []
        window.config(state='normal')  # Make it editable
        window.insert(tk.END, "AI:\n")
        for data in self.chatbot.ask_stream(message):
            window.insert(tk.END, data)
            response.append(data)
            window.see(tk.END)
        window.insert('end', '\n' + '-'*50 + '\n', 'separator')  # Add separation line
        window.config(state='disabled')  # Make it read only
        return "".join(response)


    def ask_gpt(self, message, window, reset):
        if reset:
            self.chatgpt.reset_chat()
        response = self.chatbot.ask(message) #Get Response
        window.config(state='normal')  # Make it editable
        prev_text = ""
        window.insert(tk.END, "AI:\n")
        for data in response:
            message = data["message"][len(prev_text) :]
            prev_text = data["message"]
            window.insert(tk.END, message)
            window.see(tk.END)
        window.insert('end', '\n' + '-'*50 + '\n', 'separator')  # Add separation line
        window.config(state='disabled')  # Make it read only
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
        window.config(state='normal')  # Make it editable
        window.insert(tk.END, "AI (Bing):\n")
        prev_text = ""
        async for final, response in self.bing.ask_stream(prompt=prompt, conversation_style=EdgeGPT.ConversationStyle.creative):
            if not final:
                window.insert(tk.END, response[len(prev_text):])
                window.see(tk.END)
                prev_text = response
        window.insert('end', '\n' + '-'*50 + '\n', 'separator')  # Add separation line
        window.config(state='disabled')  # Make it read only
        
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
        self.browser = BrowserInteraction(link)
        self.chatAI = ChatAI()
        self.ocr = OCR()

        ttk.Frame.__init__(self, parent, **kwargs)
        self.parent = parent
        self.parent.configure(bg='white')
        self.parent.geometry('1000x600')
        self.parent.minsize(800, 480)
        self.parent.grid_columnconfigure(0, weight=3)  # Make the main window responsive horizontally
        self.parent.grid_columnconfigure(1, weight=2)  # Make the system prompt responsive horizontally
        self.parent.grid_rowconfigure(1, weight=1)    # Make the main window responsive vertically

        self.parent.iconbitmap('icon.ico')

        self.initialize_user_interface()

    def handle_engine(self, event):
        self.chatAI.set_model(self.gpt_combobox.get())

    def initialize_user_interface(self):
        # Create labels for widgets
        ttk.Label(self.parent, text='System Prompt:', background='white', padding=10).grid(column=1, row=0, sticky='w')
        ttk.Label(self.parent, text='Message Input:', background='white', padding=10).grid(column=0, row=2, sticky='w')

        # Define the system prompt input field
        self.system_prompt = scrolledtext.ScrolledText(self.parent, height=3, width=25)
        self.system_prompt.grid(column=1, row=1, rowspan=5, padx=10, pady=10, sticky="nsew")

        # Define the chat history box
        self.chat_history = scrolledtext.ScrolledText(self.parent, height=15, width=50)
        self.chat_history.grid(column=0, row=1, padx=10, pady=10, sticky="nsew")
        self.chat_history.config(state='disabled', bg='#E8F5E9')  # Initially, this is not editable
        self.chat_history.configure(font=("Arial", 12))  # Change the font to Arial with size 12


        # Define the message input field
        self.message_input = scrolledtext.ScrolledText(self.parent, height=8, width=50)
        self.message_input.grid(column=0, row=3, padx=10, pady=10, sticky="ew")
        self.message_input.config(bg='#FFF9C4')

        style = ttk.Style()
        style.configure("White.TEntry", fieldbackground="white")
        style.configure("White.TButton", background="white")
        style.configure("White.TCheckbutton", background="white")

        # Define the timestamp input field
        self.timestamp_frame = tk.Frame(self.parent, background="white")
        ttk.Label(self.timestamp_frame, text='Timestamp:', background='white', padding=10).grid(column=0, row=0, sticky='e')
        self.timestamp = ttk.Entry(self.timestamp_frame, width=20, style="White.TEntry")
        self.timestamp.grid(column=1, row=0, padx=10, pady=5, sticky="we")
        # Adding a text entry field for 'time span' inside the frame
        ttk.Label(self.timestamp_frame, text='Time Span:', background='white', padding=10).grid(column=2, row=0, sticky='e')
        self.time_span = ttk.Entry(self.timestamp_frame, width=20, style="White.TEntry")
        self.time_span.insert(0, '180')
        self.time_span.grid(column=3, row=0, padx=10, pady=5, sticky="we")

        self.timestamp_frame.grid(column=0, row=5, padx=10, pady=10, sticky="w")

        # Define the send message button
        self.send_button = ttk.Button(self.parent, text="Send", command=lambda: threading.Thread(target=self.send_message).start(), style="White.TButton")
        self.send_button.grid(column=0, row=5, padx=10, pady=10, sticky="e")

        # Create a frame for the new widgets
        self.extra_options_frame = tk.Frame(self.parent, background="white")
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
        self.reset_chat = BooleanVar(value=True)
        self.reset_chat_box = ttk.Checkbutton(self.extra_options_frame, text='Reset', variable=self.reset_chat, style="White.TCheckbutton")
        Tooltip(self.reset_chat_box, "Reset the chatbot's memory each time you hit send without a message\nThis may be required for bing to work properly as it might terminate conversations occasionally")
        self.reset_chat_box.grid(column=4, row=0, padx=10, pady=5, sticky="we")

        # Adding a checkbox for copy inside the frame
        self.copy_response = BooleanVar(value=True)
        self.copy_response_box = ttk.Checkbutton(self.extra_options_frame, text='Copy', variable=self.copy_response, style="White.TCheckbutton")
        Tooltip(self.copy_response_box, "Copy the response to clipboard after each message for fast note-taking.\nYou can paste it to Notion or alike tools for better readability")
        self.copy_response_box.grid(column=5, row=0, padx=10, pady=5, sticky="we")

        self.extra_options_frame.grid(column=0, row=0, padx=10, pady=10, columnspan=1, sticky="nsew")

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
        mm, ss = timestamp.split(':')
        return int(mm) * 60 + int(ss)

    def get_relevant_transcription_from_timestamp(self, timestamp):
        text_list = []
        int_timestamp = self.timestamp_to_int(timestamp)
        for time, text in self.browser.timestamp_data.items():
            int_time = self.timestamp_to_int(time)
            if abs(int_timestamp - int_time) < int(self.time_span.get()) and text != None:
                text_list.append(f"{text} [{time}]\n")
        return " ".join(text_list)

    def construct_prompt(self):
        prompt = ""
        if self.ocr_value.get():
            self.system_prompt.insert('end', "Running OCR...\n")
            self.system_prompt.see(tk.END)
            prompt += "[OCR]\n" + self.get_ocr_prompt()
        prompt += "\n" + "[TRANSCRIPTION]\n" + self.get_relevant_transcription_from_timestamp(self.retrieve_timestamp()) + MESSAGE + "\nCurrent timestamp: " + self.retrieve_timestamp() + "\n"
        self.system_prompt.insert('end', prompt)
        self.system_prompt.see(tk.END)
        return prompt

    def send_message(self):
        self.send_button.config(state="disabled")
      # Get the current message
        try:
            message = self.message_input.get("1.0", 'end-1c')
            if message:  #if message is not empty
                self.message_input.delete("1.0", 'end')  # Clear the input field

                # Add the message to the chat history
                self.chat_history.config(state='normal')  # Make it editable
                self.chat_history.insert('end', "You: " + message + '\n')
                self.chat_history.tag_config('separator', foreground='grey')

                #Send message
                self.chatAI.generate_response(message, self.chat_history, self.reset_chat.get(), self.copy_response.get())

                self.chat_history.config(state='disabled')  # M
            else:
                self.chatAI.generate_response(self.construct_prompt(), self.chat_history, self.reset_chat.get(), self.copy_response.get())
        except Exception as e:
            self.chat_history.insert('end', f"Error: {repr(e)} \nYou might want to try other models for now, and make sure you update all dependencies of this program. The official models are stable yet cost you money.\n")
            self.system_prompt.insert('end', f"Error: {repr(e)}\n")
        self.send_button.config(state="normal")
            


class BrowserInteraction:
    def __init__(self, link):
        # Create a new instance of the Edge driver
        self.driver = webdriver.Edge()
        self.timestamp_data = {}  # Dictionary to store timestamp data
        self.get_transcription(link)

    def get_transcription(self, link):
        # Load the webpage
        self.driver.get(link)# Replace with the URL of the webpage

        # Wait until the elements with class "index-event-row" are present
        wait = WebDriverWait(self.driver, 120)  # Maximum wait time of 120 seconds
        elements_present = EC.presence_of_all_elements_located((By.CLASS_NAME, 'index-event-row'))
        wait.until(elements_present)

        # Find all the elements with class "index-event-row"
        elements = self.driver.find_elements(By.CLASS_NAME, 'index-event-row')

        # Iterate over the elements
        for element in elements:
            try:
                # Extract the text
                text = WebDriverWait(element, 60).until(EC.visibility_of_element_located((By.CLASS_NAME, 'event-text'))).text

                # Extract the timestamp
                timestamp = WebDriverWait(element, 60).until(EC.visibility_of_element_located((By.CLASS_NAME, 'event-time'))).text

                # Store the text and timestamp in the dictionary
                self.timestamp_data[timestamp] = text

            except Exception as e:
                print(f"Error occurred while extracting element data: {e}")

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
    link = simpledialog.askstring("Input", "Please enter the link to the lecture recording:")
    root = tk.Tk()
    root.title("Cope Hard I Cry")
    ChatClient(link, root)
    root.mainloop()

if __name__ == "__main__":
    main()
