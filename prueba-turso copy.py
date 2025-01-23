import asyncio
from sqlmodel import SQLModel, Field, create_engine, Session
from libsql_client import create_client_sync
from typing import Any, Optional
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.engine.cursor import CursorResultMetaData
from sqlalchemy.engine.row import Row
from sqlalchemy import text

URL = "libsql://vencimiento-adibattista.turso.io"
TOKEN = 'eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3Mzc1MDExMjEsImlkIjoiMDA2MjQxMjAtODk2YS00MDllLWE4MDUtYmNlZjVkYThhNTcxIn0.e-1OWld33Mx_PMHKf-eEdj8GpQE5PKIw1aSSCvuhYdCmS3Np8IpajawWaKoWF6pAxZO2JciOkHYEgij_drwUCw'

class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    power: str
    age: Optional[int] = None

class TursoConnection:
    def __init__(self, client):
        self.client = client
        self._cursor = None
        self._transaction = None
        self.last_result = None

    def execute(self, statement, parameters=None):
        sql = str(statement)
        self.last_result = self.client.execute(sql, parameters)
        return self

    def close(self):
        if self._transaction:
            self.rollback()
    
    def commit(self):
        if self._transaction:
            self.client.execute("COMMIT")
            self._transaction = None
        return True

    def rollback(self):
        if self._transaction:
            self.client.execute("ROLLBACK")
            self._transaction = None
        return True

    def cursor(self):
        return self

    def begin(self):
        if not self._transaction:
            self.client.execute("BEGIN")
            self._transaction = True
        return self
    
    def check_table_exists(self, table_name):
        result = self.client.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", [table_name])
        return len(result.rows) > 0

    def create_function(self, name, num_params, func, *, deterministic=False):
        pass  # SQLite specific, we can ignore

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def description(self):
        if self.last_result and self.last_result.columns:
            return [(col, None, None, None, None, None, None) for col in self.last_result.columns]
        return None

    @property
    def rowcount(self):
        if self.last_result and self.last_result.rows:
            return len(self.last_result.rows)
        return -1

    def fetchall(self):
        if self.last_result:
            return self.last_result.rows
        return []

    def fetchone(self):
        if self.last_result and self.last_result.rows:
            return self.last_result.rows[0]
        return None

# La clase TursoConnection es necesaria para integrar libsql_client con SQLAlchemy.
# No se realizan cambios en esta sección.

def create_turso_engine():
    client = create_client_sync(url=URL, auth_token=TOKEN)
    
    def connect():
        conn = TursoConnection(client)
        return conn

    return create_engine(
        "sqlite://",
        creator=connect,
        echo=True,
        isolation_level="AUTOCOMMIT"
    )

def main():
    engine = create_turso_engine()
    
    # Verificar y recrear tabla si es necesario
    with engine.connect() as conn:
        turso_conn = conn.connection
        if hasattr(turso_conn, 'check_table_exists') and turso_conn.check_table_exists('hero'):
            print("Dropping existing table...")
            conn.execute(text("DROP TABLE IF EXISTS hero"))
            conn.commit()
    
    print("Creating table...")
    SQLModel.metadata.create_all(engine)
    
    # Crear héroes
    with Session(engine) as session:
        hero1 = Hero(name="Thor", power="Rayos", age=1500)
        hero2 = Hero(name="Iron Man", power="Tecnología", age=53)
        session.add(hero1)
        session.add(hero2)
        session.commit()
        
        # Listar héroes
        heroes = session.query(Hero).all()
        print("\n📜 Lista de héroes:")
        for hero in heroes:
            print(f"  {hero.id}: {hero.name} ({hero.power}) - Edad: {hero.age}")
        
        # Eliminar último héroe
        if heroes:
            session.delete(heroes[-1])
            session.commit()
            print(f"❌ Héroe eliminado: {heroes[-1].name}")
        
        # Listar nuevamente
        heroes = session.query(Hero).all()
        print("\n📜 Lista actualizada de héroes:")
        for hero in heroes:
            print(f"  {hero.id}: {hero.name} ({hero.power}) - Edad: {hero.age}")

if __name__ == "__main__":
    main()