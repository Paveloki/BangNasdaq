import re
import tweepy
import pandas as pd
from datetime import date
from textblob import TextBlob


def clean_text(text):
    text = re.sub(r'@[A-Za-z0-9]+', '', text) #Remove mentions
    text = re.sub(r'#', '', text) #Remove #
    text = re.sub(r'RT[\s]:+', '', text) #Remove RT
    text = re.sub(r'https:\/\/\S+', '', text) #Remove mentions
    text = re.sub('\n'," ",text)
    text = re.sub('-\n([a-z])', '', text)
    text = re.sub('\r'," ",text)
    text = re.sub('-\r([a-z])', '', text)
    text = deEmojify(text)
    return text


def deEmojify(text):
    regrex_pattern = re.compile(pattern="["
                                        u"\U0001F600-\U0001F64F"  # emoticons
                                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                        "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'', text)


def getSubjectivity(text):
    return TextBlob(text).sentiment.subjectivity


def getPolarity(text):
    return TextBlob(text).sentiment.polarity


def x_range(x):
    if x > 0:
        return 1
    elif x == 0:
        return 0
    else:
        return -1


def x_range_sentiment(x):
    if x > 0:
        return 'Positive'
    elif x == 0:
        return 'Neutral'
    else:
        return 'Negative'


def get_tweets(stock: str, update: str):
    if update == "upyes":
        consumer_key = "89sGhwiTspic1SS4NBnnv6yHk"
        consumer_secret = "wPMainc6F8aw1KPYjWpBUz17wTUQJdDUu4a5vyjWsSYPPbMNvH"
        access_token = "3243736436-RkiWCNFrQ5Gl82OFSCtENHqnRdRrnjeTB5pOpk6"
        access_token_secret = "FzxpAu9WCmJYJIeTyqqT8p1mf0kum4s8z2sArU3MAqgDW"

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        query = '$' + stock

        tweets = api.search(q=query,
                            # 200 is the maximum allowed count
                            count=100,
                            include_rts=False,
                            # Necessary to keep full_text
                            # otherwise only the first 140 words are extracted
                            tweet_mode='extended'
                            )

        all_tweets = []
        all_tweets.extend(tweets)
        oldest_id = tweets[-90].id

        for i in range(160):
            i += 1
            tweets = api.search(q=query,
                                # 200 is the maximum allowed count
                                count=100,
                                include_rts=False,
                                lang='en',
                                max_id=oldest_id - 1,

                                # Necessary to keep full_text
                                # otherwise only the first 140 words are extracted
                                tweet_mode='extended'
                                )
            if len(tweets) == 0:
                break
            oldest_id = tweets[-1].id
            all_tweets.extend(tweets)

            print('N of tweets downloaded till now {}'.format(len(all_tweets)), 'ciclo = ', i)

        outtweets = [[tweet.id_str,
                      tweet.user,
                      tweet.created_at,
                      tweet.favorite_count,
                      tweet.retweet_count,
                      tweet.full_text.encode("utf-8").decode("utf-8")]
                     for idx, tweet in enumerate(all_tweets)]
        df = pd.DataFrame(outtweets, columns=["id", 'user_name', "created_at", "favorite_count", "retweet_count", "text"])
        df['Date'] = df['created_at'].map(lambda x: x.date())
        df['text'] = df['text'].apply(clean_text)
        df['Subjectivity'] = df['text'].apply(getSubjectivity)
        df['Polarity'] = df['text'].apply(getPolarity)
        df['result'] = df['Polarity'].apply(x_range)
        df['Sentiment'] = df['Polarity'].apply(x_range_sentiment)
        df.to_csv("$SPY_tweets.csv", index=False)
        return df
    else:
        print("No update")
