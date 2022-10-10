from pydantic import BaseModel


class CheckUploadSecretKeySerializer(BaseModel):
    secret_key: str


class UpdateUploadStatusSerializer(BaseModel):
    secret_key: str
    download_url: str


class UpdateUploadStatusOutputSerializer(BaseModel):
    download_url: str
    updated_file: int
