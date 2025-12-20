import os
from datetime import datetime, timedelta, timezone

import dotenv
import jwt
from langchain.tools import tool
from pwdlib import PasswordHash

from app.sql_graph.graph import sql_graph

# --- Sql Tool


@tool(
    "call_sql_graph",
    description="""
    This tool can run a natural language command related to SQL.
    """,
)
def call_sql_graph(user_command: str):
    response = sql_graph.invoke({"user_command": user_command})
    return response["messages"][-1].content


# --- Password Hash Tool

password_hash = PasswordHash.recommended()


@tool(description="Verify password.")
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


@tool(
    description="Hash the password. The user password must be hashed before saved in a database."
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
            return True
        except jwt.exceptions.InvalidTokenError:
            return False


jwt_manager = JwtManager()


@tool(
    description="""
    Create a JWT access token using the given username.
    This tool should only be used when a user login.
    """,
)
def create_jwt(username: str):
    access_token = jwt_manager.create_access_token(data={"sub": username})
    return access_token


@tool(
    description="""
    Check the signature of the given JWT access token.
    Return True if it is valid, otherwise return False.
    This tool should be used to check the user login session.
    """
)
def check_jwt(access_token: str) -> bool:
    return jwt_manager.check_signature(access_token)


handler_tools = [call_sql_graph, hash_password, verify_password, create_jwt, check_jwt]
