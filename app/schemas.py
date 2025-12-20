from pydantic import BaseModel, Field


class UserCommand(BaseModel):
    user_command: str = Field(description="The api request in natural language")


class Plan(BaseModel):
    plan: str = Field(
        description="The backend procedure plan to accomplish the user request."
    )
    denied: bool = Field(
        description="True if the user request is not listed in the API examples"
    )
    denied_reason: str = Field(
        description="""
        Explain why the user request was deniend.
        If the requets was not denited, then it is an empty string
        """
    )


class ResponseBody(BaseModel):
    user_id: str = Field(description="The unique identifier of the registered user")
    access_token: str = Field(description="JWT Token of the user session")
    lab_id: str = Field(description="The unique identifier of the created Lab")
