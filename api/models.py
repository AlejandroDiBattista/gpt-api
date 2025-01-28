from sqlmodel import SQLModel, Field

class VencimientoBase(SQLModel):
    # Datos del vencimiento
    vencimiento: str # Fecha de vencimiento
    descripcion: str # Descripción del vencimiento
    deuda: float     # Monto de la deuda
    # Datos de del pago
    pago: str        # Fecha de pago 
    pagado: float    # Monto pagado
    responsable: str # Responsable del pago

class Vencimiento(VencimientoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    
