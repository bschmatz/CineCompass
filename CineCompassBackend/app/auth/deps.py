from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.init_db import init_db
from app.auth.jwt_handler import JWTHandler
from app.models.user import User

jwt_handler = JWTHandler()

def get_db():
    engine, SessionLocal = init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Session = Depends(get_db),
    token_data: dict = Depends(jwt_handler.verify_token)
):
    user = db.query(User).filter(User.id == int(token_data.get("sub"))).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token for user")
    return user