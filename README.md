# Stargazer API

A simple FastAPI web service that finds "neighbours" for a given GitHub repository.

[![CI](https://github.com/stephanlascar/stargazer/actions/workflows/ci.yml/badge.svg)](https://github.com/stephanlascar/stargazer/actions/workflows/ci.yml)

---

## 📖 Project Overview

This project exposes an endpoint:

```
GET /repos/<owner>/<repo>/starneighbours
```

It returns a list of repositories that share at least one stargazer with the given repository, along with the list of common stargazers.
This leverages the GitHub REST API to fetch and process stargazer data.

Authentication support is provided via API key (token) in the `Authorization` header.

---

## 🚀 Features

- **REST API** with FastAPI
- **Service Layer** for business logic
- **Client abstraction** for GitHub API communication
- **Authentication** via API token
- **TDD-first**: Unit tests with pytest
- **Dockerized** for easy setup
- **Interactive API docs available at [`/docs`](http://localhost:8000/docs)**
- ⚠️ **Pagination Limitation:** *For performance reasons, GitHub API pagination is limited to a maximum of 5 pages per request in this implementation (i.e., up to 500 results per query). This limit applies to both stargazer and starred repositories fetches.*

---

## 🏃‍♂️ Running the Project Locally (with Poetry)

### 1. Clone the repository

```sh
git clone https://github.com/slascar/gitbros.git
cd gitbros
```

### 2. Install Poetry

If you don't have Poetry installed:
```sh
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. Install dependencies

```sh
poetry install
```

### 4. Set environment variables

Create a `.env` file or export the following variables:

- `GITHUB_TOKEN`: (optional, for authenticated GitHub API requests — increases rate limits)
- `TOKEN`: API key required to access endpoints (e.g. `supersecret`)

### 5. Run the API

```sh
poetry run uvicorn app.main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000)

---

## 🐳 Running with Docker

### 1. Build the Docker image

```sh
docker build -t gitbros .
```

### 2. Run the container

```sh
docker run -p 8000:8000 gitbros
```

The API will be available at [http://localhost:8000](http://localhost:8000)

---

## 🧪 Running the Test Suite

```sh
poetry run pytest
```

---

## 🔐 Authentication

All endpoints require an API token to be passed in the `Authorization` header:

```
Authorization: Bearer <API_TOKEN>
```

If the token is missing or invalid, a 401 Unauthorized is returned.

---

## 📝 API Usage Example

```
GET /repos/stephanlascar/gitbros/starneighbours
Authorization: Bearer supersecret
```

**Response:**
```json
[
  {
    "repo": "octocat/hello-world",
    "stargazers": ["alice", "bob"]
  },
  {
    "repo": "mergifyio/mergify-engine",
    "stargazers": ["alice"]
  }
]
```

---

## 🛠️ Potential Improvements

- **Implement a background task scheduler**: Add a mechanism to periodically or asynchronously launch background jobs for fetching and updating neighbours, making use of a scheduler (such as [APScheduler](https://apscheduler.readthedocs.io/) or [Celery Beat](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html)). This would offload expensive computations from the API endpoints and allow clients to retrieve precomputed results, improving scalability, performance, and user experience.
- Expose more filters (e.g., min common stargazers)
- Add request throttling and rate limiting for API users
