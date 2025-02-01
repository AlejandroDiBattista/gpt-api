from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy import inspect  # Añadido inspect

URL   = "sqlite+libsql://vencimiento-adibattista.turso.io"
TOKEN = 'eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3Mzc1MDExMjEsImlkIjoiMDA2MjQxMjAtODk2YS00MDllLWE4MDUtYmNlZjVkYThhNTcxIn0.e-1OWld33Mx_PMHKf-eEdj8GpQE5PKIw1aSSCvuhYdCmS3Np8IpajawWaKoWF6pAxZO2JciOkHYEgij_drwUCw'

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    power: str
    age: int | None = None

def main():
    URL   = "sqlite+libsql://vencimiento-adibattista.turso.io"
    TOKEN = 'eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3Mzc1MDExMjEsImlkIjoiMDA2MjQxMjAtODk2YS00MDllLWE4MDUtYmNlZjVkYThhNTcxIn0.e-1OWld33Mx_PMHKf-eEdj8GpQE5PKIw1aSSCvuhYdCmS3Np8IpajawWaKoWF6pAxZO2JciOkHYEgij_drwUCw'
    engine = create_engine(f"{URL}?authToken={TOKEN}", echo=True)
    # engine = create_engine("sqlite:///:memory:", echo=True)

    inspector = inspect(engine)
    if inspector.has_table("hero"):
        print("Dropping existing table...")
        # Hero.__table__.drop(engine)
        SQLModel.metadata.drop_all(engine, tables=[Hero.__table__])  # Eliminación declarativa de la tabla
    # Hero.__table__.drop(engine)
    print("Creating table...")
    SQLModel.metadata.create_all(engine)  # Creación de tablas declarativas
    
    # Crear héroes
    with Session(engine) as session:
        hero1 = Hero(name="Thor", power="Rayos", age=1500)
        hero2 = Hero(name="Iron Man", power="Tecnología", age=53)
        session.add(hero1)
        session.add(hero2)
        session.commit()
        
        # Listar héroes
        heroes = session.exec(select(Hero).all())

        print("\n 📜 Lista de héroes:")
        for hero in heroes:
            print(f"  {hero.id}: {hero.name} ({hero.power}) - Edad: {hero.age}")
        
        # # Eliminar último héroe
        # if heroes:
        #     session.delete(heroes[-1])
        #     session.commit()
        #     print(f"❌ Héroe eliminado: {heroes[-1].name}")
        
        # Listar nuevamente
        heroes = session.exec(select(Hero).all())
        print("\n 📜 Lista actualizada de héroes:")
        for hero in heroes:
            print(f"  {hero.id}: {hero.name} ({hero.power}) - Edad: {hero.age}")

if __name__ == "__main__":
    main()