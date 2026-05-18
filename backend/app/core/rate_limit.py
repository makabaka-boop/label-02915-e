"""API 限流中间件 — 滑动窗口限流

支持两种后端：
- **memory**（默认）：基于进程内存，适用于单实例开发/测试。
- **redis**：基于 Redis ZSET，适用于多实例/分布式生产部署。

通过环境变量 REDIS_URL 控制：为空时使用内存，配置后自动切换 Redis。
"""
import time
import uuid
from collections import defaultdict
from threading import Lock
from typing import Optional

from fastapi import Request, HTTPException
from loguru import logger


def get_real_client_ip(request: Request) -> str:
    """解析真实客户端 IP，依次检查 X-Forwarded-For、X-Real-IP、request.client.host"""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # X-Forwarded-For: client, proxy1, proxy2 — 取第一个即为原始客户端
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "unknown"


# ──────────────────────────────────────────────
# 内存实现（单实例）
# ──────────────────────────────────────────────

class MemoryRateLimiter:
    """基于进程内存的滑动窗口限流器"""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60, key_prefix: str = ""):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.key_prefix = key_prefix
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def _get_client_key(self, request: Request) -> str:
        client_ip = get_real_client_ip(request)
        return f"{self.key_prefix}{client_ip}" if self.key_prefix else client_ip

    def _cleanup(self, key: str, now: float):
        cutoff = now - self.window_seconds
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]

    def reset(self):
        """清空所有限流记录（用于测试）"""
        with self._lock:
            self._requests.clear()

    def check(self, request: Request):
        """检查是否超过限流，超过则抛出 429"""
        key = self._get_client_key(request)
        now = time.time()

        with self._lock:
            self._cleanup(key, now)
            if len(self._requests[key]) >= self.max_requests:
                raise HTTPException(
                    status_code=429,
                    detail=f"请求过于频繁，请 {self.window_seconds} 秒后再试",
                )
            self._requests[key].append(now)


# ──────────────────────────────────────────────
# Redis 实现（多实例 / 分布式）
# ──────────────────────────────────────────────

class RedisRateLimiter:
    """基于 Redis ZSET 的滑动窗口限流器

    每个客户端 key 对应一个 Sorted Set，score 为请求时间戳。
    通过 ZREMRANGEBYSCORE 清理过期记录，ZCARD 判断窗口内请求数。
    """

    def __init__(self, redis_client, max_requests: int = 60, window_seconds: int = 60, key_prefix: str = ""):
        self._redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.key_prefix = f"rate_limit:{key_prefix}" if key_prefix else "rate_limit:"

    def _get_client_key(self, request: Request) -> str:
        client_ip = get_real_client_ip(request)
        return f"{self.key_prefix}{client_ip}"

    def reset(self):
        """清空所有限流记录（用于测试）"""
        for key in self._redis.scan_iter(f"{self.key_prefix}*"):
            self._redis.delete(key)

    def check(self, request: Request):
        """检查是否超过限流，超过则抛出 429"""
        key = self._get_client_key(request)
        now = time.time()
        cutoff = now - self.window_seconds

        pipe = self._redis.pipeline(True)
        try:
            pipe.zremrangebyscore(key, 0, cutoff)
            pipe.zcard(key)
            pipe.zadd(key, {f"{now}:{uuid.uuid4().hex[:8]}": now})
            pipe.expire(key, self.window_seconds + 1)
            results = pipe.execute()
        except Exception as e:
            logger.warning(f"Redis 限流异常，放行请求: {e}")
            return

        current_count = results[1]
        if current_count >= self.max_requests:
            raise HTTPException(
                status_code=429,
                detail=f"请求过于频繁，请 {self.window_seconds} 秒后再试",
            )


# ──────────────────────────────────────────────
# 工厂函数 — 根据配置自动选择后端
# ──────────────────────────────────────────────

def _create_redis_client(redis_url: str):
    """尝试创建 Redis 连接，失败则返回 None"""
    try:
        import redis
        client = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=3)
        client.ping()
        logger.info(f"限流后端: Redis ({redis_url})")
        return client
    except Exception as e:
        logger.warning(f"Redis 连接失败，回退到内存限流: {e}")
        return None


def create_limiter(
    max_requests: int = 60,
    window_seconds: int = 60,
    key_prefix: str = "",
    redis_url: str = "",
):
    """创建限流器实例，根据 redis_url 自动选择后端"""
    if redis_url:
        client = _create_redis_client(redis_url)
        if client:
            return RedisRateLimiter(client, max_requests, window_seconds, key_prefix)
    return MemoryRateLimiter(max_requests, window_seconds, key_prefix)


def _init_limiters():
    """初始化全局限流器实例"""
    from app.config import settings
    redis_url = settings.REDIS_URL

    _global = create_limiter(max_requests=120, window_seconds=60, redis_url=redis_url)
    _login = create_limiter(max_requests=5, window_seconds=60, key_prefix="login:", redis_url=redis_url)
    return _global, _login


global_limiter: Optional[object] = None
login_limiter: Optional[object] = None


def get_global_limiter():
    global global_limiter
    if global_limiter is None:
        global_limiter, _ = _init_limiters()
    return global_limiter


def get_login_limiter():
    global login_limiter
    if login_limiter is None:
        _, login_limiter = _init_limiters()
    return login_limiter
