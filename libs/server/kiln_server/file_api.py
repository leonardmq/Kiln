import hashlib
import logging
import os
import tempfile
import uuid
from asyncio import Lock

from fastapi import FastAPI, File, UploadFile
from kiln_ai.datamodel.file import File as KilnFile
from kiln_ai.datamodel.registry import project_from_id
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Lock to prevent overwriting via concurrent updates. We use a load/update/write pattern that is not atomic.
update_run_lock = Lock()


class FileUploadResponse(BaseModel):
    success: bool
    file_id: str


# TODO: wondering if this should be in server/kiln_server/ or in app/desktop/studio_server/
def connect_file_api(app: FastAPI):
    @app.post("/api/projects/{project_id}/files")
    async def file_upload(
        project_id: str,
        file: UploadFile = File(...),
    ) -> FileUploadResponse:
        project = project_from_id(project_id)
        file_name = file.filename if file.filename else "untitled"
        file_path = os.path.join(
            tempfile.gettempdir(),
            file_name,
        )
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # TODO: save the file to the project
        file_id = str(uuid.uuid4())
        file = KilnFile(
            id=file_id,
            name=file_name,
            name_original=file_name,
            hash=hashlib.sha256(content).hexdigest(),
            extension=file_name.split(".")[-1],
            mime_type=file.content_type,
            size=len(content),
            file_path=file_path,
            parent=project,
        )
        file.save_to_file()

        return FileUploadResponse(
            success=True,
            file_id=file_id,
        )
