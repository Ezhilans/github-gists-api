## :warning: Please read these instructions carefully and entirely first
* Clone this repository to your local machine.
* Use your IDE of choice to complete the assignment.
* When you have completed the assignment, you need to  push your code to this repository and [mark the assignment as completed by clicking here]({{submission_link}}).
* Once you mark it as completed, your access to this repository will be revoked. Please make sure that you have completed the assignment and pushed all code from your local machine to this repository before you click the link.

## Operability Take-Home Exercise

Welcome to the start of our recruitment process for Operability Engineers. It was great to speak to you regarding an opportunity to join the Equal Experts network!

Please write code to deliver a solution to the problems outlined below.

We appreciate that your time is valuable and do not expect this exercise to **take more than 90 minutes**. If you think this exercise will take longer than that, I **strongly** encourage you to please get in touch to ask any clarifying questions.

### Submission guidelines
**Do**
- Provide a README file in text or markdown format that documents a concise way to set up and run the provided solution.
- Take the time to read any applicable API or service docs, it may save you significant effort.
- Make your solution simple and clear. We aren't looking for overly complex ways to solve the problem since in our experience, simple and clear solutions to problems are generally the most maintainable and extensible solutions.

**Don't**

Expect the reviewer to dedicate a machine to review the test by:

- Installing software globally that may conflict with system software
- Requiring changes to system-wide configurations
- Providing overly complex solutions that need to spin up a ton of unneeded supporting dependencies. We aspire to keep our dev experiences as simple as possible (but no simpler)!
- Include identifying information in your submission. We are endeavouring to make our review process anonymous to reduce bias.

### Exercise
If you have any questions on the below exercise, please do get in touch and we’ll answer as soon as possible.

#### Build an API, test it, and package it into a container
- Build a simple HTTP web server API in any general-purpose programming language[^1] that interacts with the GitHub API and responds to requests on `/<USER>` with a list of the user’s publicly available Gists[^2].
- Create an automated test to validate that your web server API works. An example user to use as test data is `octocat`.
- Package the web server API into a docker container that listens for requests on port `8080`. You do not need to publish the resulting container image in any container registry, but we are expecting the Dockerfile in the submission.
- The solution may optionally provide other functionality (e.g. pagination, caching) but the above **must** be implemented.

Best of luck,  
Equal Experts
__________________________________________
For example Go, Python or Ruby but not Bash or Powershell.  
 https://docs.github.com/en/rest/gists/gists?apiVersion=2022-11-28


---

## Solution:  GitHub Gist API - Operability Take-Home Assignment

This is a lightweight Flask API that returns public GitHub gists for a given username. It includes pagination, Redis caching, test coverage, and runs in Docker.

---

## Features

- REST API to fetch public GitHub gists: `GET /<username>`
- Pagination support via `?page=&per_page=`
- Redis caching (mocked in tests)
- Health check at `/healthz`
- Full automated tests with coverage
- Dockerized

---

## Setup & Run

### Option 1: Docker (Recommended)

```bash
docker build -t gist-flask-api .
docker run -p 8080:8080 gist-flask-api
```

Access via:  
http://localhost:8080/octocat

---

### Option 2: Run Locally (Python 3.10+)

```bash
git clone <repo-url>
cd <repo-folder>
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

## API Usage

- `GET /<username>` – Returns public gists for the GitHub user
- Optional query params:
  - `page` (default: 1)
  - `per_page` (default: 10, max: 100)
- `GET /healthz` – Health check endpoint

**Example:**

```bash
curl http://localhost:8080/octocat?page=2&per_page=5
```

---

## Run Tests

```bash
pytest --cov=app --cov-report=html tests/
```

View test coverage:  
Open `htmlcov/index.html` in your browser.

---

## Project Structure

```
.
├── app.py             # Flask app with Redis + GitHub API logic
├── Dockerfile         # Multi-stage Dockerfile
├── requirements.txt   # Dependencies
├── tests/
│   └── test_app.py    # Unit tests
└── README.md          # This file
```

---

## Notes for Review

- No global installs or system config changes required
- Redis is optional and mocked during testing
- All tests are self-contained and reproducible
- Code is simple, readable, and extensible

---

## Thank You!

Looking forward to hearing from you!