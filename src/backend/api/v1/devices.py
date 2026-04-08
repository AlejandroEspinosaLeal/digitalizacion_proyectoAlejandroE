from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from src.backend.api.deps import get_db, get_current_user
from src.backend.models.schema import Device, SortingRule, User

router = APIRouter()

@router.get("/sync/{device_id}", response_model=List[SortingRule])
async def sync_device_rules(
    device_id: str,
    db: Session = Depends(get_db)
):
    """
    Called by local Enterprise Agents upon initialization to dynamically download
    their specific authorized cloud Sorting Rules and extensions.
    """
    statement = select(SortingRule).where(
        SortingRule.device_id == device_id, 
        SortingRule.is_active == True
    )
    rules = db.exec(statement).all()
    
    # Update device heartbeat and online status in the cloud DB
    device = db.get(Device, device_id)
    if device:
        device.is_online = True
        device.last_sync = datetime.utcnow()
        db.add(device)
        db.commit()
        
    return rules

@router.post("/{device_id}/rules", response_model=SortingRule)
async def create_rule(
    device_id: str,
    rule_data: SortingRule,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Authenticated endpoint enabling remote Web Dashboards to securely inject 
    new automated behavioral rules into a specific target PC.
    """
    device = db.get(Device, device_id)
    if not device or device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this device")
    
    db.add(rule_data)
    db.commit()
    db.refresh(rule_data)
    return rule_data