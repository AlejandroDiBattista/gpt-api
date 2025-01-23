from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Session, select
from database import engine, get_session
from models import Vencimiento
from crud import * # Importar todas las funciones CRUD
from crud import crear_vencimiento

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if not session.exec(select(Vencimiento)).first():
            print("🚩 No hay vencimientos, creando ejemplos")
            ejemplos = [
                Vencimiento(fecha="2023-10-01", vencimiento="2023-10-31", descripcion="Ejemplo 1", deuda=100.0, pago=50.0, pagado=False, responsable="Responsable A"),
                Vencimiento(fecha="2023-10-02", vencimiento="2023-11-01", descripcion="Ejemplo 2", deuda=200.0, pago=150.0, pagado=False, responsable="Responsable B"),
                Vencimiento(fecha="2023-10-03", vencimiento="2023-11-02", descripcion="Ejemplo 3", deuda=300.0, pago=250.0, pagado=False, responsable="Responsable C"),
                Vencimiento(fecha="2023-10-04", vencimiento="2023-11-03", descripcion="Ejemplo 4", deuda=400.0, pago=350.0, pagado=False, responsable="Responsable D"),
                Vencimiento(fecha="2023-10-05", vencimiento="2023-11-04", descripcion="Ejemplo 5", deuda=500.0, pago=450.0, pagado=False, responsable="Responsable E"),
            ]
            for ejemplo in ejemplos:
                crear_vencimiento(session, ejemplo)
    yield
    
app = FastAPI(lifespan=lifespan)

@app.post("/vencimientos/", response_model=Vencimiento)
def create_new_vencimiento(vencimiento: Vencimiento, session=Depends(get_session)):
    return crear_vencimiento(session, vencimiento)

@app.get("/vencimientos/", response_model=list[Vencimiento])
def read_vencimientos(session=Depends(get_session)):
    return obtener_vencimientos(session)

@app.get("/vencimientos/{vencimiento_id}", response_model=Vencimiento)
async def read_vencimiento(vencimiento_id: int, session=Depends(get_session)):
    vencimiento = obtener_vencimiento_por_id(session, vencimiento_id)
    if not vencimiento:
        raise HTTPException(status_code=404, detail="Vencimiento no encontrado")
    return vencimiento

@app.patch("/vencimientos/{vencimiento_id}/cambiar_fecha", response_model=Vencimiento)
async def cambiar_fecha_vencimiento(vencimiento_id: int, fecha: str, session=Depends(get_session)):
    vencimiento = cambiar_fecha(session, vencimiento_id, fecha)
    if not vencimiento:
        raise HTTPException(status_code=404, detail="Vencimiento no encontrado")
    return vencimiento

@app.patch("/vencimientos/{vencimiento_id}/cambiar_responsable", response_model=Vencimiento)
async def cambiar_responsable_vencimiento(vencimiento_id: int, responsable: str, session=Depends(get_session)):
    vencimiento = cambiar_responsable(session, vencimiento_id, responsable)
    if not vencimiento:
        raise HTTPException(status_code=404, detail="Vencimiento no encontrado")
    return vencimiento

@app.patch("/vencimientos/{vencimiento_id}/cambiar_pago", response_model=Vencimiento)
async def cambiar_pago_vencimiento(vencimiento_id: int, monto: float = None, session=Depends(get_session)):
    vencimiento = cambiar_pago(session, vencimiento_id, monto)
    if not vencimiento:
        raise HTTPException(status_code=404, detail="Vencimiento no encontrado")
    return vencimiento

