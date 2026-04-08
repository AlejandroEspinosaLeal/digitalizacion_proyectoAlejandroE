from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, Session, create_all

class SubscriptionTier(str, Enum):
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class User(SQLModel, table=True):
    """Core PostgreSQL User entity storing encrypted passwords and Subscription status."""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    subscription_tier: SubscriptionTier = Field(default=SubscriptionTier.BASIC)
    devices: List["Device"] = Relationship(back_populates="owner")

class Device(SQLModel, table=True):
    """Maps to a physical Windows OS endpoint. Identified uniquely by an Agent-generated UUID."""
    id: str = Field(primary_key=True) # Unique Host UUID
    name: str
    user_id: int = Field(foreign_key="user.id")
    is_online: bool = Field(default=False)
    last_sync: datetime = Field(default_factory=datetime.utcnow)
    
    owner: User = Relationship(back_populates="devices")
    rules: List["SortingRule"] = Relationship(back_populates="device")

class SortingRule(SQLModel, table=True):
    """Relational table storing dynamic Cloud-Synched file extensions mapped to Target Folders."""
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: str = Field(foreign_key="device.id")
    name: str
    extension: str
    keyword: str
    target_folder: str
    is_active: bool = Field(default=True)
    
    device: Device = Relationship(back_populates="rules")

class FileEvent(SQLModel, table=True):
    """Immutable Audit Log trailing all file sorting operations successfully enacted by a Node."""
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: str = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    filename: str
    source_path: str
    dest_path: str
    status: str = "success"