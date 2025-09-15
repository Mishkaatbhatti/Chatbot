import os
import gradio as gr
import google.generativeai as genai

# 🔑 Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Load model (flash = faster, pro = more powerful)
model = genai.GenerativeModel("gemini-2.5-flash")

# Chat function with memory
def chat_with_gemini(message, history):
    # Convert Gradio history to Gemini format
    conversation = []
    for user, bot in history:
        conversation.append({"role": "user", "parts": [user]})
        if bot:
            conversation.append({"role": "model", "parts": [bot]})
    conversation.append({"role": "user", "parts": [message]})

    try:
        response = model.generate_content(conversation)
        bot_reply = response.text
    except Exception as e:
        bot_reply = f"❌ Error: {str(e)}"

    history.append((message, bot_reply))
    return "", history

# Create Gradio Chatbot UI
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## 🤖 Gemini Chatbot\nTalk with Google's Gemini in real time!")

    chatbot = gr.Chatbot(height=450, bubble_full_width=False)
    msg = gr.Textbox(label="Type your message", placeholder="Ask me anything...")
    clear = gr.Button("🗑️ Clear Chat")

    msg.submit(chat_with_gemini, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

demo.launch()
