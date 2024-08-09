import google.generativeai as genai
import os

genai.configure(api_key="AIzaSyCbv-uIRcEFL4YTGxk1yoXHGiRDE0KCHwA")
model = genai.GenerativeModel('gemini-1.0-pro-latest')
response = model.generate_content("The opposite of hot is")
print(response.text)