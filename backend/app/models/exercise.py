"""Exercise catalog model.

Location: app/models/exercise.py

This did not exist yet -- ExerciseEntry.exercise_id is an Integer FK with
no catalog table behind it. This model + the seed list below fill that gap,
using every exercise named in fitness_coaching_handoff.docx (Machine,
Dumbbell, and Home templates) so Telegram set-logging has something real
to resolve exercise names against.
"""

from typing import List, Optional

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Exercise(Base):
    """A single exercise in the catalog, with aliases for fuzzy name matching."""

    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    aliases: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    template: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # machine/dumbbell/home
    equipment: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "aliases": self.aliases or [],
            "template": self.template,
            "equipment": self.equipment,
        }
