# AI-Resume-Builder
AI-Resume Builder



## Run the Tests
Execute the following command:

Test for utils functions:
```
python manage.py test resume_build.tests.test_calculate_skill_scores
python manage.py test resume_build.tests.test_calculate_category_match
python manage.py test resume_build.tests.test_extract_skills_from_text
python manage.py test resume_build.tests.test_calculate_title_degree_scores
python manage.py test resume_build.tests.test_generate_title_degree_report
```

Test for functions in view.py
```
python manage.py test resume_build.tests.test_match_score_page
python manage.py test resume_build.tests.test_fetch_resume_content
python manage.py test resume_build.tests.test_rewrite_resume
python manage.py test resume_build.tests.test_download_pdf

```
