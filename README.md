# AI Resume Builder

## How to run the application

Here are the instructions on how to install and run this application locally:

* Clone this repository. Instructions on how to clone a repository can be found <a href="https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository">here.</a>

* Create and activate a virtual environment:

<code>python -m venv venv</code>

<code>.\venv\Scripts\activate</code>

* Install the dependencies:

<code>pip install -r requirements.txt</code>

* Go to the views.py file in the resume_build folder and enter your Nebius API key in the first line by replacing ENTER_YOUR_API_KEY_HERE.
  
* Run database migrations:

<code>python manage.py migrate</code>

* Run the server:

<code>python manage.py runserver</code>

* Go to http://127.0.0.1:8000/ to access the application.



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
