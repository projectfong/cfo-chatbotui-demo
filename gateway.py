#!/usr/bin/env python3
# -------------------------------------------------------
# gateway.py
# -------------------------------------------------------
# Purpose Summary:
#   - Minimal demo API for cfo-chatbotui public repo.
#   - Provides health check and a simple /api/chat echo endpoint.
#   - Does NOT call any private router/orchestration.
# Audit:
#   - All actions print ISO 8601 UTC timestamps.
#   - Fail-safe HTTPException on errors.
# -------------------------------------------------------

import os
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware

def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()

def _log(msg: str) -> None:
    print(f"[{_ts()}] {msg}")

BIND = os.getenv("CFO_GATEWAY_BIND", "0.0.0.0")
PORT = int(os.getenv("CFO_GATEWAY_PORT", "9000"))

app = FastAPI(title="cfo-chatbotui-gateway-demo", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/api/healthz")
def healthz() -> Dict[str, str]:
    _log("HEALTHZ ok")
    return {"status": "ok"}

@app.post("/api/chat")
def chat(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    try:
        text = str(payload.get("message", "")).strip()
        _log(f"CHAT recv bytes={len(text)}")
        if not text:
            raise HTTPException(status_code=400, detail="message required")
        return {"response": f"You said: {text}"}
    except HTTPException:
        raise
    except Exception as e:
        _log(f"CHAT error {e}")
        raise HTTPException(status_code=500, detail="internal error")

if __name__ == "__main__":
    import uvicorn
    _log(f"DEMO start bind={BIND} port={PORT}")
    uvicorn.run(app, host=BIND, port=PORT)

