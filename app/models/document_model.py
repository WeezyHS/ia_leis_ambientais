from pydantic import BaseModel
from typing import List

class ChunkedDocument(BaseModel):
    filename: str
    chunks: List[str]
