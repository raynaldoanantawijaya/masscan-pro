import aiosqlite
import asyncio
from typing import List, Optional, Dict, Any
from proxy_manager.core.config import settings
import os

class StorageManager:
    def __init__(self, db_path: str = settings.database.path):
        self.db_path = db_path
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS proxies (
                    ip TEXT,
                    port INTEGER,
                    protocol TEXT,
                    anonymity TEXT,
                    country TEXT,
                    region TEXT,
                    city TEXT,
                    isp TEXT,
                    response_time_ms INTEGER,
                    last_checked TIMESTAMP,
                    health_score INTEGER DEFAULT 100,
                    success_count INTEGER DEFAULT 0,
                    fail_count INTEGER DEFAULT 0,
                    PRIMARY KEY (ip, port)
                )
            """)
            
            # Migration: Add columns if they don't exist
            # Check if 'isp' column exists
            async with db.execute("PRAGMA table_info(proxies)") as cursor:
                columns = [row[1] for row in await cursor.fetchall()]
                
            if 'isp' not in columns:
                await db.execute("ALTER TABLE proxies ADD COLUMN isp TEXT")
            if 'success_count' not in columns:
                await db.execute("ALTER TABLE proxies ADD COLUMN success_count INTEGER DEFAULT 0")
            if 'fail_count' not in columns:
                await db.execute("ALTER TABLE proxies ADD COLUMN fail_count INTEGER DEFAULT 0")
            if 'region' not in columns:
                await db.execute("ALTER TABLE proxies ADD COLUMN region TEXT")
            if 'city' not in columns:
                await db.execute("ALTER TABLE proxies ADD COLUMN city TEXT")

            await db.commit()

    async def save_proxy(self, proxy_data: Dict[str, Any]):
        # Ensure new fields are present in data or set defaults
        data = proxy_data.copy()
        data.setdefault('isp', 'Unknown')
        data.setdefault('region', '')
        data.setdefault('city', '')
        data.setdefault('success_count', 1)
        data.setdefault('fail_count', 0)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO proxies 
                (ip, port, protocol, anonymity, country, region, city, isp, response_time_ms, last_checked, health_score, success_count, fail_count)
                VALUES (:ip, :port, :protocol, :anonymity, :country, :region, :city, :isp, :response_time_ms, CURRENT_TIMESTAMP, :health_score, :success_count, :fail_count)
            """, data)
            await db.commit()

    async def get_proxies(self, protocol: Optional[str] = None, limit: int = 100) -> List[Any]:
        query = "SELECT * FROM proxies"
        params = []
        if protocol:
            query += " WHERE protocol = ?"
            params.append(protocol)
        
        query += " ORDER BY response_time_ms ASC LIMIT ?"
        params.append(limit)

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def delete_proxy(self, ip: str, port: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM proxies WHERE ip = ? AND port = ?", (ip, port))
            await db.commit()
