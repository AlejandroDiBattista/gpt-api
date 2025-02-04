from sqlmodel import select
from api.database import Session, get_session, engine
from api.models import *  # Importación relativa
from datetime import date  # Importar date


# Registra un nuevo vencimiento en la base de datos.
def registrar_vencimiento(session: Session, vencimiento: VencimientoCreate):
    session.add(vencimiento)
    session.commit()
    session.refresh(vencimiento)
    return vencimiento


# Obtiene una lista de vencimientos según los filtros especificados.
def obtener_vencimientos(session: Session, desde: date = None, hasta: date = None, pagado: bool = None, responsable: str = None):
    query = select(Vencimiento)
    print(f"obtener_vencimientos > {desde=}, {hasta=}, {pagado=}, {responsable=}")
    if desde is not None:
        query = query.where(Vencimiento.vencimiento >= desde)
    if hasta is not None:
        query = query.where(Vencimiento.vencimiento <= hasta)
    if pagado is not None:
        if pagado:
            query = query.where(Vencimiento.pagado > 0)
        else:
            query = query.where(Vencimiento.pagado == 0)
    if responsable:
        query = query.where(Vencimiento.responsable == responsable)
    return session.exec(query).all()


# Obtiene un vencimiento específico por su ID.
def obtener_vencimiento(session: Session, id: int):
    return session.get(Vencimiento, id)


# Cambia la fecha de un vencimiento específico.
def cambiar_fecha(session: Session, id: int, fecha: date):
    if vencimiento := session.get(Vencimiento, id):
        vencimiento.vencimiento = fecha
        session.add(vencimiento)
        session.commit()
        session.refresh(vencimiento)
    return vencimiento


# Cambia el responsable de un vencimiento específico.
def cambiar_responsable(session: Session, id: int, responsable: str):
    if vencimiento := session.get(Vencimiento, id):
        vencimiento.responsable = responsable
        session.add(vencimiento)
        session.commit()
        session.refresh(vencimiento)
    return vencimiento


# Cambia el monto y marca como pagado un vencimiento específico.
def cambiar_pago(session: Session, id: int, monto: float | None):
    if vencimiento := session.get(Vencimiento, id):
        if monto is not None:
            vencimiento.pagado = monto
            vencimiento.pago = date.today()
        session.add(vencimiento)
        session.commit()
        session.refresh(vencimiento)
    return vencimiento