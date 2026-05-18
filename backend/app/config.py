"""应用配置

敏感配置项通过环境变量注入，不在代码中硬编码默认值。
docker-compose.yml 中提供了开发环境的默认值，生产环境请务必修改。
"""
import os
import sys


class Settings:
    APP_NAME: str = "商品管理系统"
    APP_VERSION: str = "1.0.0"

    # Database — 必须通过环境变量配置
    DB_HOST: str = os.environ.get("DB_HOST", "")
    DB_PORT: int = int(os.environ.get("DB_PORT", "3306"))
    DB_USER: str = os.environ.get("DB_USER", "")
    DB_PASSWORD: str = os.environ.get("DB_PASSWORD", "")
    DB_NAME: str = os.environ.get("DB_NAME", "")

    @property
    def DATABASE_URL(self) -> str:
        if not all([self.DB_HOST, self.DB_USER, self.DB_PASSWORD, self.DB_NAME]):
            print("ERROR: 数据库环境变量未配置 (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)", file=sys.stderr)
            sys.exit(1)
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset=utf8mb4&collation=utf8mb4_unicode_ci"
        )

    # JWT — 必须通过环境变量配置
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.environ.get("JWT_EXPIRE_MINUTES", "480"))

    # CORS — 逗号分隔的允许来源列表，"*" 表示允许所有（仅限开发环境）
    CORS_ORIGINS: str = os.environ.get("CORS_ORIGINS", "*")

    @property
    def cors_origin_list(self) -> list[str]:
        raw = self.CORS_ORIGINS.strip()
        if raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]

    # Redis — 可选，配置后限流将使用 Redis 共享存储（适用于多实例部署）
    REDIS_URL: str = os.environ.get("REDIS_URL", "")

    # Upload
    UPLOAD_DIR: str = os.environ.get("UPLOAD_DIR", "/app/uploads")
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB

    # Pagination
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    def validate(self):
        """启动时校验必要配置"""
        missing = []
        if not self.DB_HOST:
            missing.append("DB_HOST")
        if not self.DB_USER:
            missing.append("DB_USER")
        if not self.DB_PASSWORD:
            missing.append("DB_PASSWORD")
        if not self.DB_NAME:
            missing.append("DB_NAME")
        if not self.JWT_SECRET:
            missing.append("JWT_SECRET")
        if missing:
            print(f"ERROR: 缺少必要环境变量: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)

        # 防止使用 .env.example 中的占位值启动
        placeholder = []
        if "CHANGEME" in self.DB_PASSWORD:
            placeholder.append("DB_PASSWORD")
        if "CHANGEME" in self.JWT_SECRET:
            placeholder.append("JWT_SECRET")
        if placeholder:
            print(
                f"ERROR: 以下环境变量仍为占位值，请在 .env 中替换: {', '.join(placeholder)}",
                file=sys.stderr,
            )
            sys.exit(1)


settings = Settings()
