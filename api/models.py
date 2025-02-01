from sqlmodel import SQLModel, Field
from datetime import date  # Importar date

class VencimientoBase(SQLModel):
    """
    Base para el modelo Vencimiento.

    :param vencimiento: Fecha de vencimiento.
    :param descripcion: Descripción del vencimiento.
    :param deuda: Monto de la deuda.
    :param pago: Fecha de pago, puede ser None.
    :param pagado: Monto pagado, puede ser None.
    :param responsable: Responsable del pago, puede ser None.
    """
    # Datos del vencimiento
    vencimiento: date       # Fecha de vencimiento
    descripcion: str        # Descripción del vencimiento
    deuda: float            # Monto de la deuda
    # Datos del pago
    pago: date | None = None       # Fecha de pago 
    pagado: float | None = None    # Monto pagado
    responsable: str | None = None # Responsable del pago

class VencimientoCreate(VencimientoBase):
    pass    

class Vencimiento(VencimientoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

