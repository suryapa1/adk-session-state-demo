"""Shared schema for user profile data."""

from typing import List
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """User profile information schema."""
    
    user_id: str = Field(description="Unique user identifier")
    name: str = Field(description="Full name of the user")
    email: str = Field(description="Email address")
    role: str = Field(description="Job role/title")
    department: str = Field(description="Department name")
    skills: List[str] = Field(description="List of skills")
    projects: List[str] = Field(description="Current projects")
    status: str = Field(description="Account status (active/inactive)")
    joined_date: str = Field(description="Date joined (YYYY-MM-DD)")
    last_login: str = Field(description="Last login timestamp (ISO 8601)")
