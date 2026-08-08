"""
Lambda entrypoint. Wraps the same FastAPI app used locally so there is
exactly one implementation of the API surface, not a parallel one.
"""
from mangum import Mangum

from src.api import app

handler = Mangum(app)
