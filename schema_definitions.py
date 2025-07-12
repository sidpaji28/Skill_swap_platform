from pydantic import BaseModel
from typing import List, Optional

class UserProfile(BaseModel):
    name: str
    email: str
    password: str  # 🔐 Added password field
    location: Optional[str] = None
    is_public: bool = True
    availability: Optional[str] = None
    skills_offered: List[str]
    skills_wanted: List[str]
    

class SwapRequest(BaseModel):
    from_user_id: str
    to_user_id: str
    skill_offered: str
    skill_requested: str
    status: Optional[str] = "pending"  # pending, accepted, rejected, cancelled

class FeedbackData(BaseModel):
    swap_id: str
    from_user_id: str
    to_user_id: str
    rating: int  # 1 to 5
    comment: Optional[str] = None
