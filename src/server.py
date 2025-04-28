import json
import os
import traceback
from typing import Optional
from uuid import UUID
from uuid import uuid4
import tempfile
from asyncio import Queue
from functools import partial

from concurrent.futures import ThreadPoolExecutor

from fastapi import Depends
from fastapi import FastAPI, Response, WebSocket, Body
# from fastapi import  BackgroundTasks
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from fastapi_sessions.session_verifier import SessionVerifier
from pydantic import BaseModel, Field
from typing import List
from json_file_session_backend import JsonFileMemoryBackend
from download_lyrics import search_genius_url, download_lyrics
from create_karaoke import STEPS, generate_karaoke
import base64
import re
from directories import data_dir, media_dir, webapp_dir

from progress_notifier import WebSocketProgressNotifier
from guess_lyrics_language import supported_languages, guess_language
from start_segments_adjustment import start_segments_adjustment

generate_executor = ThreadPoolExecutor(max_workers=1)

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

from get_or_create_karaoke_project_data import slugify_karaoke
import threading

karaokes_lock = threading.Lock()
karaoke_locks = {}

websockets = {}

@api.post("/create-karaoke", dependencies=[Depends(cookie)], response_model=SessionData)
async def create_karaoke(new_karaoke: NewKaraoke, session_data: SessionData = Depends(verifier), session_id: UUID = Depends(cookie)):
    with karaokes_lock:
        karaokes_json = f'{data_dir}/karaokes.json'
        if not os.path.exists(karaokes_json):
            with open(karaokes_json, mode='w') as fp:
                fp.write('{}')
        with open(karaokes_json, mode='r') as fp:
            karaokes = json.load(fp)
        slug = slugify_karaoke(new_karaoke.artist, new_karaoke.title)
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


@api.post("/open-karaoke", dependencies=[Depends(cookie)], response_model=SessionData)
async def open_karaoke(project_name: str, session_data: SessionData = Depends(verifier), session_id: UUID = Depends(cookie)):
    with karaokes_lock:
        karaokes_json = f'{data_dir}/karaokes.json'
        if not os.path.exists(karaokes_json):
            with open(karaokes_json, mode='w') as fp:
                fp.write('{}')
        with open(karaokes_json, mode='r') as fp:
            karaokes = json.load(fp)
        if project_name not in karaokes:
            raise HTTPException(400, "no such karaoke")

        session_data.project_name = project_name
        await backend.update(session_id, session_data)
        return session_data



class SimpleKaraoke(BaseModel):
    project_name: str
    artist: str
    title: str

class KaraokePatch(BaseModel):
    artist: Optional[str] = Field(None)
    title: Optional[str] = Field(None)
    youtube_url: Optional[str] = Field(None)
    genius_url: Optional[str] = Field(None)
    lyrics: Optional[str] = Field(None)
    language: Optional[str] = Field(None)
    alignment_correction: Optional[bool] = Field(None)


@api.get("/languages", response_model=List[str])
async def get_languages():
    return supported_languages

class KaraokeData(KaraokePatch):
    audio_mp3: Optional[str] = Field(None)
    audio_wav: Optional[str] = Field(None)
    accompaniment_mp3: Optional[str] = Field(None)
    accompaniment_wav: Optional[str] = Field(None)
    vocals_mp3: Optional[str] = Field(None)
    vocals_wav: Optional[str] = Field(None)
    video_mp4: Optional[str] = Field(None)
    video_accompaniment_mp4: Optional[str] = Field(None)
    subtitles_segments_ass: Optional[str] = Field(None)
    subtitles_words_ass: Optional[str] = Field(None)
    subtitles_words_karaoke_ass: Optional[str] = Field(None)
    karaoke_video_mp4: Optional[str] = Field(None)
    karaoke_subtitles_ass: Optional[str] = Field(None)
    lyrics_video_mp4: Optional[str] = Field(None)
    lyrics_subtitles_ass: Optional[str] = Field(None)
    alignment_correction: Optional[bool] = Field(None)

from create_media_links import karaoke_video_file, karaoke_subtitles_file, lyrics_video_file, lyrics_subtitles_file

