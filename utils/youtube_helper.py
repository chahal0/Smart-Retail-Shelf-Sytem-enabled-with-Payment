import yt_dlp

def fetch_youtube_comments(video_url, max_comments=100):
    """
    Fetches comments from a YouTube video utilizing yt-dlp.
    Returns a list of comment texts.
    """
    ydl_opts = {
        'getcomments': True,
        'skip_download': True,
        'quiet': True,
        'extract_flat': True, # Don't download video
        'max_comments': max_comments
    }
    
    comments = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            if 'comments' in info:
                for c in info['comments']:
                    if isinstance(c, dict) and 'text' in c:
                         comments.append(c['text'])
            # Sometimes comments are not in 'comments' key directly or need different handling depending on yt-dlp version/extractor
            # But standard extraction should work.
    except Exception as e:
        print(f"Error extracting comments: {e}")
        return []
        
    return comments
