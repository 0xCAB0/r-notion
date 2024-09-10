import os, praw, re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


reddit = praw.Reddit(
    client_id=os.environ["REDDIT_CLIENT_ID"],
    client_secret=os.environ["REDDIT_CLIENT_SECRET"],
    password=os.environ["REDDIT_CLIENT_PASSWORD"],
    username=os.environ["REDDIT_CLIENT_USERNAME"],
)


# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Function to post to Reddit
def post_to_reddit(title, content, subreddit="your_subreddit"):
    try:
        reddit.subreddit(subreddit).submit(title=title, selftext=content)
        print(f"Posted to Reddit: {title}")
    except Exception as e:
        print(f"Error posting to Reddit: {e}")

# Listen for incoming messages from the Notion Slack app
@app.message(re.compile(r'.*edited in.*Status.*'))
def notion_update_handler(message, say):
    # Example message:
    # "Impakta Administrator edited in :spiral_note_pad: Posts · Today 5:58 PM :new: Aplicaciones de digital-wellness: COMPARATIVA Status Changes to be made → Published Author Gonzalo Sucunza"
    
    # Extract relevant information from the message
    text = message.get("text", "")
    
    # Extract the post title (this assumes a format where title follows ":new:")
    title_match = re.search(r":new:\s*(.*?):", text)
    title = title_match.group(1).strip() if title_match else "Unknown Title"
    
    # Extract the status change (assuming format "Status X → Y")
    status_match = re.search(r"Status\s*(.*)\s*→\s*(.*)", text)
    old_status = status_match.group(1).strip() if status_match else "Unknown"
    new_status = status_match.group(2).strip() if status_match else "Unknown"

    # Extract the author (assuming format "Author NAME")
    author_match = re.search(r"Author\s*(.*)", text)
    author = author_match.group(1).strip() if author_match else "Unknown Author"

    # Formulate the content for Reddit post
    content = f"Title: {title}\nStatus changed from {old_status} to {new_status}\nAuthor: {author}"

    # Post to Reddit
    post_to_reddit(title=f"Status Update: {title}", content=content)

    # Optionally send a confirmation message back to the Slack channel
    say(f"Posted update to Reddit: {title}")

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()