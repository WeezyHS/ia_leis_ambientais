from pydantic import BaseModel

class QueryRequest(BaseModel):
    texto: str
