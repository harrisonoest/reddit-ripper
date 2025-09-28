#!/usr/bin/env python3
"""Extract Reddit posts and comments to LLM-optimized markdown format."""
import praw
import re
import argparse
import sys
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class RedditRipper:
    def __init__(self, client_id, client_secret, user_agent):
        """Initialize Reddit API connection."""
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
    
    def extract_post_id(self, url):
        """Extract post ID from Reddit URL."""
        # Match pattern: /comments/[post_id]/
        match = re.search(r'/comments/([a-zA-Z0-9]+)', url)
        return match.group(1) if match else None
    
    def sanitize_filename(self, text):
        """Sanitize text for use in filename and convert to snake_case."""
        # Remove invalid filename characters
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        # Keep only alphanumeric, whitespace, and hyphens
        text = re.sub(r'[^\w\s-]', '', text)
        # Convert spaces and hyphens to underscores
        text = re.sub(r'[-\s]+', '_', text)
        return text.lower()[:100].strip('_')
    
    def extract_comments(self, comment_forest, depth=0, top_level_only=False):
        """Recursively extract comments with hierarchy."""
        comments = []
        
        for comment in comment_forest:
            if hasattr(comment, 'body'):
                # Indent based on comment depth
                indent = "  " * depth
                comments.append(f"{indent}- {comment.body}")
                
                # Recursively process replies unless top-level only
                if not top_level_only and comment.replies:
                    comments.extend(self.extract_comments(comment.replies, depth + 1))
        
        return comments
    
    def extract_post(self, url, top_level_only=False):
        """Extract post and comments from Reddit URL."""
        post_id = self.extract_post_id(url)
        if not post_id:
            raise ValueError("Invalid Reddit URL")
        
        submission = self.reddit.submission(id=post_id)
        # Load all comments (replace "more comments" placeholders)
        submission.comments.replace_more(limit=None)
        
        # Extract post data
        post_data = {
            'title': submission.title,
            'subreddit': submission.subreddit.display_name,
            'content': submission.selftext or '[Link Post]',
            'url': url,
            'comments': self.extract_comments(submission.comments, top_level_only=top_level_only)
        }
        
        return post_data
    
    def format_markdown(self, post_data):
        """Format extracted data as LLM-optimized markdown."""
        md = f"# {post_data['title']}\n\n"
        md += f"**Original Post:** {post_data['url']}\n\n"
        md += f"**Subreddit:** r/{post_data['subreddit']}\n\n"
        md += f"## Post Content\n\n{post_data['content']}\n\n"
        
        if post_data['comments']:
            md += "## Comments\n\n"
            md += "\n".join(post_data['comments'])
        
        return md
    
    def save_to_file(self, post_data, markdown_content):
        """Save markdown content to file with proper naming in output directory."""
        os.makedirs('output', exist_ok=True)
        
        # Create filename from title and subreddit
        title = self.sanitize_filename(post_data['title'])
        subreddit = self.sanitize_filename(post_data['subreddit'])
        filename = f"reddit_{title}_{subreddit}.md"
        filepath = os.path.join('output', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filepath

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Extract Reddit post and comments to markdown')
    parser.add_argument('url', help='Reddit post URL')
    parser.add_argument('--client-id', help='Reddit API client ID (or set REDDIT_CLIENT_ID in .env)')
    parser.add_argument('--client-secret', help='Reddit API client secret (or set REDDIT_CLIENT_SECRET in .env)')
    parser.add_argument('--user-agent', default='RedditRipper/1.0', help='User agent string')
    parser.add_argument('--top-level-only', action='store_true', help='Extract only top-level comments')
    
    args = parser.parse_args()
    
    # Get credentials from CLI args or environment variables
    client_id = args.client_id or os.getenv('REDDIT_CLIENT_ID')
    client_secret = args.client_secret or os.getenv('REDDIT_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("Error: Reddit API credentials required. Provide via CLI args or .env file.", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Extract and save Reddit post
        ripper = RedditRipper(client_id, client_secret, args.user_agent)
        post_data = ripper.extract_post(args.url, args.top_level_only)
        markdown_content = ripper.format_markdown(post_data)
        filename = ripper.save_to_file(post_data, markdown_content)
        
        print(f"Successfully extracted to: {filename}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
