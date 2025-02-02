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

@app.get("/", response_model=list[Vencimiento])
def leer_raiz(session: Session = Depends(get_session)):
    """
    Ruta raíz de la API que devuelve una lista de vencimientos.

    Parámetros:
        - session (Session): Sesión de base de datos SQLModel, gestionada automáticamente.

    Retorna:
        List[Vencimiento]: Lista de vencimientos.
    """
    return obtener_vencimientos(session)


@app.post("/vencimientos/", response_model=Vencimiento)
def crear_vencimiento(vencimiento: VencimientoCreate, session: Session = Depends(get_session)):
    """
    Crea un nuevo vencimiento en la base de datos.

    Parámetros:
        - vencimiento (VencimientoCreate): Objeto Vencimiento a crear.
        - session (Session): Sesión de base de datos SQLModel, gestionada automáticamente.

    Retorna:
        Vencimiento: Vencimiento creado.
    """
    return registrar_vencimiento(session, vencimiento)


@app.get("/vencimientos/", response_model=list[Vencimiento])
def leer_vencimientos(desde: date = None, hasta: date = None, pagado: bool = None, responsable: str = None, session: Session = Depends(get_session)):
    """
    Obtiene una lista de vencimientos filtrados según los parámetros especificados.

    Parámetros:
        - desde (date, opcional): Fecha inicial para filtrar vencimientos.
        - hasta (date, opcional): Fecha final para filtrar vencimientos.
        - pagado (bool, opcional): Estado de pago para filtrar vencimientos. True para pagados, False para impagos.
        - responsable (str, opcional): Responsable para filtrar vencimientos.
        - session (Session): Sesión de base de datos SQLModel, gestionada automáticamente.

    Retorna:
        List[Vencimiento]: Lista de objetos Vencimiento que cumplen con los filtros.
    """
    return obtener_vencimientos(session, desde, hasta, pagado, responsable)


@app.get("/vencimientos/{id}", response_model=Vencimiento)
async def leer_vencimiento(id: int, session: Session = Depends(get_session)):
    """
    Obtiene un vencimiento específico por su ID.

    Parámetros:
        - id (int): ID del vencimiento a obtener.
        - session (Session): Sesión de base de datos SQLModel, gestionada automáticamente.

    Retorna:
        Vencimiento: Objeto Vencimiento encontrado.

    Excepciones:
        - HTTPException: Se lanza con status_code=404 si no se encuentra el vencimiento.
    """
    vencimiento = obtener_vencimiento(session, id)
    if not vencimiento:
        raise HTTPException(status_code=404, detail="Vencimiento no encontrado")
    return vencimiento


@app.patch("/vencimientos/{id}/pasar/{fecha}", response_model=Vencimiento)
async def actualizar_fecha_vencimiento(id: int, fecha: date, session: Session = Depends(get_session)):
    """
    Actualiza la fecha de un vencimiento específico.

    Parámetros:
        - id (int): ID del vencimiento a actualizar.
        - fecha (date): Nueva fecha para el vencimiento.
        - session (Session): Sesión de base de datos SQLModel, gestionada automáticamente.

    Retorna:
        Vencimiento: Objeto Vencimiento actualizado.

    Excepciones:
        - HTTPException: Se lanza con status_code=404 si no se encuentra el vencimiento.
    """
    vencimiento = cambiar_fecha(session, id, fecha)
    if not vencimiento:
        raise HTTPException(status_code=404, detail="Vencimiento no encontrado")
    return vencimiento


@app.patch("/vencimientos/{id}/asignar/{responsable}", response_model=Vencimiento)
async def actualizar_responsable_vencimiento(id: int, responsable: str, session: Session = Depends(get_session)):
    """
    Actualiza el responsable de un vencimiento específico.

    Parámetros:
        - id (int): Identificador único del vencimiento a modificar.
        - responsable (str): Nuevo responsable que se asignará al vencimiento.
        - session (Session): Sesión de base de datos SQLModel, gestionada automáticamente.

    Retorna:
        Vencimiento: Objeto vencimiento actualizado.

    Excepciones:
        - HTTPException: Se lanza con status_code=404 si no se encuentra el vencimiento.
    """
    vencimiento = cambiar_responsable(session, id, responsable)
    if not vencimiento:
        raise HTTPException(status_code=404, detail="Vencimiento no encontrado")
    return vencimiento


@app.patch("/vencimientos/{id}/pagar/{monto}", response_model=Vencimiento)
async def actualizar_pago_vencimiento(id: int, monto: float = None, session: Session = Depends(get_session)):
    """
    Actualiza el monto de pago y marca un vencimiento como pagado.

    Parámetros:
        - id (int): Identificador único del vencimiento a actualizar.
        - monto (float, opcional): Nuevo monto del pago. Si se omite, se aplicará el monto por defecto.
        - session (Session): Sesión de base de datos SQLModel, gestionada automáticamente.

    Retorna:
        Vencimiento: Objeto vencimiento actualizado.

    Excepciones:
        - HTTPException: Se lanza con status_code=404 si no se encuentra el vencimiento.
    """
    vencimiento = cambiar_pago(session, id, monto)
    if not vencimiento:
        raise HTTPException(status_code=404, detail="Vencimiento no encontrado")
    return vencimiento
