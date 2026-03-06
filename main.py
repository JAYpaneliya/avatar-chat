from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel

from db import init_db
from models import AvatarCreate, ChatRequest, ChatResponse
from avatar import create_avatar, get_avatars_by_user, get_avatar_by_id, delete_avatar
from chat import chat_with_avatar, analyse_chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Avatar Chat API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Serve UI ──────────────────────────────────────────────────────────
@app.get("/")
def serve_ui():
    return FileResponse("trial_ui.html")


# ── Avatar Endpoints ──────────────────────────────────────────────────
@app.post("/avatars")
def create_new_avatar(data: AvatarCreate, x_user_id: str = Header(...)):
    avatar = create_avatar(user_id=x_user_id, data=data)
    return {"success": True, "avatar": avatar}


@app.get("/avatars")
def list_avatars(x_user_id: str = Header(...)):
    avatars = get_avatars_by_user(user_id=x_user_id)
    return {"avatars": avatars}


@app.get("/avatars/{avatar_id}")
def get_avatar(avatar_id: int, x_user_id: str = Header(...)):
    avatar = get_avatar_by_id(avatar_id)
    if not avatar or avatar["user_id"] != x_user_id:
        raise HTTPException(status_code=404, detail="Avatar not found.")
    return {"avatar": avatar}


@app.delete("/avatars/{avatar_id}")
def remove_avatar(avatar_id: int, x_user_id: str = Header(...)):
    deleted = delete_avatar(avatar_id=avatar_id, user_id=x_user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Avatar not found.")
    return {"success": True}


# ── Chat Endpoints ────────────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
def send_message(data: ChatRequest):
    try:
        result = chat_with_avatar(
            user_id=data.user_id,
            avatar_id=data.avatar_id,
            user_message=data.message
        )
        return ChatResponse(reply=result["reply"], avatar_name=result["avatar_name"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


# ── Analysis Endpoint ─────────────────────────────────────────────────
class AnalyseRequest(BaseModel):
    user_id: str
    avatar_id: int


@app.post("/analyse")
def end_and_analyse(data: AnalyseRequest):
    try:
        result = analyse_chat(user_id=data.user_id, avatar_id=data.avatar_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


# ── Health ────────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "avatar-chat-api"}