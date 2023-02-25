# TweetScraper
- This repository presents a kind of web-scraping that allows you to get tweets from the Twitter with the features you specify.
- Scraper provides the following informations for each tweet. (Modifiable)
-         'tweet_id', 'tweet_created_at', 'lang','source', 'text', 'like_count',
-         'quote_count','reply_count','retweet_count','entities','hashtags','mentions','conversation_id'
-         'referenced_tweets','possibly_sensitive','in_reply_to_user_id','retweeted_user_id','geo','author_id'
-         'author_created_at','author_screen','name','description','user_tweet_count',
-         'user_followers_count','user_following_count','user_listed_count','verified','user_entities',
-         'pinned_tweet_id','profile_image_url','withheld'
## Prerequest
-           Python 3.6 or newer versions.
-           Academic bearer token for full-arsive search.(https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens)

## How to use?
- You can modify your 'search_string' via config file.
- Config file content:
-         'bearer_token': Your academic bearer token.
-         'query_string': Query that you want to search for it. (Check for various query strings that you can make:https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query
-         'tw_start_date': Starting period of searching query_string.
-         'tw_end_date': Ending period of searching query_string.

## Sample query and possible output
- query_string = 'from:KingJames lang:en'
- tw_start_date = '2023-01-01T00:00:00Z'
- tw_end_date = '2023-02-24T00:00:00Z'

- <img width="763" alt="Screenshot_1" src="https://user-images.githubusercontent.com/70888420/221368634-d9bfbfb4-f791-496a-bb18-e2cd29c62692.png">
