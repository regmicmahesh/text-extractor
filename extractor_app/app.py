import typing as ty

from dotenv import load_dotenv

from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel, Field

from sanic import Config, Sanic, redirect
from sanic.request import Request
from sanic_ext import validate

from extractor_app import database
from extractor_app.llm import get_chain, get_model, chunkify_text

load_dotenv()

app = Sanic("ExtractorApp", config=Config(env_prefix="EXTRACTOR_APP_"))


@app.before_server_start
async def setup_dependencies(app, _):
    db_pool: AsyncConnectionPool[ty.Any] = await database.get_connection_pool(
        conn_string=app.config.DATABASE_CONN_STRING
    )
    app.ctx.db_pool = db_pool

    llm_model = get_model(app.config.OPENAI_API_KEY)
    llm_chain = await get_chain(llm_model, db_pool)
    app.ctx.llm_chain = llm_chain


@app.get("/")
@app.ext.template("pages/home.html")
async def home_page(_: Request):
    chain_graph = app.ctx.llm_chain.get_graph().draw_ascii()
    return {"chain_graph": chain_graph}


@app.get("/display")
@app.ext.template("pages/display.html")
async def display_page(_):
    async with app.ctx.db_pool.connection() as conn:
        companies = await database.fetch_companies(conn)
        return {"companies": companies}


@app.get("/import")
@app.ext.template("pages/import.html")
async def import_page(_):
    return {}


class ImportDto(BaseModel):
    essay: str = Field(max_length=10240, min_length=10)


@app.post("/import")
@validate(form=ImportDto)
async def process_import(_: Request, body: ImportDto):
    chunked_text = chunkify_text(body.essay)
    await app.ctx.llm_chain.abatch([{"query": text} for text in chunked_text])
    return redirect("/display")
