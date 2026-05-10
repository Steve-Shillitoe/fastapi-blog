from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg://postgres:C9VW4LJJMQRtgbA@fastapi-db.cboweoimgxz9.eu-west-2.rds.amazonaws.com:5432/postgres"
)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(result.fetchone())