import praw
import config

class SocialMediaScraper:
    """Fetch posts from Reddit"""

    def __init__(self):
        self.reddit_client = None
        self.initialize_api()

    def initialize_api(self):
        """Initialize Reddit API client"""
        try:
            self.reddit_client = praw.Reddit(
                client_id=config.REDDIT_CLIENT_ID,
                client_secret=config.REDDIT_CLIENT_SECRET,
                username=config.REDDIT_USERNAME,
                password=config.REDDIT_PASSWORD,
                user_agent=config.REDDIT_USER_AGENT
            )
            # test connection
            _ = self.reddit_client.user.me()
            print("✓ Reddit API connected successfully")
        except Exception as e:
            print(f"✗ Reddit API connection failed: {str(e)}")
            self.reddit_client = None

    def search_reddit(self, query, subreddit="all", limit=50):
        """Search Reddit for posts matching a keyword"""
        if not self.reddit_client:
            print("✗ Reddit client not initialized")
            return []

        posts = []
        try:
            for submission in self.reddit_client.subreddit(subreddit).search(query, limit=limit):
                posts.append(submission.title + " " + submission.selftext)
            print(f"✓ Found {len(posts)} Reddit posts for '{query}'")
        except Exception as e:
            print(f"✗ Reddit search error: {str(e)}")

        return posts

    def search_all(self, query, count=50):
        """Wrapper method to maintain compatibility"""
        return self.search_reddit(query, limit=count)
