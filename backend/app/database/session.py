from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

db_url = settings.DATABASE_URL

# Normalize scheme for asyncpg driver
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://") and "+asyncpg" not in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Auto-convert direct Supabase IPv6 host to IPv4 Pooler host for Render compatibility
if "db.ktsobwkibnwdrzamgkvd.supabase.co" in db_url:
    db_url = db_url.replace("db.ktsobwkibnwdrzamgkvd.supabase.co:5432", "aws-0-ap-southeast-1.pooler.supabase.com:6543")
    if "postgres:" in db_url:
        db_url = db_url.replace("postgres:", "postgres.ktsobwkibnwdrzamgkvd:", 1)

connect_args = {}
if "sqlite" in db_url:
    connect_args["check_same_thread"] = False
else:
    connect_args["statement_cache_size"] = 0

try:
    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
        connect_args=connect_args
    )
except Exception as e:
    print(f"⚠️ Failed to initialize engine for {db_url}: {e}. Falling back to SQLite.")
    db_url = "sqlite+aiosqlite:///./jobpilot.db"
    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False}
    )

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
