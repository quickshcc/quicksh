from modules import html_deliver
from modules import transfers
from modules import ratelimit
from modules import timestamp
from modules.logs import Log
from modules import cleaner
from modules import errors

from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import dotenv
import os


MainLimiter = ratelimit.ClientRateLimiter("(root)", 500, 3, 180)
ApiLimiter = ratelimit.ClientRateLimiter("api/", 100, 5, 360)


api = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
api.mount('/web/static', StaticFiles(directory="./web/static", html=True), name="static")
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_error_response(message: str) -> JSONResponse:
    return JSONResponse({
        "status": False,
        "error": message
    }, 400)


@api.get("/")
@api.get("/{code}")
@MainLimiter.gate
async def home(request: Request, code: str = None) -> HTMLResponse:
    page = html_deliver.PageContent("main")
    return HTMLResponse(content=page.get())


@api.post("/api/transfer")
@ApiLimiter.gate
async def transfer(request: Request, file: UploadFile = File(...), expire: int = Form(...)) -> JSONResponse:
    result = transfers.SharedFile.create_shared_file(file, expire, request.client.host)
    if isinstance(result, errors.T_Error):
        Log.error(f"failed to transfer file: {result}")
        return build_error_response(result)

    return JSONResponse({
        "status": True,
        "code": result.code,
        "expire": timestamp.convert_to_readable(result.date_expire)
    }, 200)  



@api.get("/api/receive/{code}")
@ApiLimiter.gate
async def receive(code: int, request: Request) -> FileResponse:
    file = transfers.get_shared_file(code)
    if isinstance(file, errors.T_Error):
        return build_error_response(file)

    Log.info(f"Sharing file: {code}")
    return FileResponse(
        transfers.get_file_path(file),
        filename=file.name
    )
    
    
@api.delete("/api/delete/{code}")
@ApiLimiter.gate
async def delete(code: int, request: Request) -> JSONResponse:
    file = transfers.get_shared_file(code)
    if isinstance(file, errors.T_Error):
        return build_error_response(file)
    
    del_status = file.request_delete(request.client.host)
    if isinstance(del_status, errors.T_Error):
        return build_error_response(del_status)
    
    return JSONResponse({
        "status": True,
    }, 200)
    
    
@api.get("/api/owned-codes")
@ApiLimiter.gate
async def fetch_owned_codes(request: Request) -> JSONResponse:
    """
    response: {
        code1: {
            'file': str,
            'expire': str
        },
        code2: {...}
    }
    """
    codes = {}
    ip_addr = transfers.hash_ip(request.client.host)
    
    for model in transfers.transfers_db.get_all_models():
        if model.owner_ip == ip_addr:
            codes[model.code] = {
                "file": model.name,
                "expire": timestamp.convert_to_readable(model.date_expire)
            }
            
    return JSONResponse({
        "status": True,
        "response": codes
    }, 200)

    
if __name__ == "__main__":
    env_status = dotenv.load_dotenv(".env")
    if not env_status:
        raise EnvironmentError("No .env file found.")
    
    host = os.getenv("HOST") or "localhost"
    port = int(os.getenv("PORT")) or 80
    
    cleaner.Cleaner()
    
    uvicorn.run(api, host=host, port=port)

