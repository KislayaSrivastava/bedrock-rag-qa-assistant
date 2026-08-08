"""
Lambda entrypoint. Wraps the same FastAPI app used locally so there is
exactly one implementation of the API surface, not a parallel one.

Cold-start note: Lambda's own filesystem is read-only except /tmp, and /tmp
is wiped between execution environments. For this demo, a pre-ingested
ChromaDB snapshot is bundled into the deployment package as chroma_db_seed/
and copied into /tmp on first invocation of a fresh execution environment.
This is a fine shortcut for a small, static demo corpus -- see the roadmap
note in docs/ARCHITECTURE.md for the production-grade alternative (EFS or
a managed vector store) if the corpus needs to grow or update independently
of a redeploy.
"""
import os
import shutil

_SEED_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db_seed")
_RUNTIME_DIR = "/tmp/chroma_db"

if os.path.isdir(_SEED_DIR) and not os.path.exists(_RUNTIME_DIR):
    shutil.copytree(_SEED_DIR, _RUNTIME_DIR)

from mangum import Mangum  # noqa: E402

from src.api import app  # noqa: E402

handler = Mangum(app)