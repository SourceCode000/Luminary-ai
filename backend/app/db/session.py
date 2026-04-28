from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config import get_settings

settings = get_settings()

# ── Engine ─────────────────────────────────────────────────────────

# The engine is the actual connection to PostgreSQL
# It reads the DATABASE_URL from your .env file
engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",  # logs all SQL in dev mode
)

# ── Session Factory ────────────────────────────────────────────────

# SessionLocal is a factory that creates new sessions
# Think of it like a template for creating database conversations
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # keeps data accessible after committing
)

# ── Dependency ─────────────────────────────────────────────────────

async def get_db():
    """
    FastAPI dependency that gives each request its own database session.
    Automatically closes the session when the request is done.
    """
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()  # undo changes if something goes wrong
            raise