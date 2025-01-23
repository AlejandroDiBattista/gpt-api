from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

URL   = os.getenv("TURSO_URL")          # Debe ser solo el host, p.ej. "vencimiento-adibattista.turso.io"
TOKEN = os.getenv("TURSO_AUTH_TOKEN")

print(f"URL: {URL}")
print(f"TOKEN: {TOKEN}")

# URL='sqlite+libsql://vencimiento-adibattista.turso.io'
# TOKEN='eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3Mzc1MDExMjEsImlkIjoiMDA2MjQxMjAtODk2YS00MDllLWE4MDUtYmNlZjVkYThhNTcxIn0.e-1OWld33Mx_PMHKf-eEdj8GpQE5PKIw1aSSCvuhYdCmS3Np8IpajawWaKoWF6pAxZO2JciOkHYEgij_drwUCw'
engine = create_engine(f"{URL}?authToken={TOKEN}", echo=True)

def get_session():
    with Session(engine) as session:
        yield session