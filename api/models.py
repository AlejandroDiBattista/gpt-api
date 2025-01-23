from sqlmodel import SQLModel, Field

class VencimientoBase(SQLModel):
    fecha: str
    vencimiento: str
    descripcion: str
    deuda: float
    pago: float
    pagado: bool
    responsable: str

class Vencimiento(VencimientoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    
