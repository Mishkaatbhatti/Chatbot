import os
import gradio as gr
import google.generativeai as genai

# 🔑 Get API key from Hugging Face secrets
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ No API key found. Please set GEMINI_API_KEY in Hugging Face secrets.")

# Configure Gemini client
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

# Store reactions separately
reactions_dict = {}

# Chat function
def chat_with_gemini(message, history):
    history = history or []
    response = model.generate_content(message)
    bot_reply = response.text

    history.append((message, bot_reply))
    history_text = "\n".join([f"👤 {m}\n🤖 {r}\n{reactions_dict.get(i,'')}" for i,(m,r) in enumerate(history)])

    return history, history, history_text, ""  # "" clears textbox

# Function to save history
def download_history(history_text):
    if not history_text.strip():
        return None
    file_path = "chat_history.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(history_text)
    return file_path

# Add reaction
def add_reaction(index, reaction, history):
    if history and 0 <= index < len(history):
        reactions_dict[index] = f"⭐ Reaction: {reaction}"
    history_text = "\n".join([f"👤 {m}\n🤖 {r}\n{reactions_dict.get(i,'')}" for i,(m,r) in enumerate(history)])
    return history_text

# CSS for dark/light mode
custom_css = """
:root {
    --user-bg-light: #DCF8C6;
    --bot-bg-light: #F1F0F0;
    --sidebar-bg-light: #f8f9fa;

    --user-bg-dark: #056162;
    --bot-bg-dark: #262d31;
    --sidebar-bg-dark: #1e1e1e;

    --text-light: #000;
    --text-dark: #fff;
}

body.light {
    background-color: #fff !important;
    color: var(--text-light) !important;
}
body.light .chatbot .message.user {
    background-color: var(--user-bg-light) !important;
    color: var(--text-light) !important;
}
body.light .chatbot .message.bot {
    background-color: var(--bot-bg-light) !important;
    color: var(--text-light) !important;
}
body.light #sidebar {
    background-color: var(--sidebar-bg-light) !important;
    color: var(--text-light) !important;
}

body.dark {
    background-color: #121212 !important;
    color: var(--text-dark) !important;
}
body.dark .chatbot .message.user {
    background-color: var(--user-bg-dark) !important;
    color: var(--text-dark) !important;
}
body.dark .chatbot .message.bot {
    background-color: var(--bot-bg-dark) !important;
    color: var(--text-dark) !important;
}
body.dark #sidebar {
    background-color: var(--sidebar-bg-dark) !important;
    color: var(--text-dark) !important;
    border-right: 2px solid #333 !important;
}
"""

# Gradio UI
with gr.Blocks(css=custom_css) as demo:
    theme_state = gr.State("light")  # default theme

    gr.Markdown("<h2 style='text-align:center;'>🤖 Gemini Chatbot</h2>")

    with gr.Row():
        # Sidebar
        with gr.Column(scale=1, elem_id="sidebar"):
            theme_toggle = gr.Radio(["Light ☀️", "Dark 🌙"], value="Light ☀️", label="Theme")
            with gr.Accordion("📜 Chat History", open=True):
                history_box = gr.Textbox(label="Conversation Log", interactive=False, lines=20)
                download_btn = gr.Button("⬇️ Download History")
                file_output = gr.File(label="Download your conversation")
            with gr.Accordion("⭐ React to Last Bot Reply", open=True):
                reaction_choice = gr.Radio(["👍", "👎", "❤️"], label="Pick a reaction")
                reaction_btn = gr.Button("✅ Add Reaction")

        # Main chat area
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(height=500, elem_classes="chatbot")
            msg = gr.Textbox(placeholder="💬 Type your message here and press Enter...")
            clear = gr.Button("🗑️ Clear Chat")

            msg.submit(chat_with_gemini, [msg, chatbot], [chatbot, chatbot, history_box, msg])
            clear.click(lambda: ([], [], "", ""), None, [chatbot, chatbot, history_box, msg], queue=False)
            download_btn.click(download_history, inputs=[history_box], outputs=[file_output])

            reaction_btn.click(add_reaction, inputs=[gr.Number(value=-1, label="Message Index (auto last)", visible=False), reaction_choice, chatbot], outputs=[history_box])

    # Theme switching
    def switch_theme(choice):
        return choice.lower().split()[0]

    theme_toggle.change(switch_theme, inputs=[theme_toggle], outputs=[theme_state])

demo.launch()
