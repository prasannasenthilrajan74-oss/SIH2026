from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from backend.app.core.config import settings
from backend.app.core.security import verify_password, create_access_token
from backend.app.db.session import get_db
from backend.app.models.models import User, Role
from backend.app.schemas.schemas import Token, UserResponse, LoginRequest
from typing import List

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/token", response_model=Token)
def login_for_access_token_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login_for_access_token_json(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        role_id=current_user.role_id,
        role_name=current_user.role.name,
        state=current_user.state,
        district=current_user.district,
        constituency=current_user.constituency
    )

@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = db.query(User).all()
    return [
        UserResponse(
            id=u.id,
            username=u.username,
            role_id=u.role_id,
            role_name=u.role.name,
            state=u.state,
            district=u.district,
            constituency=u.constituency
        ) for u in users
    ]

def apply_role_filters(query, model, user: User):
    if user.role.name == "State Nodal Authority":
        return query.filter(model.state_code == user.state)
    elif user.role.name == "District Authority":
        return query.filter(model.district_code == user.district)
    elif user.role.name == "MP / Constituency Viewer":
        return query.filter(model.constituency == user.constituency)
    return query

