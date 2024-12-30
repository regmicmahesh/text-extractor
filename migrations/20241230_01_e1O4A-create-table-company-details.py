"""
create table company_details
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        "CREATE TABLE company_details (id SERIAL PRIMARY KEY, name VARCHAR(255) UNIQUE, founders TEXT[], founded_date DATE)",
        "DROP TABLE company_details",
    )
]
