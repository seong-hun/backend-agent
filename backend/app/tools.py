import os
from datetime import datetime, timedelta, timezone

import dotenv
import jwt
from langchain.tools import tool
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError


from app.sql_graph.graph import sql_graph

# --- Sql Tool


@tool(
    "call_sql_graph",
    description="""
    Send a user command in a natural language to the database,
    and request proper return values (i.e., user_id).
    """,
)
async def call_sql_graph(user_command: str):
    response = await sql_graph.ainvoke({"messages": [user_command]})
    return response["messages"][-1].content


# --- Password Hash Tool

password_hash = PasswordHash.recommended()


@tool(
    description="""
    Verifies if a password matches a given hash.
    The hash must be obtained from the database using username before calling this tool.
    """
)
def verify_password(password: str, hash: str) -> str:
    try:
        rv = password_hash.verify(password, hash)
        if rv:
            return "Password verified"
        else:
            return "Invalid password"
    except UnknownHashError:
        return "Invalid hash"


@tool(
    description="Hashes a password. The user password must be hashed before saved in a database."
)
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# --- JWT Tools


class JwtManager:
    def __init__(self):
        dotenv.load_dotenv()
        self.secret_key = os.getenv("JWT_SECRET_KEY", "my_secret_key")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.expires_delta = timedelta(
            minutes=int(os.getenv("JTW_ACCESS_TOKEN_EXPIRE_MINUTES", 15))
        )

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        expires_delta = expires_delta or self.expires_delta
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def check_signature(self, access_token: str):
        try:
            payload = jwt.decode(
                access_token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            return payload
        except jwt.exceptions.InvalidTokenError:
            return


jwt_manager = JwtManager()


@tool(
    description="""
    Create a JWT access token using the given user_id.
    This tool should only be used when a user login.
    """,
)
def create_jwt(user_id: str):
    access_token = jwt_manager.create_access_token(data={"sub": user_id})
    return access_token


@tool(
    description="""
    Check the signature of the given JWT access token.
    Return the payload if it is valid, otherwise return None.
    This tool should be used to check the user login session.
    """
)
def check_jwt(access_token: str) -> str | None:
    return jwt_manager.check_signature(access_token)


handler_tools = [call_sql_graph, hash_password, verify_password, create_jwt, check_jwt]
