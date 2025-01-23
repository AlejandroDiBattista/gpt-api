from sqlmodel import Session, select
from .models import Vencimiento

# Crear
def crear_vencimiento(session: Session, vencimiento: Vencimiento):
    session.add(vencimiento)
    session.commit()
    session.refresh(vencimiento)
    return vencimiento

# Leer
def obtener_vencimientos(session: Session):
    return session.exec(select(Vencimiento)).all()

def obtener_vencimiento_por_id(session: Session, id: int):
    return session.get(Vencimiento, id)

# Actualizar
def cambiar_fecha(session: Session, id: int, fecha: str):
    if vencimiento := session.get(Vencimiento, id):
        vencimiento.fecha = fecha
        session.add(vencimiento)
        session.commit()
        session.refresh(vencimiento)
    return vencimiento

# Cambiar responsable
def cambiar_responsable(session: Session, id: int, responsable: str):
    if vencimiento := session.get(Vencimiento, id):
        vencimiento.responsable = responsable
        session.add(vencimiento)
        session.commit()
        session.refresh(vencimiento)
    return vencimiento

# Cambiar pago
def cambiar_pago(session: Session, id: int, monto: float = None):
    if vencimiento := session.get(Vencimiento, id):
        if monto is not None:
            vencimiento.pago = monto
        vencimiento.pagado = True
        session.add(vencimiento)
        session.commit()
        session.refresh(vencimiento)
    return vencimiento