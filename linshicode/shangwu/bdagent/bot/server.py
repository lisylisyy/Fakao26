import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel  # noqa: E402

import storage  # noqa: E402
from bot import simulator  # noqa: E402

app = FastAPI(title="bdagent 训练台")

_STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

storage.init_db()


class NewSessionRequest(BaseModel):
    hint: str = ""


class MessageRequest(BaseModel):
    role: str
    text: str


class AiReplyRequest(BaseModel):
    role: str


@app.get("/")
def index():
    return FileResponse(_STATIC_DIR / "index.html")


@app.get("/api/sessions")
def api_list_sessions():
    return simulator.list_sessions()


@app.post("/api/sessions")
def api_new_session(req: NewSessionRequest):
    return simulator.new_session(hint=req.hint)


@app.get("/api/sessions/{session_id}")
def api_get_session(session_id: str):
    session = simulator.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    return session


@app.post("/api/sessions/{session_id}/end")
def api_end_session(session_id: str):
    simulator.end_session(session_id)
    return {"ok": True}


@app.post("/api/sessions/{session_id}/message")
def api_message(session_id: str, req: MessageRequest):
    try:
        return simulator.manual_message(session_id, req.role, req.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/sessions/{session_id}/ai_reply")
def api_ai_reply(session_id: str, req: AiReplyRequest):
    try:
        return simulator.ai_reply(session_id, req.role)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/sessions/{session_id}/auto_chat/start")
def api_auto_chat_start(session_id: str):
    try:
        return simulator.start_auto_chat(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/sessions/{session_id}/auto_chat/stop")
def api_auto_chat_stop(session_id: str):
    return simulator.stop_auto_chat(session_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8899)
