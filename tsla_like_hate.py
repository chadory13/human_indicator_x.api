import tweepy
import pandas as pd
import time
from tweepy.errors import TooManyRequests
from textblob import TextBlob  # pip install textblob

# 1) API 초기화
bearer_token =
client = tweepy.Client(bearer_token=bearer_token)

# 2) 감성 분석 함수
def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"

# 3) 검색 조건: $TSLA 언급, 리트윗·답글 제외, 영어 트윗만
query = '"$TSLA" -is:retweet -is:reply lang:en'

# 4) 한번에 가져올 최대 개수, 결과 저장용
max_results = 100
tweets_data = []

# 5) 데이터 가져오기 및 예외 처리
try:
    resp = client.search_recent_tweets(
        query=query,
        tweet_fields=["created_at","public_metrics","entities"],
        max_results=max_results
    )
except TooManyRequests:
    print("Rate limit hit. 15분 대기 후 재시도합니다.")
    time.sleep(15 * 60)
    resp = client.search_recent_tweets(
        query=query,
        tweet_fields=["created_at","public_metrics","entities"],
        max_results=max_results
    )

# 6) 트윗별로 정보 추출
if resp.data:
    for tweet in resp.data:
        # cashtags(주식티커)가 실제로 있는지 한 번 더 체크
        if tweet.entities and "cashtags" in tweet.entities:
            sentiment = analyze_sentiment(tweet.text)
            metrics = tweet.public_metrics
            tweets_data.append({
                "tweet_id":    tweet.id,
                "created_at":  tweet.created_at,
                "text":        tweet.text,
                "sentiment":   sentiment,
                "like_count":  metrics.get("like_count", 0),
                "retweet_count": metrics.get("retweet_count", 0),
            })

# 7) DataFrame 생성 및 저장
df = pd.DataFrame(tweets_data)
df.to_csv("tsla_sentiment_tweets.csv", index=False, encoding="utf-8-sig")
print("CSV 파일(tsla_sentiment_tweets.csv) 저장 완료!")
