# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):
#     app_name: str = "RAG Freelance Assistant"

#     openai_api_key: str

#     chat_model: str = "gpt-4o-mini"
#     embedding_model: str = "text-embedding-3-small"

#     upload_dir: str = "uploads"
#     chroma_dir: str = "storage/chroma"

#     sqlite_path: str = "storage/app.db"
#     sqlite_db_path: str = "storage/app.db"

#     cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         extra="ignore",
#     )


# settings = Settings()


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RAG Freelance Assistant"

    openai_api_key: str

    chat_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    database_url: str

    upload_dir: str = "app/storage/uploads"

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()