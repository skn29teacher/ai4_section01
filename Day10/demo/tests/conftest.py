from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import create_app
from scripts.init_db import initialize, DEMO_PASSWORD


@pytest.fixture(scope="session")
def seeded_database(tmp_path_factory):
    path = tmp_path_factory.mktemp("seed") / "seed.db"
    initialize(path, DEMO_PASSWORD, demo=True)
    return path


@pytest.fixture
def app(tmp_path, seeded_database):
    path = tmp_path / "test.db"
    shutil.copyfile(seeded_database, path)
    return create_app(dict(TESTING=True, SECRET_KEY="test-secret-" * 5, DATABASE_PATH=str(path), PRODUCTION=False))


@pytest.fixture
def client(app):
    return app.test_client()


def mutate(client, path, method="POST", data=None, **kwargs):
    token = client.get("/api/auth/me").json["csrf_token"]
    return client.open(path, method=method, json=data if data is not None else {}, headers={"X-CSRF-Token": token, **kwargs})


def login(client, email="user1@example.com"):
    return mutate(client, "/api/auth/login", data=dict(email=email, password=DEMO_PASSWORD))
