from pydantic import BaseModel, EmailStr

class ClienteCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
