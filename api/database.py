from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv
import threading

load_dotenv()

URL   = os.getenv("TURSO_URL")          # Debe ser solo el host, p.ej. "vencimiento-adibattista.turso.io"
TOKEN = os.getenv("TURSO_AUTH_TOKEN")

print(f"create_engine: {URL=}{TOKEN=}")

engine = create_engine(f"sqlite+libsql://{URL}?authToken={TOKEN}", 
                       echo=True, connect_args={"check_same_thread": False})

db_lock = threading.Lock()

def get_session():
    """
    Genera una nueva sesión de base de datos.

    :yield: Sesión de SQLModel.
    """
    with db_lock:
        with Session(engine) as session:
            yield session