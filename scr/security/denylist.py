import hashlib
import time

from authx import TokenPayload
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials
from redis.asyncio import Redis

from scr.db.session import get_cache
from scr.auth.security import security


class Denylist:
    def __init__(self):
        DENYLIST_PREFIX = "auth:denylist:"