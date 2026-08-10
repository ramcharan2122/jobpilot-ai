from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

CLOUD_SUPABASE_URL = "postgresql+asyncpg://postgres.ktsobwkibnwdrzamgkvd:padmasri%4044@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

db_url = settings.DATABASE_URL

# Fallback to persistent Supabase Cloud PostgreSQL if DATABASE_URL is default/SQLite
if not db_url or "sqlite" in db_url:
    db_url = CLOUD_SUPABASE_URL

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

connect_args = {"statement_cache_size": 0}

engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    connect_args=connect_args
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
