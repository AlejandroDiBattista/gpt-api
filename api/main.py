from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Session, select
from api.database import engine, get_session  # Importación absoluta
from api.models import Vencimiento
from api.crud import registrar_vencimiento, obtener_vencimientos, obtener_vencimiento, cambiar_fecha, cambiar_responsable, cambiar_pago

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if not session.exec(select(Vencimiento)).first():
            print("🚩 No hay vencimientos, creando ejemplos")
            ejemplos = [
                # Febrero 2025
                Vencimiento(fecha="2025-02-01", vencimiento="2025-02-28", descripcion="Pago servicios Q1 2025",         deuda=1500.0, pago="", pagado=False, responsable="silvia"),
                Vencimiento(fecha="2025-02-01", vencimiento="2025-02-28", descripcion="Cuota mantenimiento Q1 2025",    deuda=2000.0, pago="", pagado=False, responsable="carlos"),
                Vencimiento(fecha="2025-02-01", vencimiento="2025-02-28", descripcion="Seguro anual 2025",              deuda=3500.0, pago="", pagado=False, responsable="marcelo"),
                Vencimiento(fecha="2025-02-01", vencimiento="2025-02-28", descripcion="Impuestos municipales Q1",       deuda=1200.0, pago="", pagado=False, responsable="silvia"),
                # Marzo 2025
                Vencimiento(fecha="2025-03-01", vencimiento="2025-03-31", descripcion="Servicios marzo 2025",           deuda=1600.0, pago="", pagado=False, responsable="carlos"),
                Vencimiento(fecha="2025-03-01", vencimiento="2025-03-31", descripcion="Mantenimiento edificio",         deuda=2200.0, pago="", pagado=False, responsable="marcelo"),
                Vencimiento(fecha="2025-03-01", vencimiento="2025-03-31", descripcion="Cuota leasing 2025",             deuda=3000.0, pago="", pagado=False, responsable="silvia"),
                Vencimiento(fecha="2025-03-01", vencimiento="2025-03-31", descripcion="Servicios limpieza",             deuda=1800.0, pago="", pagado=False, responsable="carlos"),
                # Abril 2025
                Vencimiento(fecha="2025-04-01", vencimiento="2025-04-30", descripcion="Servicios Q2 2025",              deuda=1700.0, pago="", pagado=False, responsable="marcelo"),
                Vencimiento(fecha="2025-04-01", vencimiento="2025-04-30", descripcion="Cuota mantenimiento Q2 2025",    deuda=2100.0, pago="", pagado=False, responsable="silvia"),
                Vencimiento(fecha="2025-04-01", vencimiento="2025-04-30", descripcion="Impuestos municipales Q2",       deuda=1300.0, pago="", pagado=False, responsable="carlos"),
                Vencimiento(fecha="2025-04-01", vencimiento="2025-04-30", descripcion="Seguro trimestral",              deuda=2500.0, pago="", pagado=False, responsable="marcelo"),
            ]
            for ejemplo in ejemplos:
                registrar_vencimiento(session, ejemplo)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def leer_ruta_raiz(session: Session = Depends(get_session), response_model=list[Vencimiento]):
    """
    Ruta raíz de la API.

    :return: Mensaje de bienvenida.
    """
    return leer_vencimientos(session)


@app.post("/vencimientos/", response_model=Vencimiento)
def crear_vencimiento(vencimiento: Vencimiento, session: Session = Depends(get_session)):
    """
    Crea un nuevo vencimiento en la base de datos.

    :param vencimiento: Objeto Vencimiento a crear.
    :param session: Sesión de base de datos SQLModel.
    :return: Vencimiento creado.
    """
    return registrar_vencimiento(session, vencimiento)


@app.get("/vencimientos/", response_model=list[Vencimiento])
def leer_vencimientos(desde: str = None,hasta: str = None,pagado: bool = None,responsable: str = None, session: Session = Depends(get_session)):
    """
    Obtiene una lista de vencimientos filtrados según los parámetros especificados.

    :param session: Sesión de base de datos SQLModel.
    :param desde: Fecha inicial para filtrar vencimientos. (Opcional)
    :param hasta: Fecha final para filtrar vencimientos. (Opcional)
    :param pagado: Estado de pago para filtrar vencimientos. True para pagados, False para impagos. (Opcional)
    :param responsable: Responsable para filtrar vencimientos. (Opcional)
    :return: Lista de objetos Vencimiento que cumplen con los filtros.
    """
    return obtener_vencimientos(session, desde, hasta, pagado, responsable)


@app.get("/vencimientos/{id}", response_model=Vencimiento)
async def leer_vencimiento(id: int, session: Session = Depends(get_session)):
    """
    Obtiene un vencimiento específico por su ID.

    :param id: ID del vencimiento a obtener.
    :param session: Sesión de base de datos SQLModel.
    :return: Objeto Vencimiento encontrado.
    :raises HTTPException: Si no se encuentra el vencimiento.
    """
    vencimiento = obtener_vencimiento(session, id)
    if not vencimiento:
        raise HTTPException(status_code=404, detail="Vencimiento no encontrado")
    return vencimiento


@app.patch("/vencimientos/{id}/cambiar_fecha", response_model=Vencimiento)
async def actualizar_fecha_vencimiento(id: int, fecha: str, session: Session = Depends(get_session)):
    """
    Actualiza la fecha de un vencimiento específico.

    :param id: ID del vencimiento a actualizar.
    :param fecha: Nueva fecha para el vencimiento.
    :param session: Sesión de base de datos SQLModel.
    :return: Objeto Vencimiento actualizado.
    :raises HTTPException: Si no se encuentra el vencimiento.
    """
    vencimiento = cambiar_fecha(session, id, fecha)
    if not vencimiento:
        raise HTTPException(status_code=404, detail="Vencimiento no encontrado")
    return vencimiento


@app.patch("/vencimientos/{id}/cambiar_responsable", response_model=Vencimiento)
async def actualizar_responsable_vencimiento(id: int, responsable: str, session: Session = Depends(get_session)):
    """
    Actualiza el responsable de un vencimiento específico.

    :param id: ID del vencimiento a actualizar.
    :param responsable: Nuevo responsable del vencimiento.
    :param session: Sesión de base de datos SQLModel.
    :return: Objeto Vencimiento actualizado.
    :raises HTTPException: Si no se encuentra el vencimiento.
    """
    vencimiento = cambiar_responsable(session, id, responsable)
    if not vencimiento:
        raise HTTPException(status_code=404, detail="Vencimiento no encontrado")
    return vencimiento


@app.patch("/vencimientos/{id}/cambiar_pago", response_model=Vencimiento)
async def actualizar_pago_vencimiento(id: int, monto: float = None, session: Session = Depends(get_session)):
    """
    Actualiza el monto y marca como pagado un vencimiento específico.

    :param id: ID del vencimiento a actualizar.
    :param monto: Nuevo monto del pago. (Opcional)
    :param session: Sesión de base de datos SQLModel.
    :return: Objeto Vencimiento actualizado.
    :raises HTTPException: Si no se encuentra el vencimiento.
    """
    vencimiento = cambiar_pago(session, id, monto)
    if not vencimiento:
        raise HTTPException(status_code=404, detail="Vencimiento no encontrado")
    return vencimiento