@api.get("/karaoke/{project_name}", response_model=KaraokeData)
async def get_karaoke(project_name: str):
    with karaoke_lock(project_name):
        project_dir = f'{data_dir}/{project_name}'
        data_json = f'{project_dir}/_data.json'
        with open(data_json, mode='r') as fp:
            project_data = json.load(fp)
        for key, file in [("lyrics", "lyrics.txt")]:
            if os.path.exists(f'{project_dir}/{file}'):
                with open(f'{project_dir}/{file}', mode='r') as fp:
                    project_data[key] = fp.read()
        for key, file in [
            *[(f"{name.replace('-', '_')}_mp3", f"{name}.mp3") for name in ["accompaniment", "audio", "vocals"] ],
            *[(f"{name.replace('-', '_')}_wav", f"{name}.wav") for name in ["accompaniment", "audio", "vocals"] ],
            *[(f"{name.replace('-', '_')}_mp4", f"{name}.mp4") for name in ["video", "video-accompaniment"] ],
            *[(f"{name.replace('-', '_')}_ass", f"{name}.ass") for name in ["subtitles-segments", "subtitles-words", "subtitles-words-karaoke"] ],
        ]:
            if os.path.exists(f'{project_dir}/{file}'):
                project_data[key] = f'/data/{project_name}/{file}'

        for key, file in [
            *[(f"{name.replace('-', '_')}_mp4", f"{file_supplier(project_data)}") for name, file_supplier in [ ("karaoke-video", karaoke_video_file), ("lyrics-video", lyrics_video_file)] ],
            *[(f"{name.replace('-', '_')}_ass", f"{file_supplier(project_data)}") for name, file_supplier in [ ("karaoke-subtitles", karaoke_subtitles_file), ("lyrics-subtitles", lyrics_subtitles_file)] ],
        ]:
            if os.path.exists(f'{media_dir}/{file}'):
                print(f'{key}=/media/{file}')
                project_data[key] = f'/media/{file}'
        return project_data

@api.patch("/karaoke/{project_name}", response_model=KaraokeData)
async def patch_karaoke(project_name: str, patch: KaraokePatch):
    with karaoke_lock(project_name):
        project_data = await read_karaoke_data(project_name)
        project_dir = f'{data_dir}/{project_name}'
        for key, value in patch.model_dump().items():
            if value is not None:
                if key == "lyrics":
                    with open(f'{project_dir}/{key}.txt', mode='w') as fp:
                        fp.write(value)
                else:
                    project_data[key] = value
        await write_karaoke_data(project_name, project_data)
        return project_data



@app.websocket("/ws/{context}")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    context = websocket.url.path.split('/')[-1]
    session_id = websocket.cookies[cookie_name]
    [ base64_real_session_id, *_ ] = str(session_id).split('.')
    real_session_id = decode_base64(base64_real_session_id)[1:-1]
    real_session_id = str(UUID(real_session_id))
    queue = Queue()
    websockets[f'{real_session_id}-{context}'] = (websocket, queue)
    # websockets[f'{real_session_id}-{context}'] = websocket
    print(f"websocket: session_id {real_session_id} and context {context} associated to websocket {websocket} and queue {queue}")
    while True:
        try:
            item = await queue.get()
            if "close" in item:
                break
            # await websocket.send_json({'ping': True})
            await websocket.send_json(item)
        except:
            traceback.format_exc()
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

def hello():
    print("------ hello")

@api.post("/_guess_language", response_model=KaraokePatch)
async def gen_karaoke(lyrics: str = Body(..., media_type='text/plain')):
    try:
        language = guess_language(lyrics)
        return KaraokePatch(language=language)
    except:
        print(traceback.format_exc())
        return KaraokePatch(language=None)

@api.get("/karaokes", response_model=List[SimpleKaraoke])
async def gen_karaokes():
    try:
        with open(f'{data_dir}/karaokes.json', mode="r") as fp:
            karaokes = json.load(fp)
        return [ {'project_name': key, 'title': value['title'], 'artist': value['artist']} for key, value in karaokes.items() ]
    except:
        print(traceback.format_exc())
        return KaraokePatch(language=None)

