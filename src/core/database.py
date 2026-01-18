"""
MongoDB database connection module.

Handles MongoDB connection lifecycle using Motor (async MongoDB driver).
"""

import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MongoDB connection lifecycle."""

    def __init__(self):
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        """Establish connection to MongoDB."""
        mongodb_url = os.getenv("MONGODB_URL")
        if not mongodb_url:
            raise ValueError("MONGODB_URL environment variable is not set")

        database_name = os.getenv("MONGODB_DATABASE", "mumble_ai")

        logger.info("Connecting to MongoDB...")
        print(f"Connecting to MongoDB: {mongodb_url}")

        self.client = AsyncIOMotorClient(
            mongodb_url,
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000,
        )

        # Verify connection
        await self.client.admin.command('ping')
        self.db = self.client[database_name]

        logger.info(f"Connected to MongoDB database: {database_name}")

    async def close(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            logger.info("Closing MongoDB connection...")
            self.client.close()
            self.client = None
            self.db = None
            logger.info("MongoDB connection closed")

    def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if self.db is None:
            raise RuntimeError("Database not connected")
        return self.db


# Singleton instance
db_manager = DatabaseManager()
