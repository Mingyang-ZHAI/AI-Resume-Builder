from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from ..skills_config import HARD_SKILLS, SOFT_SKILLS, OTHER_KEYWORDS


def calculate_category_match(category_keywords, content):
    """
    Calculate match percentage for a specific category of keywords.
    Args:
        category_keywords (list): List of keywords for the category.
        content (str): The content to match the keywords against.
    Returns:
        float: Match percentage (0-100).
    """
    if not category_keywords:  # Handle empty keywords list
        return 0.0
    
    if not content.strip():  # Ensure content is not empty
        return 0.0
    
    # Preprocess content and keywords
    content = content.lower()
    category_keywords = [keyword.lower() for keyword in category_keywords]
    
    # Vectorize content and keywords
    vectorizer = CountVectorizer(vocabulary=category_keywords)
    content_vector = vectorizer.fit_transform([content])
    category_vector = vectorizer.transform([' '.join(category_keywords)])
    
    # Debugging: Check vectors
    # print("Category Keywords Vector:", category_vector.toarray())
    # print("Content Vector:", content_vector.toarray())
    
    # Compute cosine similarity
    similarity = cosine_similarity(content_vector, category_vector)[0][0]
    # print("Cosine Similarity:", similarity)
    
    return round(similarity * 100, 2)


def extract_skills_from_text(text, skills):
    """
    Extract relevant skills from text based on a predefined list of skills.
    """
    if not text:
        return []
    text_lower = text.lower()
    relevant_skills = [skill for skill in skills if skill.lower() in text_lower]
    return relevant_skills


def calculate_skill_scores(job, raw_content, processed_content):
    """
    Calculate scores and reports for hard skills, soft skills, and keywords.
    """
    skill_categories = {
        "Hard Skills": HARD_SKILLS,
        "Soft Skills": SOFT_SKILLS,
        "Keywords": OTHER_KEYWORDS,
    }

    scores_and_reports = {}

    for category, skills in skill_categories.items():
        # Extract job-relevant skills
        job_relevant_skills = extract_skills_from_text(job.description, skills)

        if not job_relevant_skills:
            raw_score = 0.0
            processed_score = 0.0
            raw_report = f"No {category.lower()} extracted from the job description."
            processed_report = raw_report
        else:
            raw_score = calculate_category_match(job_relevant_skills, raw_content)
            processed_score = calculate_category_match(job_relevant_skills, processed_content)
            processed_score = max(processed_score, raw_score)

            missing_raw = [skill for skill in job_relevant_skills if skill.lower() not in raw_content.lower()]
            missing_processed = [skill for skill in job_relevant_skills if skill.lower() not in processed_content.lower()]

            raw_report = (
                f"Great work! You have most of the {category.lower()} required for this job."
                if not missing_raw
                else f"You are missing {len(missing_raw)} {category.lower()}: {', '.join(missing_raw)}."
            )

            processed_report = (
                f"Great work! You have most of the {category.lower()} required for this job."
                if not missing_processed
                else f"You are missing {len(missing_processed)} {category.lower()}: {', '.join(missing_processed)}."
            )

        scores_and_reports[category] = {
            "raw_score": raw_score,
            "processed_score": processed_score,
            "raw_report": raw_report,
            "processed_report": processed_report,
        }

    return scores_and_reports


def calculate_title_degree_scores(content, job):
    """
    Calculate degree and title match scores.
    """
    degree_score = 100 if "master" in content.lower() else 0
    title_score = 100 if job.job_title.lower() in content.lower() else 0
    return degree_score, title_score


def calculate_overall_score(hard, soft, keywords, degree, title):
    """
    Calculate overall match score based on weighted averages.
    """
    return round((hard * 0.4) + (soft * 0.2) + (keywords * 0.2) + (degree * 0.1) + (title * 0.1), 2)


def generate_title_degree_report(score, category):
    """
    Generate a report for the title or degree match.
    """
    return (
        f"Great work! The {category} matches your resume perfectly."
        if score == 100
        else f"Consider aligning your {category.lower()} with the job posting for a better match."
    )

