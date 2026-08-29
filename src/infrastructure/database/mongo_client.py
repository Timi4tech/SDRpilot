import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

MONGO_URI = os.environ["MONGO_URI"]  
DB_NAME = os.environ.get("MONGO_DB_NAME", "leadsengineops")

client = AsyncIOMotorClient(
    MONGO_URI,

    # --- Connection pool sizing ---
    maxPoolSize=50,          # max concurrent connections to the cluster
    minPoolSize=5,           # keep warm connections ready, avoids cold-start latency
    maxIdleTimeMS=60_000,    # close idle pooled connections after 60s

    # --- Timeouts (fail fast instead of hanging requests) ---
    serverSelectionTimeoutMS=5_000,   # how long to wait to find a usable node
    connectTimeoutMS=5_000,           # how long to wait to establish a connection
    socketTimeoutMS=20_000,           # how long to wait on an individual query

    # --- Reliability ---
    #retryWrites=True,        # auto-retry transient write failures (Atlas default, explicit here)
    #retryReads=True,

    # --- Write/read guarantees ---
    #w="majority",             # write acknowledged by majority of replica set nodes
    #readPreference="primaryPreferred",  # reads from primary, falls back to secondary if down

    # --- App identification (shows up in Atlas monitoring/logs) ---
    appname="leadsengineops-api",

    # --- TLS (Atlas requires this; mongodb+srv:// usually handles it automatically,
    # but explicit is safer if you ever move off SRV-style URIs) ---
    tls=False,
)


def get_db() -> AsyncIOMotorDatabase:
    """Returns the database handle. Motor's client already pools connections
    internally, so this is cheap to call on every request."""
    return client[DB_NAME]


async def verify_connection() -> bool:
    """Call this on app startup to fail fast if the cluster is unreachable,
    rather than discovering it on the first user request."""
    try:
        await client.admin.command("ping")
        logger.info("MongoDB cluster connection verified.")
        return True
    except Exception:
        logger.error("MongoDB cluster connection failed.", exc_info=True)
        raise