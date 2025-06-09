from flask import Flask, request, abort
import os
from scrape_bhw import get_threads

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

# LINE Bot credentials - Replace these with your actual credentials
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

print(type(LINE_CHANNEL_ACCESS_TOKEN))
print(len(LINE_CHANNEL_ACCESS_TOKEN))

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # Get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # Get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # Handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    if event.message.text.strip().lower() == 'freeb':
        # Get threads from our scraper
        threads = get_threads()
        
        # Format the message
        message = "🎁 Top 3 Recent Giveaways:\n\n"
        for i, thread in enumerate(threads, 1):
            # Format as Markdown link
            message += f"{i}. [{thread['title']}]({thread['url']})\n"
            message += f"   Posted: {thread['timestamp']}\n\n"
        
        # Send the message back to the user
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=message)]
                )
            )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) 