from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
from app.database import get_db
from app.auth.jwt import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_token, get_current_user,
)
from app.models.user import UserCreate, UserLogin, UserUpdate, UserResponse
from app.utils.helpers import serialize_doc

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    db = get_db()
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = {
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "display_name": user_data.display_name,
        "saved_gyms": [],
        "wearable_connections": {},
        "preferences": {"units": "imperial", "default_gym_id": None, "notifications_enabled": True},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    return {
        "access_token": create_access_token(user_id),
        "refresh_token": create_refresh_token(user_id),
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": user_data.email,
            "display_name": user_data.display_name,
        },
    }


@router.post("/login")
async def login(credentials: UserLogin):
    db = get_db()
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user["_id"])
    return {
        "access_token": create_access_token(user_id),
        "refresh_token": create_refresh_token(user_id),
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": user["email"],
            "display_name": user["display_name"],
        },
    }


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload.get("sub")
    return {
        "access_token": create_access_token(user_id),
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["_id"],
        email=current_user["email"],
        display_name=current_user["display_name"],
        saved_gyms=current_user.get("saved_gyms", []),
        wearable_connections=current_user.get("wearable_connections", {}),
        preferences=current_user.get("preferences", {}),
        created_at=current_user["created_at"],
    )


@router.put("/me")
async def update_me(update_data: UserUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    update_fields = {}
    if update_data.display_name is not None:
        update_fields["display_name"] = update_data.display_name
    if update_data.preferences is not None:
        update_fields["preferences"] = update_data.preferences.model_dump()

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_fields["updated_at"] = datetime.utcnow()
    await db.users.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": update_fields},
    )
    return {"message": "Profile updated"}
