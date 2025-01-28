from sqlmodel import Session, select
from models import Vencimiento

# Crear
def registrar_vencimiento(session: Session, vencimiento: Vencimiento):
    """
    Registra un nuevo vencimiento en la base de datos.

    :param session: Sesión de SQLModel para interactuar con la base de datos.
    :param vencimiento: Objeto Vencimiento a registrar.
    :return: El objeto Vencimiento registrado.
    
    En caso de no tener un responsable debe enviar un string vacío.
    En caso de no tener una fecha de pago debe enviar un string vacío y asumirá que es el mismo día que el vencimiento.
    En caso de no tener un monto de pago debe enviar un 0.0 y asumirá que no se ha pagado.
    En caso de no tener un responsable debe enviar un string vacío.
    """
    session.add(vencimiento)
    session.commit()
    session.refresh(vencimiento)
    return vencimiento

# Leer
def obtener_vencimientos(session: Session, desde: str = None, hasta: str = None, pagado: bool = None, responsable: str = None):
    """
    Obtiene una lista de vencimientos según los filtros especificados.
    Args:
        session (Session): Sesión de base de datos SQLModel
        desde (str, optional): Fecha inicial para filtrar vencimientos. Defaults to None.
        hasta (str, optional): Fecha final para filtrar vencimientos. Defaults to None. 
        pagado (bool, optional): Filtrar por estado de pago. True para pagados, False para impagos. Defaults to None.
        responsable (str, optional): Filtrar por responsable del vencimiento. Defaults to None.
    Returns:
        list: Lista de objetos Vencimiento que cumplen con los filtros especificados
    Example:
        >>> vencimientos = obtener_vencimientos(session, desde="2023-01-01", hasta="2023-12-31", pagado=False)
    """
    query = select(Vencimiento)

    if desde:
        query = query.where(Vencimiento.fecha >= desde)
    if hasta:
        query = query.where(Vencimiento.fecha <= hasta)

    if pagado is not None:
        if pagado:
            query = query.where(Vencimiento.pago > 0)
        else:
            query = query.where(Vencimiento.pago == 0)

    if responsable:
        query = query.where(Vencimiento.responsable == responsable)
    
    return session.exec(query).all()

def obtener_vencimiento_por_id(session: Session, id: int):
    """
    Obtiene un vencimiento específico por su ID.

    :param session: Sesión de SQLModel para interactuar con la base de datos.
    :param id: ID del vencimiento a obtener.
    :return: Objeto Vencimiento o None si no se encuentra.
    """
    return session.get(Vencimiento, id)

# Actualizar fecha de pago
def cambiar_fecha(session: Session, id: int, fecha: str):
    """
    Cambia la fecha de un vencimiento específico.

    :param session: Sesión de SQLModel para interactuar con la base de datos.
    :param id: ID del vencimiento a actualizar.
    :param fecha: Nueva fecha para el vencimiento.
    :return: El objeto Vencimiento actualizado o None si no se encuentra.
    """
    if vencimiento := session.get(Vencimiento, id):
        vencimiento.fecha = fecha
        session.add(vencimiento)
        session.commit()
        session.refresh(vencimiento)
    return vencimiento

# Cambiar responsable
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

# Cambiar pago
def cambiar_pago(session: Session, id: int, monto: float):
    """
    Cambia el monto y marca como pagado un vencimiento específico.

    :param session: Sesión de SQLModel para interactuar con la base de datos.
    :param id: ID del vencimiento a actualizar.
    :param monto: Nuevo monto del pago.
    :return: El objeto Vencimiento actualizado o None si no se encuentra.
    """
    if vencimiento := session.get(Vencimiento, id):
        if monto is not None:
            vencimiento.pago = monto
        vencimiento.pagado = True
        session.add(vencimiento)
        session.commit()
        session.refresh(vencimiento)
    return vencimiento