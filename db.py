from sqlalchemy import create_engine, Column, String, Date, Table, MetaData
from datetime import date

engine = create_engine('sqlite:///vakitler.db')
metadata = MetaData()

vakitler = Table('vakitler', metadata,
    Column('id', String, primary_key=True),  # il_ilce_tarih birleşimi
    Column('il', String),
    Column('ilce', String),
    Column('tarih', Date),
    Column('data', String),
)

metadata.create_all(engine)
