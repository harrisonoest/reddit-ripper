# Reddit Ripper

Extract Reddit posts and comments to LLM-optimized markdown format.

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Get Reddit API credentials:
   - Go to https://www.reddit.com/prefs/apps
   - Create a new application (script type)
   - Note your client_id and client_secret

4. Create a `.env` file (optional):
```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
```

## Usage

### With .env file:
```bash
python reddit_ripper.py <reddit_url>
```

### With CLI arguments:
```bash
python reddit_ripper.py <reddit_url> --client-id <your_client_id> --client-secret <your_client_secret>
```

### Options

- `--client-id`: Reddit API client ID (optional if set in .env)
- `--client-secret`: Reddit API client secret (optional if set in .env)
- `--top-level-only`: Extract only top-level comments (skip nested replies)
- `--user-agent`: Custom user agent string (default: RedditRipper/1.0)

### Example

```bash
python reddit_ripper.py "https://www.reddit.com/r/Python/comments/abc123/example_post/"
```

## Output

- Files are saved to the `output/` directory (created automatically)
- Filename format: `reddit_{title}_{subreddit}.md`
- Example: `reddit_example_post_python.md`

## Output Format

The generated markdown is optimized for LLM consumption with:
- Clear post title and subreddit
- Post content section
- Hierarchical comment structure using indentation
- No metadata clutter

## Cleanup

When finished, deactivate the virtual environment:
```bash
deactivate
```
