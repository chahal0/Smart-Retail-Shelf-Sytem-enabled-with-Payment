from django.shortcuts import render
from django.http import HttpResponse
from urllib.parse import urlparse
from textblob import TextBlob
from utils.youtube_helper import fetch_youtube_comments

def get_video(video_id):
    if not video_id:
        return {"error": "video_id is required"}

    # Reconstruct URL for yt-dlp
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    comments = fetch_youtube_comments(video_url)
    
    # If no comments found, return empty results
    if not comments:
        return {"predictions": [], "comments": [], "summary": {"positive":0, "negative":0, "num_comments":0, "rating":0}}

    predictions = predict_sentiments(comments)

    positive = predictions.count("Positive")
    negative = predictions.count("Negative")
    
    num_comments = len(comments)
    rating = (positive / num_comments * 100) if num_comments > 0 else 0

    summary = {
        "positive": positive,
        "negative": negative,
        "num_comments": num_comments,
        "rating": rating
    }

    return {"predictions": predictions, "comments": comments, "summary": summary}

def getvideo_id(value):
    """
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
    query = urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = urlparse(query.query)
            return str(p.path[2:]).split('&')[0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    return None

def reviews(request):
    summary = None
    comments = []
    
    if request.method == 'POST':
        video_url = request.POST.get('video_url')
        video_id = getvideo_id(video_url)
        if video_id:
            data = get_video(video_id)
            summary = data['summary']
            comments = list(zip(data['comments'], data['predictions']))
    
    return render(request, 'reviews/index.html', {'summary': summary, 'comments': comments})

def predict_sentiments(text_list):
    """
    Predicts sentiment using TextBlob (local, free).
    """
    sentiments = []
    for text in text_list:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        # Simple thresholding
        if polarity > 0.1:
            sentiments.append("Positive")
        elif polarity < -0.1:
            sentiments.append("Negative")
        else:
            sentiments.append("Neutral")
    return sentiments
