from sqlmodel import select
from api.database import Session, get_session, engine
from api.models import *  # Importación relativa
from datetime import date  # Importar date


def registrar_vencimiento(session: Session, vencimiento: VencimientoCreate):
    """
    Registra un nuevo vencimiento en la base de datos.

    :param session: Sesión de SQLModel para interactuar con la base de datos.
    :param vencimiento: Objeto VencimientoCreate a registrar.
    :return: El objeto Vencimiento registrado.
    
    En caso de no tener un responsable, enviar un string vacío.
    En caso de no tener una fecha de pago, enviar un string vacío y se asumirá que es el mismo día que el vencimiento.
    En caso de no tener un monto de pago, enviar un 0.0 y se asumirá que no se ha pagado.
    """
    session.add(vencimiento)
    session.commit()
    session.refresh(vencimiento)
    return vencimiento


def obtener_vencimientos(session: Session, desde: date = None, hasta: date = None, pagado: bool = None, responsable: str = None):
    """
    Obtiene una lista de vencimientos según los filtros especificados.

    :param session: Sesión de SQLModel para interactuar con la base de datos.
    :param desde: Fecha inicial para filtrar vencimientos. Opcional, por defecto None.
    :param hasta: Fecha final para filtrar vencimientos. Opcional, por defecto None.
    :param pagado: Filtrar por estado de pago. True para pagados, False para impagos. Opcional, por defecto None.
    :param responsable: Filtrar por responsable del vencimiento. Opcional, por defecto None.
    :return: Lista de objetos Vencimiento que cumplen con los filtros especificados.
    :example:
        >>> vencimientos = obtener_vencimientos(session, desde=date(2023, 1, 1), hasta=date(2023, 12, 31), pagado=False)
    """
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

def obtener_vencimiento(session: Session, id: int):
    """
    Obtiene un vencimiento específico por su ID.

    :param session: Sesión de SQLModel para interactuar con la base de datos.
    :param id: ID del vencimiento a obtener.
    :return: Objeto Vencimiento o None si no se encuentra.
    """
    return session.get(Vencimiento, id)


def cambiar_fecha(session: Session, id: int, fecha: date):
    """
    Cambia la fecha de un vencimiento específico.

    :param session: Sesión de SQLModel para interactuar con la base de datos.
    :param id: ID del vencimiento a actualizar.
    :param fecha: Nueva fecha para el vencimiento.
    :return: El objeto Vencimiento actualizado o None si no se encuentra.
    """
    if vencimiento := session.get(Vencimiento, id):
        vencimiento.vencimiento = fecha
        session.add(vencimiento)
        session.commit()
        session.refresh(vencimiento)
    return vencimiento


def cambiar_responsable(session: Session, id: int, responsable: str):
    """
    Cambia el responsable de un vencimiento específico.

    :param session: Sesión de SQLModel para interactuar con la base de datos.
    :param id: ID del vencimiento a actualizar.
    :param responsable: Nuevo responsable del vencimiento.
    :return: El objeto Vencimiento actualizado o None si no se encuentra.
    """
    if vencimiento := session.get(Vencimiento, id):
        vencimiento.responsable = responsable
        session.add(vencimiento)
        session.commit()
        session.refresh(vencimiento)
    return vencimiento


def cambiar_pago(session: Session, id: int, monto: float | None):
    """
    Cambia el monto y marca como pagado un vencimiento específico.

    :param session: Sesión de SQLModel para interactuar con la base de datos.
    :param id: ID del vencimiento a actualizar.
    :param monto: Nuevo monto del pago. Si es None, se actualiza solo la marca de pago.
    :return: El objeto Vencimiento actualizado o None si no se encuentra.
    """
    if vencimiento := session.get(Vencimiento, id):
        if monto is not None:
            vencimiento.pagado = monto
            vencimiento.pago = date.today()
        session.add(vencimiento)
        session.commit()
        session.refresh(vencimiento)
    return vencimiento