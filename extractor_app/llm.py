from functools import partial

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain_text_splitters import TokenTextSplitter

from psycopg_pool import AsyncConnectionPool

from extractor_app import schema
import extractor_app.database as database


OUTPUT_PARSER = PydanticOutputParser(pydantic_object=schema.CompanyList)

PROMPT = PromptTemplate(
    template="Extract data from the given texts based on the instructions.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": OUTPUT_PARSER.get_format_instructions()},
)


async def insert_into_database(
    companies: schema.CompanyList,
    db_pool: AsyncConnectionPool,
) -> None:
    async with db_pool.connection() as conn:
        await database.bulk_upsert_companies(conn, companies=companies)


def chunkify_text(text: str) -> list[str]:
    text_splitter = TokenTextSplitter(
        chunk_size=1024,
        chunk_overlap=20,
    )
    return text_splitter.split_text(text)


def get_model(api_key: str, model_name: str = "gpt-4o-mini") -> ChatOpenAI:
    return ChatOpenAI(model=model_name, api_key=api_key)  # type: ignore


async def get_chain(model: ChatOpenAI, db_pool: AsyncConnectionPool):
    return (
        PROMPT | model | OUTPUT_PARSER | partial(insert_into_database, db_pool=db_pool)
    )
