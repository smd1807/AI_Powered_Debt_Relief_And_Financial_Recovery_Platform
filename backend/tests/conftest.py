"""
Shared pytest configuration.

All test_*.py files in this suite import `app.main` and therefore share
the SAME SQLAlchemy engine/database for the whole pytest session (Python
only imports a module once per process). This fixture deletes the test
database file exactly once, after every test file has finished — never
mid-session, which would break whichever test file runs next.
"""
import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_database():
    yield
    for db_file in ("test_finrelief.db", "finrelief.db"):
        if os.path.exists(db_file):
            os.remove(db_file)
