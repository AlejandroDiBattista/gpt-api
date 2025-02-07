from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Session, select
from api.database import engine, get_session  # Importación absoluta
from api.models import *
from api.crud import registrar_vencimiento, obtener_vencimientos, obtener_vencimiento, cambiar_fecha, cambiar_responsable, cambiar_pago
from datetime import date  # Importar date

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if not session.exec(select(Vencimiento)).first():
            print("🚩 No hay vencimientos, creando ejemplos...")
            ejemplos = [
                # Febrero 2025
                Vencimiento(fecha=date(2025, 2, 1), vencimiento=date(2025, 2, 28), descripcion="Pago servicios Q1 2025",         deuda=1500.0, pago=None, pagado=False, responsable="silvia"),
                Vencimiento(fecha=date(2025, 2, 1), vencimiento=date(2025, 2, 28), descripcion="Cuota mantenimiento Q1 2025",    deuda=2000.0, pago=None, pagado=False, responsable="carlos"),
                Vencimiento(fecha=date(2025, 2, 1), vencimiento=date(2025, 2, 28), descripcion="Seguro anual 2025",              deuda=3500.0, pago=None, pagado=False, responsable="marcelo"),
                Vencimiento(fecha=date(2025, 2, 1), vencimiento=date(2025, 2, 28), descripcion="Impuestos municipales Q1",       deuda=1200.0, pago=None, pagado=False, responsable="silvia"),
                # Marzo 2025
                Vencimiento(fecha=date(2025, 3, 1), vencimiento=date(2025, 3, 31), descripcion="Servicios marzo 2025",           deuda=1600.0, pago=None, pagado=False, responsable="carlos"),
                Vencimiento(fecha=date(2025, 3, 1), vencimiento=date(2025, 3, 31), descripcion="Mantenimiento edificio",         deuda=2200.0, pago=None, pagado=False, responsable="marcelo"),
                Vencimiento(fecha=date(2025, 3, 1), vencimiento=date(2025, 3, 31), descripcion="Cuota leasing 2025",             deuda=3000.0, pago=None, pagado=False, responsable="silvia"),
                Vencimiento(fecha=date(2025, 3, 1), vencimiento=date(2025, 3, 31), descripcion="Servicios limpieza",             deuda=1800.0, pago=None, pagado=False, responsable="carlos"),
                # Abril 2025
                Vencimiento(fecha=date(2025, 4, 1), vencimiento=date(2025, 4, 30), descripcion="Servicios Q2 2025",              deuda=1700.0, pago=None, pagado=False, responsable="marcelo"),
                Vencimiento(fecha=date(2025, 4, 1), vencimiento=date(2025, 4, 30), descripcion="Cuota mantenimiento Q2 2025",    deuda=2100.0, pago=None, pagado=False, responsable="silvia"),
                Vencimiento(fecha=date(2025, 4, 1), vencimiento=date(2025, 4, 30), descripcion="Impuestos municipales Q2",       deuda=1300.0, pago=None, pagado=False, responsable="carlos"),
                Vencimiento(fecha=date(2025, 4, 1), vencimiento=date(2025, 4, 30), descripcion="Seguro trimestral",              deuda=2500.0, pago=None, pagado=False, responsable="marcelo"),
            ]
            for ejemplo in ejemplos:
                registrar_vencimiento(session, ejemplo)
            print("✅ Ejemplos creados.")
    yield

app = FastAPI(lifespan=lifespan)

# Ruta raíz: devuelve la lista completa de vencimientos.
@app.get("/", 
         summary="Ruta raíz de la API que devuelve una lista de vencimientos.", 
         description="Consulta la base de datos y retorna una lista completa de vencimientos registrados.")
def leer_raiz(session: Session = Depends(get_session)) -> list[Vencimiento]:
    return obtener_vencimientos(session)

# Crea un nuevo vencimiento a partir de VencimientoCreate y lo registra en la base de datos.
@app.post("/vencimientos/", 
          summary="Crea un nuevo vencimiento en la base de datos.",
          description="Crea un objeto Vencimiento a partir de VencimientoCreate y lo registra en la base de datos.")
def crear_vencimiento(vencimiento: VencimientoCreate, session: Session = Depends(get_session)) -> Vencimiento:
    nuevo_vencimiento = Vencimiento(**vencimiento.model_dump())
    return registrar_vencimiento(session, nuevo_vencimiento)

# Filtra y retorna vencimientos según criterios.
@app.get("/vencimientos/", 
         summary="Obtiene una lista de vencimientos filtrados según criterios.", 
         description="Permite filtrar vencimientos por fechas, estado de pago y responsable.")
def leer_vencimientos(desde: date = None, hasta: date = None, pagado: bool = None, responsable: str = None, session: Session = Depends(get_session)) -> list[Vencimiento]:
    return obtener_vencimientos(session, desde, hasta, pagado, responsable)

# Retorna un vencimiento específico por ID.
@app.get("/vencimientos/{id}", 
         summary="Obtiene un vencimiento específico por ID.", 
         description="Busca en la base de datos el vencimiento con el identificador único dado y retorna error si no se encuentra.")
async def leer_vencimiento(id: int, session: Session = Depends(get_session)) -> Vencimiento:
    vencimiento = obtener_vencimiento(session, id)
    if not vencimiento:
        raise HTTPException(status_code=404, detail="Vencimiento no encontrado")
    return vencimiento

# Actualiza la fecha de vencimiento.
@app.patch("/vencimientos/{id}/pasar/{fecha}", 
           summary="Actualiza la fecha de vencimiento.", 
           description="Cambia la fecha de un vencimiento específico; retorna el objeto actualizado o error en caso de inexistencia.")
async def actualizar_fecha_vencimiento(id: int, fecha: date, session: Session = Depends(get_session)) -> Vencimiento:
    vencimiento = cambiar_fecha(session, id, fecha)
    if not vencimiento:
        raise HTTPException(status_code=404, detail="Vencimiento no encontrado")
    return vencimiento

# Actualiza el responsable del vencimiento.
@app.patch("/vencimientos/{id}/asignar/{responsable}", 
           summary="Actualiza el responsable del vencimiento.", 
           description="Modifica el responsable de un vencimiento y retorna el objeto actualizado; lanza error si no se encuentra.")
async def actualizar_responsable_vencimiento(id: int, responsable: str, session: Session = Depends(get_session)) -> Vencimiento:
    vencimiento = cambiar_responsable(session, id, responsable)
    if not vencimiento:
        raise HTTPException(status_code=404, detail="Vencimiento no encontrado")
    return vencimiento

# Actualiza el pago de un vencimiento.
@app.patch("/vencimientos/{id}/pagar/{monto}", 
           summary="Actualiza el pago de un vencimiento.", 
           description="Registra un nuevo monto de pago y marca el vencimiento como pagado; retorna el objeto actualizado o error si no existe.")
async def actualizar_pago_vencimiento(id: int, monto: float = None, session: Session = Depends(get_session)) -> Vencimiento:
    vencimiento = cambiar_pago(session, id, monto)
    if not vencimiento:
        raise HTTPException(status_code=404, detail="Vencimiento no encontrado")
    return vencimiento
