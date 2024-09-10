import re
from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
import emoji
import seaborn as sns
from collections import Counter
extractor = URLExtract()
def fetch_stats(selected_user, df):

    # Filter by selected user if not 'Overall'
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Fetch the number of messages
    num_messages = df.shape[0]

    # Fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # Fetch number of media messages
    media_msg = df[df['message'].str.strip().isin(['\u200eimage omitted', '\u200evideo omitted', '\u200esticker omitted\n'])].shape[0]

    # Fetch number of Links Shared
    valid_url_pattern = re.compile(r'^(http|https|ftp)://|.*\.(com|org|net|in|edu|gov|co|io)')
    links = []
    for message in df['message']:
        found_urls = extractor.find_urls(message)
        valid_urls = [url for url in found_urls if re.match(valid_url_pattern, url)]
        links.extend(valid_urls)

    return num_messages, len(words), media_msg, len(links)

def most_busy_users(df):
    df = df[df['user'] != 'group_notification']
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x, df

def create_wordcloud(selected_user,df):

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].isin(['\u200eimage omitted', '\u200evideo omitted', '\u200esticker omitted'])]

    def remove_stop_words(message):
        y=[]
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    # Remove unwanted terms (image omitted, video omitted, sticker omitted)
    unwanted_terms = ['\u200eimage omitted', '\u200evideo omitted', '\u200esticker omitted']
    df['message'] = df['message'].replace(unwanted_terms, '', regex=True)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    temp['message']=temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc


def most_common_words(selected_user, df):
    # Read stop words from file
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = set(f.read().splitlines())  # Load stop words as a set for faster lookup

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Filter out group notifications and specific omitted messages
    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].isin(['\u200eimage omitted', '\u200evideo omitted', '\u200esticker omitted'])]

    words = []

    for message in temp['message']:
        # Remove numbers and emojis
        message = re.sub(r'\b\d+\b', '', message)  # Remove numbers
        message = ''.join([char for char in message if char not in emoji.EMOJI_DATA])  # Remove emojis

        # Split the message into words and filter out stop words
        for word in message.lower().split():
            if word not in stop_words and word.isalpha():  # Keep only alphabetic words
                words.append(word)

    # Create a DataFrame with the most common words
    most_common_df = pd.DataFrame(Counter(words).most_common(20), columns=['Word', 'Frequency'])
    return most_common_df

def emoji_helper(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Group by year, month, and month_num, and count messages
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    # Create a time column in the format 'Month-Year'
    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)

    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message',aggfunc='count').fillna(0)

    return user_heatmap
