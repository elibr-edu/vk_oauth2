from sqlalchemy.orm import Mapped
from .base import Base
from .annotated import str_not_nullable_an, email_nullanle_an, phone_nullable_number_an
from .mixins.int_id_pk import IntIdPkMixin


class User(Base, IntIdPkMixin):
    __tablename__ = "users"

    email: Mapped[email_nullanle_an]
    first_name: Mapped[str_not_nullable_an]
    last_name: Mapped[str_not_nullable_an]
    phone_number: Mapped[phone_nullable_number_an]
