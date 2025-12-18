from pydantic import BaseModel, Field


class ResponseBody(BaseModel):
    user_id: str = Field(description="The unique identifier of the registered user")
    access_token: str = Field(description="JWT Token of the user session")
    lab_id: str = Field(description="The unique identifier of the created Lab")
