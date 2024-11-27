from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_match_score(job_description: str, resume_content: str) -> float:
    """
    Calculate the match score between a job description and resume content.
    Args:
        job_description (str): The text of the job description.
        resume_content (str): The full content of the resume.
    Returns:
        float: Match score as a percentage (0-100).
    """
    # Validate input
    if not job_description.strip() or not resume_content.strip():
        raise ValueError("Both job description and resume content must be provided.")
    # TF-IDF Vectorization with adjusted settings for longer texts
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)  # Limit vocabulary size
    vectors = vectorizer.fit_transform([job_description, resume_content])
    # Compute Cosine Similarity
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    # Convert to percentage
    match_score = round(similarity * 100, 2)
    return match_score