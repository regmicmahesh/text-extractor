import typing as ty

from pydantic import BaseModel, Field


class Company(BaseModel):
    name: str = Field(description="Name of the company")
    founders: ty.List[str] = Field(description="Name of the founders of the company")
    founded_date: str = Field(
        description="Establishment date of the company in format YYYY-MM-DD. Use 01 for month and day if not provided."
    )


class CompanyList(BaseModel):
    companies: ty.List[Company] = Field(description="list of companies")
