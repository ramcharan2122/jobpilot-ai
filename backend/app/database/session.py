from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

CLOUD_SUPABASE_URL = "postgresql+asyncpg://postgres.ktsobwkibnwdrzamgkvd:padmasri%4044@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

# Force ALWAYS use verified Supabase Cloud IPv4 Pooler URL for 100% persistent connection
db_url = CLOUD_SUPABASE_URL

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
