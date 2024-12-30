from contextlib import asynccontextmanager

from psycopg import AsyncConnection
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from extractor_app import schema


async def get_connection_pool(conn_string: str):
    return AsyncConnectionPool(conninfo=conn_string)


@asynccontextmanager
async def get_connection(conn_pool: AsyncConnectionPool):
    async with conn_pool.connection() as conn:
        yield conn


async def upsert_company(conn: AsyncConnection, *, company: schema.Company) -> None:
    async with conn.cursor() as curr:
        await curr.execute(
            """
                        INSERT INTO company_details (name, founders, founded_date)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (name) DO UPDATE SET
                            founders = EXCLUDED.founders,
                            founded_date = EXCLUDED.founded_date;
                        """,
            (company.name, company.founders, company.founded_date),
        )
    return await conn.commit()


async def bulk_upsert_companies(
    conn: AsyncConnection, *, companies: schema.CompanyList
) -> None:
    async with conn.cursor() as curr:
        for company in companies.companies:
            await curr.execute(
                """
                            INSERT INTO company_details (name, founders, founded_date)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (name) DO UPDATE SET
                                founders = EXCLUDED.founders,
                                founded_date = EXCLUDED.founded_date;
                            """,
                (company.name, company.founders, company.founded_date),
            )
    return await conn.commit()


async def fetch_companies(conn: AsyncConnection) -> list[dict]:
    async with conn.cursor(row_factory=dict_row) as curr:
        res = await curr.execute("SELECT * FROM company_details")
        data = await res.fetchall()
        return data