@api.post("/karaoke/{project_name}/_generate", dependencies=[Depends(cookie)])
async def gen_karaoke(
        project_name: str,
        # background_tasks: BackgroundTasks,
        session_id: UUID = Depends(cookie)
):
    project_dir = f'{data_dir}/{project_name}'
    real_session_id = str(session_id)
    context = "generate"
    print(f"sending progress notifications to websocket associated to {real_session_id} and context {context}")
    (websocket, queue) = websockets[f'{real_session_id}-{context}']
    print(f"websocket: {websocket}")
    print(f"queue: {queue}")
    progress = WebSocketProgressNotifier(STEPS, websocket, queue)
    # progress.notify("Hello")
    await websocket.send_json({
        'step': 10,
        'steps': 20,
        'message': "hello",
    })
    # background_tasks.add_task(hello)
    # background_tasks.add_task(generate_karaoke, project_dir, progress, False)
    generate_executor.submit(generate_karaoke, project_dir, progress, False)


class SegmentAdjustment(BaseModel):
    id: str
    start: float
    end: float
    text: str
    validated: bool

class SegmentValidation(BaseModel):
    id: str
    start: float
    end: float

class SegmentsAdjustment(BaseModel):
    segments: List[SegmentAdjustment]

# class NonSilenceSegment(BaseModel):
#     start: float
#     end: float
#
# class NonSilenceSegments(BaseModel):
#     segments: List[NonSilenceSegment] = Field(None)

class SilenceBoundaries(BaseModel):
    boundaries: List[float]


@api.post("/karaoke/{project_name}/_start_segments_adjustment", response_model=SegmentsAdjustment)
async def gen_segments_adjustment(
        project_name: str,
):
    project_dir = f'{data_dir}/{project_name}'
    segments_adjustment = start_segments_adjustment(f'{project_dir}/transcript.json')
    with open(segments_adjustment, mode="r") as fp:
        return json.load(fp)


@api.get("/karaoke/{project_name}/segments-adjustment", response_model=SegmentsAdjustment)
async def get_segments_adjustment(
        project_name: str,
):
    segments_adjustment = f'{data_dir}/{project_name}/transcript-fixed.json'
    with open(segments_adjustment, mode="r") as fp:
        return json.load(fp)


@api.post("/karaoke/{project_name}/_validate_segment")
async def adjust_segment(
        project_name: str,
        validation: SegmentValidation,
        response: Response,
):
    segments_adjustment = f'{data_dir}/{project_name}/transcript-fixed.json'
    with open(segments_adjustment, mode="r") as fp:
        transcript = json.load(fp)
    found = False
    for segment in transcript["segments"]:
        if segment["id"] == validation.id:
            segment["start"] = validation.start
            segment["end"] = validation.end
            segment["validated"] = True
            found = True
            break
    if not found:
        response.status_code = 400
    else:
        with open(segments_adjustment, mode="w") as fp:
            json.dump(transcript, fp, indent=4)
        response.status_code = 204

@api.get("/karaoke/{project_name}/silence-boundaries", response_model=SilenceBoundaries)
async def get_silence_boundaries(
        project_name: str,
):
    split_summary_json = f'{data_dir}/{project_name}/split-summary.json'
    with open(split_summary_json, mode="r") as fp:
        split_summary = json.load(fp)
    total_start = split_summary['total']['start']
    total_end = split_summary['total']['end']

    silence_boundaries = []
    segment_end = -1
    for index, segment in enumerate(split_summary['segments']):
        segment_start = segment['start']
        segment_end = segment['end']
        if index == 0 and total_start < segment_start:
            silence_boundaries.append(total_start)
        silence_boundaries.append(segment_start)
        silence_boundaries.append(segment_end)

    if segment_end == -1 or segment_end < total_end:
        silence_boundaries.append(total_end)

    return {"boundaries": silence_boundaries}

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

app.mount("/data", StaticFiles(directory=data_dir), name="data")
app.mount("/media", StaticFiles(directory=media_dir, follow_symlink=True), name="media")
app.mount("/", StaticFiles(directory=webapp_dir, html=True), name="webapp")


