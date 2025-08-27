from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import get_tenant_db
from app.crud import crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_tenant_db)):
    from jose import jwt, JWTError
    from app.core.config import SECRET_KEY, ALGORITHM
    from app.schemas.schemas import TokenData
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario = payload.get("sub")
        if usuario is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        token_data = TokenData(usuario=usuario)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user = crud.get_usuario_by_usuario(db, token_data.usuario)
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    return user
