import base64
import json
import os
from typing import Union, Optional
from uuid import UUID
from uuid import uuid4
import tempfile

import asyncio

from fastapi import Depends
from fastapi import FastAPI, Response, WebSocket
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from fastapi_sessions.session_verifier import SessionVerifier
from pydantic import BaseModel, Field
from json_file_session_backend import JsonFileMemoryBackend
from download_lyrics import search_genius_url, download_lyrics

import base64
import re

def decode_base64(string, altchars=b'+/'):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    data = string.encode('ascii')
    data = re.sub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', data)  # normalize
    missing_padding = len(data) % 4
    if missing_padding:
        data += b'='* (4 - missing_padding)
    result = base64.b64decode(data, altchars)
    return result.decode('ascii')

data_dir = os.environ["DATA_DIR"] if "DATA_DIR" in os.environ else f'{os.path.dirname(__file__)}/../data'

class SessionData(BaseModel):
    project_name: Optional[str] = Field(None)


backend = JsonFileMemoryBackend[UUID, SessionData](f"{data_dir}/sessions.json", SessionData)
cookie_params = CookieParameters()

cookie_name = "karaoke-session"
# Uses UUID
cookie = SessionCookie(
    cookie_name=cookie_name,
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)


class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True


verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)

app = FastAPI()
api = FastAPI()


@api.get("/check-session", dependencies=[Depends(cookie)], response_model=SessionData)
async def whoami(session_data: SessionData = Depends(verifier)):
    return session_data

@api.get("/create-session", response_model=SessionData)
async def create_session(response: Response):
    session = uuid4()
    data = SessionData(project_name=None)

    await backend.create(session, data)
    cookie.attach_to_response(response, session)
    return data

@api.get("/delete-session")
async def del_session(response: Response, session_id: UUID = Depends(cookie)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    response.status_code = 204


class NewKaraoke(BaseModel):
    artist: str
    title: str

from get_or_create_karaoke_project_data import slugify
import threading

karaokes_lock = threading.Lock()
karaoke_locks = {}

websockets = {}

@api.post("/create-karaoke", dependencies=[Depends(cookie)], response_model=SessionData)
async def create_karaoke(new_karaoke: NewKaraoke, session_data: SessionData = Depends(verifier), session_id: UUID = Depends(cookie)):
    karaokes_json = f'{data_dir}/karaokes.json'
    if not os.path.exists(karaokes_json):
        with open(karaokes_json, mode='w') as fp:
            fp.write('{}')
    with karaokes_lock:
        with open(karaokes_json, mode='r') as fp:
            karaokes = json.load(fp)
        slug = slugify(f'{new_karaoke.artist} {new_karaoke.title}')
        if slug in karaokes:
            raise HTTPException(400, "already exists")

        karaoke_data = new_karaoke.model_dump()
        karaokes[slug] = karaoke_data
        with open(karaokes_json, mode='w') as fp:
            json.dump(karaokes, fp, indent=4)

        await write_karaoke_data(slug, karaoke_data)
        session_data.project_name = slug
        await backend.update(session_id, session_data)
        return session_data



class KaraokePatch(BaseModel):
    artist: Optional[str] = Field(None)
    title: Optional[str] = Field(None)
    youtube_url: Optional[str] = Field(None)
    genius_url: Optional[str] = Field(None)
    lyrics: Optional[str] = Field(None)


class KaraokeData(KaraokePatch):
    pass

@api.get("/karaoke/{project_name}", response_model=KaraokeData)
async def get_karaoke(project_name: str):
    with karaoke_lock(project_name):
        project_dir = f'{data_dir}/{project_name}'
        data_json = f'{project_dir}/_data.json'
        with open(data_json, mode='r') as fp:
            data = json.load(fp)
        return data

@api.patch("/karaoke/{project_name}", response_model=KaraokeData)
async def patch_karaoke(project_name: str, patch: KaraokePatch):
    with karaoke_lock(project_name):
        print(patch.model_dump())
        data = await read_karaoke_data(project_name)
        for key, value in patch.model_dump().items():
            if value is not None:
                data[key] = value
        print(data)
        await write_karaoke_data(project_name, data)
        return data



# @app.websocket("/ws", dependencies=[Depends(cookie)])
@app.websocket("/ws/{context}")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    context = websocket.url.path.split('/')[-1]
    session_id = websocket.cookies[cookie_name]
    [ base64_real_session_id, *_ ] = str(session_id).split('.')
    real_session_id = decode_base64(base64_real_session_id)[1:-1]
    real_session_id = str(UUID(real_session_id))
    websockets[f'{real_session_id}-{context}'] = websocket
    print(f"websocket: session_id {real_session_id} and context {context} associated to websocket {websocket}")
    while True:
        await asyncio.sleep(10)
        try:
            await websocket.send_json({'ping': True})
        except:
            pass

class SearchLyrics(BaseModel):
    artist: str
    title: str

class GeniusURL(BaseModel):
    url: str

class GeniusLyrics(BaseModel):
    lyrics: str

@api.post("/search-genius-lyrics", response_model=GeniusURL)
async def search_genius_lyrics(search_lyrics: SearchLyrics):
    result = search_genius_url(search_lyrics.artist, search_lyrics.title)
    if result is None:
        raise HTTPException(400, "not found")
    return GeniusURL(url=result)

@api.post("/get-genius-lyrics", response_model=GeniusLyrics)
async def search_genius_lyrics(genius_lyrics: GeniusURL):
    with tempfile.TemporaryDirectory() as dir:
        result = download_lyrics(genius_lyrics.url, dir, force=True)
        with open(result, mode='r') as fp:
            lyrics = fp.read()
        return GeniusLyrics(lyrics=lyrics)


@api.post("/karaoke/{project_name}/_generate", dependencies=[Depends(cookie)])
async def generate_karaoke(project_name: str, session_id: UUID = Depends(cookie)):
    print("str(session_id)")
    real_session_id = str(session_id)
    context = "create"
    print(f"sending to websocket associated to {real_session_id} and context {context}")
    websocket = websockets[f'{real_session_id}-{context}']
    await websocket.send_json({"project_name": project_name})

async def read_karaoke_data(project_name):
    project_dir = f'{data_dir}/{project_name}'
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
    data_json = f'{project_dir}/_data.json'
    with open(data_json, mode='r') as fp:
        data = json.load(fp)
    return data


async def write_karaoke_data(project_name, data):
    project_dir = f'{data_dir}/{project_name}'
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
    data_json = f'{project_dir}/_data.json'
    with open(data_json, mode='w') as fp:
        json.dump(data, fp, indent=4)


def karaoke_lock(project_name: str) -> threading.Lock:
    with karaokes_lock:
        lock = karaoke_locks.get(project_name)
        if not lock:
            lock = threading.Lock()
            karaoke_locks[project_name] = lock
        return lock


app.mount("/api", api)

app.mount("/static", StaticFiles(directory="output"), name="static")


