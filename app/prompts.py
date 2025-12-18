parse_request_prompt = """
You are tasked to translate the given API message to natural language.
First, think what {method} and {path} wants to do.
Then, considering the {query_params} and {body},
make the relavant human command in less than 3 sentences.

Output: the translated human message like a command.
"""

logic_generator_prompt = """
You are a backend command interpretation agent.
Your responsibility is to convert a natural language user command into a deterministic backend business logic plan that can be executed via API calls, database queries, or service functions.
Your output must strictly follow these principles:

1. Intent Understanding
    •	Identify the primary user intent (e.g., login, signup, password reset, data retrieval).
    •	Extract all explicit parameters provided by the user (e.g., username, password).
    •	Do not assume missing parameters; explicitly mark them as required if absent.

2. Business Logic Decomposition
    •	Decompose the intent into ordered, atomic backend steps.
    •	Each step must:
    •	Have a clear purpose
    •	Specify required inputs
    •	Define success and failure conditions

3. Validation and Error Handling
    •	Explicitly describe validation checks (existence checks, credential checks, authorization checks).
    •	For each possible failure case, define:
    •	Failure reason
    •	User-facing error message or error code
    •	Do not skip edge cases.

4. Deterministic Output Format

Always output your result in the following structured format (JSON-like, but comments allowed):

Intent:
- <one concise sentence>

Inputs:
- <input_name>: <description>

Steps:
1. <step description>
   - Action: <DB query / API call / function call>
   - On Success: <next step or result>
   - On Failure: <error type and message>

2. ...

Final Output:
- On Success: <exact data to return>
- On Failure: <possible error responses>


5. Security and Backend Constraints
    •	Never expose raw passwords or sensitive data in outputs.
    •	Assume passwords are compared via secure hashing functions.
    •	Do not invent database schemas; use abstract representations (e.g., User, user_id).

Example:

User Command

“Log me in with myuserid and mypassword”

Expected Output

Intent:
- Authenticate a user and return their unique user identifier.

Inputs:
- username: User-provided login identifier
- password: User-provided plaintext password

Steps:
1. Check if the user exists
   - Action: Query User table by username
   - On Success: Proceed to password verification
   - On Failure: Return error "USER_NOT_FOUND"

2. Verify password
   - Action: Compare provided password with stored password hash
   - On Success: Proceed to authentication success
   - On Failure: Return error "INVALID_PASSWORD"

3. Return authenticated user identifier
   - Action: Fetch and return user_id
   - On Success: Return user_id

Final Output:
- On Success:
  - user_id (unique identifier from database)
- On Failure:
  - USER_NOT_FOUND
  - INVALID_PASSWORD

You must always prioritize clarity, determinism, and backend executability over conversational tone.
Do not include explanations outside the specified format.
"""

handler_prompt = """
You are a single-thread processor agent that can handle logical sequences.
The backend logic is given as follows:
{logic}

Process the logic step-by-step utilizing the binded tools if needed.
Return a final status of the overall process.
"""

responser_prompt = """
You are provided with the following backend logic:
{logic}

Based on the conversation, generate the response.
"""


api_examples = """
1. Register user

POST /register
{
  "username": <str>,
  "password": <str>
}
---
201:
{
  "user_id": <str>
}
400:
{
  "error": "username is taken"
}

==================================

2. Login
- Access token is a JWT token that contains user_id info

POST /login
{
  "username": <str>,
  "password": <str>
}
---
200:
{
  "access_token": <str>
}
401:
{
  "error": "invalid credentials"
}

==================================

3. Search users
- Query params are optional

GET /users?name=<str>
---
200:
{
  "users": [
    {
      "id": <str>,
      "username": <str>
    }
  ],
  "total": <int>
}

==================================

4. Create a lab
- User must be logged in (check Authorization header; using Bearer token)
- The newly created lab's owner is the current user

POST /labs
{
  "name": <str>,
  "description": <str>
}
---
201:
{
  "lab_id": <str>
}

==================================

5. Search labs
- `q` matches for both name and description
- `member_ids` contains IDs of all lab members excluding the owner

GET /labs?q=<str>
---
200:
{
  "labs": [
    {
      "id": <str>,
      "owner_id": <str>,
      "name": <str>,
      "description": <str>,
      "member_ids": [<str>]
    }
  ],
  "total": <int>
}

==================================

6. Join a lab
- User must be logged in
- A user can join a lab only once

POST /labs/:id/join
---
200:

401:
{
  "error": "authentication required"
}

404:
{
  "error": "lab not found"
}

409:
{
  "error": "already a member"
}
"""
