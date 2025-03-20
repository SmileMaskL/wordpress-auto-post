from dotenv import load_dotenv  # 추가된 부분
import requests
from pytrends.request import TrendReq
from bs4 import BeautifulSoup
from datetime import datetime
import os

# ✅ .env 파일 로드
load_dotenv()  # 추가된 부분

# ✅ 워드프레스 API 설정
WORDPRESS_URL = os.getenv('WORDPRESS_URL')
WORDPRESS_USERNAME = os.getenv('WORDPRESS_USERNAME')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

# ✅ Google 트렌드에서 한국의 인기 검색어 가져오기
def get_google_trending_keywords():
    pytrends = TrendReq(hl='ko', tz=360)
    trending = pytrends.trending_searches(pn='south_korea')
    keywords = trending[0].tolist()

    if not keywords:
        raise ValueError("🚨 Google 트렌드에서 인기 검색어를 가져오지 못했습니다.")

    return keywords

# ✅ Twitter 트렌드 (웹 스크래핑 방식)
def get_twitter_trending_keywords():
    url = 'https://trends24.in/south-korea/'
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"🚨 Twitter 트렌드 요청 실패: {e}")

    soup = BeautifulSoup(response.text, 'html.parser')
    trends = [trend.get_text() for trend in soup.select('.trend-card .trend-item span')]

    if not trends:
        raise ValueError("🚨 Twitter 트렌드에서 인기 검색어를 가져오지 못했습니다.")

    return trends

# ✅ 워드프레스에 글 작성
def post_to_wordpress(title, content):
    url = f"{WORDPRESS_URL}/wp-json/wp/v2/posts"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "title": title,
        "content": content,
        "status": "publish"
    }

    try:
        response = requests.post(url, headers=headers, json=data, auth=(WORDPRESS_USERNAME, WORDPRESS_PASSWORD))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"🚨 워드프레스 포스팅 실패: {e}")

    print("✅ 워드프레스 포스팅 성공")

# ✅ 여러 트렌드에서 키워드 수집
def get_trending_keywords():
    google_keywords = get_google_trending_keywords()
    twitter_keywords = get_twitter_trending_keywords()

    all_keywords = list(set(google_keywords + twitter_keywords))

    if not all_keywords:
        raise ValueError("🚨 모든 트렌드에서 인기 검색어를 가져오지 못했습니다.")

    return all_keywords

if __name__ == "__main__":
    try:
        trending_keywords = get_trending_keywords()
        print(f"🔥 인기 검색어: {trending_keywords[:10]}")

        # ✅ 워드프레스에 포스팅
        post_title = f"{datetime.now().strftime('%Y-%m-%d')} 오늘의 인기 검색어"
        post_content = "<br>".join(trending_keywords[:20])
        post_to_wordpress(post_title, post_content)

    except Exception as e:
        print(f"🚨 오류 발생: {e}")
