from typing import Annotated
from sqlalchemy import String
from sqlalchemy.orm import mapped_column

str_not_nullable_an = Annotated[str, mapped_column(nullable=False)]
email_not_nullanle_an = Annotated[str, mapped_column(String(40), nullable=False, unique=True)]
str_nullable_an = Annotated[str | None, mapped_column(nullable=True)]
float_not_nullable_an = Annotated[float, mapped_column(nullable=False)]
float_nullable_an = Annotated[float | None, mapped_column(nullable=True)]
int_not_nullable_an = Annotated[int, mapped_column(nullable=False)]
int_nullable_an = Annotated[int | None, mapped_column(nullable=True)]
phone_nullable_number_an = Annotated[str, mapped_column(String(10), nullable=True)]
email_nullanle_an = Annotated[str | None, mapped_column(String(40), nullable=True, unique=True)]
