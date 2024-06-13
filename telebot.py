from telegram.ext import ApplicationBuilder, MessageHandler, filters
import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# OpenAI client setup
client = openai.OpenAI(base_url=os.getenv('BASE_URL'), api_key=os.getenv('API_KEY'))

# Replace 'YOUR_TOKEN' with the token you got from BotFather
TOKEN = os.getenv('TOKEN')

#Enable Groupchat Mode with @bot set to true to enable
GROUP_CHAT_MODE = os.getenv('GROUP_CHAT_MODE')
print('group chat mode:', GROUP_CHAT_MODE)
if GROUP_CHAT_MODE is None:
    GROUP_CHAT_MODE = False  # Set a default value
else:
    GROUP_CHAT_MODE = GROUP_CHAT_MODE.lower() == 'true'


# A dictionary to keep track of chat histories for different users
chat_histories = {}

def get_openai_response(user_id, message):
    # Check if the user already has a history, otherwise start a new one
    if user_id not in chat_histories:
        chat_histories[user_id] = [
            {"role": "system", "content": "You are an intelligent assistant. You always provide well-reasoned answers that are both correct and helpful."

            }
        ]

    # Add the new user message to the history
    chat_histories[user_id].append({"role": "user", "content": message})

    try:
        completion = client.chat.completions.create(
            model=os.getenv('MODEL'),  # Adjust the model as per your setup
            messages=chat_histories[user_id],
            temperature=0.7,
        )
        # Accessing the first choice and then the message content
        response_message = completion.choices[0].message
        
        # Add the response to the history
        chat_histories[user_id].append({"role": "assistant", "content": response_message.content})

        return response_message.content  # Accessing content attribute

    except Exception as e:
        print(f"Error in generating response: {e}")
        return "I am unable to respond at this moment."

# Function to handle messages
async def handle_message(update, context):
    user_id = update.effective_chat.id
    message_text = update.message.text

    if GROUP_CHAT_MODE:
        # Check if the message contains "@bot"
        if "@bot" in message_text:
            # Remove "@bot" from the message text
            processed_text = message_text.replace("@bot", "").strip()

            # Get response from OpenAI
            openai_response = get_openai_response(user_id, processed_text)

            # Send the response back to the user
            await context.bot.send_message(chat_id=user_id, text=openai_response)
    else:
        # Get response from OpenAI
        openai_response = get_openai_response(user_id, message_text)

        # Send the response back to the user
        await context.bot.send_message(chat_id=user_id, text=openai_response)

def main():
    # Create an ApplicationBuilder instance
    application = ApplicationBuilder().token(TOKEN).build()

    # Handle messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()