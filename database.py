import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env (local development)
load_dotenv()

# ---------------------------------------------------------------------------
# Database configuration — Supabase PostgreSQL (synchronous)
# ---------------------------------------------------------------------------
# DATABASE_URL must be set in your environment or .env file.
# Get it from Supabase Dashboard → Settings → Database → Connection string (URI).
#
# Example format:
#   postgresql+psycopg2://postgres:<your-db-password>@db.<project-ref>.supabase.co:5432/postgres?sslmode=require
#
# Supabase requires SSL, so the connection string should include ?sslmode=require
# (we also enforce it via connect_args below as a safety net).
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is missing! "
        "Set it to your Supabase PostgreSQL connection string."
    )

# Sync SQLAlchemy engine (compatible with existing sync services)
# pool_pre_ping=True checks connection health before each use (avoids stale/dead connections)
# connect_args={"sslmode": "require"} enforces SSL, which Supabase mandates
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"},
)

# Session factory — synchronous (matches trade_service.py, position_service.py, etc.)
# autocommit=False / autoflush=False = changes only persist on explicit db.commit()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------------------------------------------------------------------
# Database health check
# ---------------------------------------------------------------------------
# Runs a trivial query (SELECT 1) to verify the Supabase connection is alive.
# Returns True if the database responds, False otherwise.
# Useful for startup checks, /health endpoints, or debugging connectivity.
# ---------------------------------------------------------------------------
def check_db_connection() -> bool:
    """Return True if a connection to Supabase can be opened and queried."""
    from sqlalchemy import text

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_db_status() -> dict:
    """Return a small status dict describing the database connection state."""
    connected = check_db_connection()
    return {
        "database": "supabase_postgres",
        "connected": connected,
        "ssl_required": True,
        "synchronous": True,
    }