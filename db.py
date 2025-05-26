from sqlalchemy import create_engine, MetaData, Table, Column, String, Date, Text

engine = create_engine("sqlite:///vakitler.db", connect_args={"check_same_thread": False})
meta = MetaData()

vakitler = Table(
    "vakitler", meta,
    Column("id", String, primary_key=True),
    Column("il", String),
    Column("ilce", String),
    Column("tarih", Date),
    Column("data", Text),
)

meta.create_all(engine)
