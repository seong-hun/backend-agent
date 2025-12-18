# AI Backend Agent

## Installation

It is recommended to create a virtual environment using `uv`.

First, clone the repository.

```bash
git clone https://github.com/seong-hun/backend-agent.git
cd backend-agent
```

Now, run sync to install packages into `.venv`.

```bash
uv sync
```

## Usage

First, run a FastAPI server.

```bash
uv run fastapi dev main.py
```

Then, send **ANY** requests to the server!

For example:

```bash
curl --location 'http://localhost:8000/register' \
--header 'Content-Type: application/json' \
--data '{
    "username": "myname",
    "password": "mypass"
}'
```

Note that we don't have any tables but also any databases!

The AI Backed Agent tries to figure out the intend of the request
and executes proper procedures to complete the request.
