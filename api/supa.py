import os
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import (
    Depends, HTTPException,
    APIRouter
)
from gotrue import UserResponse
from typing import Annotated
from fastapi.security import (
    OAuth2PasswordBearer, 
    OAuth2PasswordRequestForm
)
from sqlmodel import create_engine, Session


app = APIRouter(
    prefix="/p",
    tags=["auth"],
)

load_dotenv(dotenv_path=".env.local")
url: str = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
connection_string: str = os.environ.get("SUPABASE_CONNECTION_STRING") 


# key: str = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supa: Client = create_client(url, key)

# oauth2_scheme dependancy
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = supa.auth.sign_in_with_password(
        {
            'email':form_data.username, 
            'password':form_data.password
        })
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user_dict.session.access_token, "token_type": "bearer"}


# fetch user from access_token dependancy
def auth_user(access_token: Annotated[str, Depends(oauth2_scheme)]) -> UserResponse|None:
    auth = supa.auth.get_user(access_token)
    supa.postgrest.auth(access_token)
    return auth.user
UserState = Annotated[UserResponse, Depends(auth_user)]


engine = create_engine(connection_string, echo=True)
def get_session(user: UserState):
    with Session(engine) as session:
        yield session
SupaSession = Annotated[Session, Depends(get_session)]


if __name__ == "__main__":
    from api.models import SQLModel, User
    from api.pretty import i
    SQLModel.metadata.create_all(engine)    