import json
import os
from uuid import uuid4

TEST_DATABASE_URL = os.environ.get("AGROSENSE_TEST_DATABASE_URL")
os.environ["DATABASE_URL"] = TEST_DATABASE_URL or "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-only-secret-for-agrosense-backend-tests"
os.environ["FRONTEND_ORIGINS"] = "http://localhost:5173"
os.environ["AGRICULTURAL_ADMIN_EMAILS"] = "catalog-admin@example.com"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Text, create_engine, event, select, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base, Farm, Plot, User


@pytest.fixture
def test_email():
    return f"agrosense-test-{uuid4().hex}@example.com"


@pytest.fixture
def test_emails():
    return []


@pytest.fixture
def client(test_emails):
    sqlite_test = TEST_DATABASE_URL is None
    database_url = TEST_DATABASE_URL or "sqlite+pysqlite:///:memory:"
    if sqlite_test:
        Farm.__table__.c.boundary.type = Text()
        Plot.__table__.c.boundary.type = Text()

    engine_options = {"pool_pre_ping": True}
    if sqlite_test:
        engine_options.update(
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    engine = create_engine(database_url, **engine_options)

    if sqlite_test:
        @event.listens_for(engine, "connect")
        def register_spatial_test_functions(connection, record):
            del record
            connection.create_function("ST_GeomFromGeoJSON", 1, lambda value: value)
            connection.create_function("ST_SetSRID", 2, lambda value, srid: value if srid == 4326 else None)

            def as_multipolygon(value):
                geometry = json.loads(value)
                if geometry["type"] == "Polygon":
                    geometry = {"type": "MultiPolygon", "coordinates": [geometry["coordinates"]]}
                return json.dumps(geometry)

            connection.create_function("ST_Multi", 1, as_multipolygon)
            connection.create_function("ST_IsValid", 1, lambda value: int(value is not None))
            connection.create_function("AsGeoJSON", 1, lambda value: value)

        Base.metadata.create_all(engine)
    else:
        with engine.connect() as connection:
            extension = connection.scalar(
                text("SELECT extname FROM pg_extension WHERE extname = 'postgis'")
            )
            if extension != "postgis":
                raise RuntimeError("PostGIS is not enabled in the configured integration test database.")
            if connection.scalar(
                text("SELECT ST_SRID(ST_SetSRID(ST_MakePoint(0, 0), 4326))")
            ) != 4326:
                raise RuntimeError("PostGIS spatial functions are not available in the connection search path.")
            revision = connection.scalar(text("SELECT version_num FROM alembic_version"))
            if revision != "20261124_plot_dashboard":
                raise RuntimeError("Apply Alembic migrations through the current agricultural master catalog revision before integration tests.")

    test_sessions = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        with test_sessions() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        if sqlite_test:
            Base.metadata.drop_all(engine)
        elif test_emails:
            with test_sessions() as session:
                users = session.scalars(select(User).where(User.email.in_(test_emails)))
                for user in users:
                    session.delete(user)
                session.commit()
        engine.dispose()
