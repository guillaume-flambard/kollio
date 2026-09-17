import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from src.modules.branches.adapters import postgres as branches_postgres  # noqa: F401
from src.modules.challenge.adapters import postgres as challenge_postgres  # noqa: F401
from src.modules.company_context.adapters import postgres as company_context_postgres  # noqa: F401
from src.modules.constraint_analysis.adapters import postgres as analysis_postgres  # noqa: F401
from src.modules.converge.adapters import postgres as converge_postgres  # noqa: F401
from src.modules.decision_spaces.adapters import postgres as decision_spaces_postgres  # noqa: F401
from src.modules.decisions.adapters import postgres as decisions_postgres  # noqa: F401
from src.modules.ideas.adapters import postgres  # noqa: F401
from src.modules.iterations.adapters import postgres as iterations_postgres  # noqa: F401
from src.modules.options.adapters import postgres as options_postgres  # noqa: F401
from src.platform import effects, embeddings, import_legacy  # noqa: F401
from src.platform.config import get_settings
from src.platform.db import Base

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata


def include_object(obj, name, type_, reflected, compare_to):
    return not (type_ == "table" and reflected and name not in Base.metadata.tables)


def run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


async def online():
    engine = create_async_engine(get_settings().database_url)
    async with engine.connect() as connection:
        await connection.run_sync(run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    context.configure(
        url=get_settings().database_url, target_metadata=target_metadata, literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    asyncio.run(online())
