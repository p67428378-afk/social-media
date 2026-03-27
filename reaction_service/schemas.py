from pydantic import BaseModel, Field
from typing import Literal

class ReactionRequest(BaseModel):
    user_id: str = Field(..., description="The ID of the user performing the reaction.")
    reaction_type: Literal["like", "dislike"] = Field(..., description="The type of reaction: 'like' or 'dislike'.")

class ReactionRemoveRequest(BaseModel):
    user_id: str = Field(..., description="The ID of the user whose reaction is to be removed.")

class ReactionResponse(BaseModel):
    reaction_id: str
    user_id: str
    comment_id: str
    reaction_type: Literal["like", "dislike"]
    created_at: str
    updated_at: str

class ReactionCountsResponse(BaseModel):
    comment_id: str
    likes: int
    dislikes: int
