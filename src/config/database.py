from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from src.config.settings import settings

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.db_name = None
    
    async def connect(self):
        """Connect to database and print info"""
        self.engine = create_async_engine(
            settings.DATABASE_URL_ASYNC,
            echo=settings.DEBUG  # Show SQL queries in debug mode
        )
        
        self.session_factory = sessionmaker(
            self.engine, 
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Get database info
        async with self.engine.begin() as conn:
            result = await conn.execute(text("SELECT current_database()"))
            self.db_name = result.scalar()
            
            # Get host info
            result = await conn.execute(text("SELECT inet_server_addr(), inet_server_port()"))
            host_info = result.fetchone()
            
        print(f"✅ Connected to database '{self.db_name}' at {host_info[0] or 'localhost'}:{host_info[1] or 5432}")
    
    async def disconnect(self):
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()
            print(f"📴 Disconnected from database '{self.db_name}'")
    
    async def get_session(self):
        """Get database session"""
        async with self.session_factory() as session:
            yield session

# Global database manager
db_manager = DatabaseManager()

# Dependency for FastAPI routes
async def get_db():
    async for session in db_manager.get_session():
        yield session