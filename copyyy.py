
import random
import requests
import json
import os
from typing import final, Dict, List
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.helpers import escape_markdown

TOKEN: final = '7160155977:AAEoNgMOzAtgozwgwctUrla2w7YieKKm9RA'
BOT_USERNAME: final = '&privatebotashekcbot'
DATA_FILE = "video_data.json"

list_of_dicts: List[Dict[str, Dict[str, str]]] = []  # List of dictionaries



# Function to load the data from the JSON file
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return []

# Function to save the list_of_dicts to the JSON file
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(list_of_dicts, file, indent=4)

def clear_json_file(file_path: str):
    # Clear the JSON file by writing an empty list
    with open(file_path, 'w') as json_file:
        json.dump([], json_file)  # Writes an empty list to the file
# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("What do you need help with?")

async def costume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command")
async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await clear_videos_command(update, context)

import requests

async def random_wiki_article(update, context):
    url = "https://en.wikipedia.org/api/rest_v1/page/random/summary"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        title = escape_markdown(data["title"], version=2)  # Escape Markdown
        summary = escape_markdown(data["extract"], version=2)  # Escape Markdown
        article_url = data["content_urls"]["desktop"]["page"]  # URLs don't need to be escaped
        
        message = f"*Title*: {title}\n\n*Summary*: {summary}\n\n[Read More]({article_url})"
        
        await update.message.reply_text(message, parse_mode="MarkdownV2")  # Use MarkdownV2
    else:
        await update.message.reply_text("Couldn't fetch a random Wikipedia article.")


async def add_video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /add <category> <video name> <url>")
        return
    
    category = context.args[0].strip()
    video_name = context.args[1].strip()
    url = context.args[2].strip()
    
    found = False
    for category_dict in list_of_dicts:
        if category in category_dict:
            category_dict[category][video_name] = url
            found = True
            break
    
    if not found:
        new_category = {category: {video_name: url}}
        list_of_dicts.append(new_category)

    save_data()  # Save after modifying the list

    await update.message.reply_text(f"Added video '{video_name}' under category '{category}'.")

async def pull_video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not list_of_dicts:
        await update.message.reply_text("No videos found.")
        return

    # Collect categories
    categories = [list(category_dict.keys())[0] for category_dict in list_of_dicts]
    
    await update.message.reply_text("Choose a category:", reply_markup=ReplyKeyboardMarkup([[category] for category in categories], one_time_keyboard=True))

    context.user_data['pull_category'] = True  # Set the flag for category selection

async def handle_pull_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'pull_category' in context.user_data:
        category = update.message.text.strip()  # Normalize input
        category_found = False

        for category_dict in list_of_dicts:
            if category.lower() in (key.lower() for key in category_dict.keys()):  # Compare in lowercase
                videos = category_dict[category]
                reply_keyboard = [[video_name] for video_name in videos.keys()]
                await update.message.reply_text("Choose a video:", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
                context.user_data['selected_category'] = category  # Set selected category
                del context.user_data['pull_category']  # Clear the pull_category flag
                category_found = True
                return  # Exit after processing the category

        if not category_found:
            await update.message.reply_text(f"Category '{category}' not found.")
    else:
        # Handle selecting the video
        category = context.user_data.get('selected_category')
        if category:
            for category_dict in list_of_dicts:
                if category in category_dict:
                    video_name = update.message.text.strip()  # Normalize input
                    if video_name in category_dict[category]:
                        url = category_dict[category][video_name]
                        await update.message.reply_text(f"URL for '{video_name}' in '{category}': {url}")
                        del context.user_data['selected_category']  # Clear selected category
                        return

            await update.message.reply_text(f"Video '{video_name}' not found in category '{category}'.")
        else:
            await update.message.reply_text("No category selected. Please use /pull first.")

async def clear_videos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    list_of_dicts.clear()  # Clear all videos
    await update.message.reply_text("All videos have been cleared.")

# Responses
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type: str = update.message.chat.type
    text: str = update.message.text
    print(f'user {update.message.chat.id} in {chat_type}: {text}')
    
    if chat_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    
    print('bot', response)
    await update.message.reply_text(response)
async def clear_videos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    list_of_dicts.clear()  # Clear all videos
    clear_json_file(DATA_FILE)  # Clear JSON file
    await update.message.reply_text("All videos have been cleared.")

def handle_response(text: str) -> str: 
    processed: str = text.lower()
    if 'hello' in processed:
        return 'heyyyyyyyyy'
    if 'how are you' in processed:
        return 'I am good'
    if 'delete' in processed or '/delete' in processed:
        clear_videos_command(DATA_FILE)
        return 'archive was deleted'
    else:
        return 'I don’t understand'

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'update {update} caused error {context.error}')

if __name__ == '__main__':
     list_of_dicts=load_data()
     print('starting bot')
     app = Application.builder().token(TOKEN).build()

     # Commands
     app.add_handler(CommandHandler('start', start_command))
     app.add_handler(CommandHandler('help', help_command))
     app.add_handler(CommandHandler('costume', costume_command))
     app.add_handler(CommandHandler('add', add_video_command))  # Add video command
     app.add_handler(CommandHandler('pull', pull_video_command))  # Pull video command
     app.add_handler(CommandHandler('clear', clear_videos_command))  # Clear videos command
     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_pull_category))
     app.add_handler(CommandHandler('randomwiki', random_wiki_article))  # Command to fetch random Wikipedia article
     app.add_handler(CommandHandler('delete', delete_command))  # Command to clear videos

     # Messages
     app.add_handler(MessageHandler(filters.TEXT, handle_message))

     # Errors
     app.add_error_handler(error)
    
     # Poll the bot
     print('polling...')
     app.run_polling(poll_interval=3)

