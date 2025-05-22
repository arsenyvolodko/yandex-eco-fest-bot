from datetime import datetime

from sqlalchemy import BigInteger, Column, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime
from sqlalchemy import Enum as SAEnum

from yandex_eco_fest_bot.bot.enums import RequestStatus
from yandex_eco_fest_bot.bot.enums.mission_verification_method import (
    MissionVerificationMethod,
)
from yandex_eco_fest_bot.db.core.base_table import BaseTable


class User(BaseTable):
    __tablename__ = "user"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=False,
    )

    username: Mapped[str] = mapped_column(
        nullable=False,
        unique=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __str__(self):
        return f"User(id={self.id}, username={self.username})"


class Location(BaseTable):
    __tablename__ = "location"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=True)
    order: Mapped[int] = mapped_column(nullable=False)
    chat_id = Column(BigInteger, nullable=True)
    is_group: Mapped[bool] = mapped_column(nullable=False, default=False)

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("location.id", ondelete="SET NULL"), nullable=True, default=None
    )

    parent: Mapped["Location"] = relationship(
        back_populates="children",
        remote_side="Location.id",
    )
    children: Mapped[list["Location"]] = relationship(
        back_populates="parent", cascade="all, delete-orphan"
    )
    missions: Mapped[list["Mission"]] = relationship(
        "Mission",
        back_populates="location",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __str__(self):
        return f"Location(id={self.id}, name={self.name}, order={self.order})"

    def __eq__(self, other):
        if isinstance(other, Location):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)


class Mission(BaseTable):
    __tablename__ = "mission"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=True)
    score: Mapped[int] = mapped_column(nullable=False)
    verification_method: Mapped[MissionVerificationMethod] = mapped_column(
        SAEnum(MissionVerificationMethod, name="mission_verification_method"),
        nullable=False,
    )
    location_id: Mapped[int] = mapped_column(ForeignKey("location.id"), nullable=True)
    order: Mapped[int] = mapped_column(nullable=False)

    location: Mapped["Location"] = relationship(
        "Location",
        back_populates="missions",
        lazy="selectin",
    )

    def __str__(self):
        return f"Mission(id={self.id}, name={self.name}, max_score={self.score}, location_id={self.location_id})"

    def __eq__(self, other):
        if isinstance(other, Mission):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)


class UserMissionSubmission(BaseTable):
    __tablename__ = "user_mission_submission"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    mission_id: Mapped[int] = mapped_column(ForeignKey("mission.id"), nullable=False)
    status: Mapped[RequestStatus] = mapped_column(
        SAEnum(RequestStatus, name="user_mission_status"),
        nullable=False,
        default=RequestStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    user: Mapped["User"] = relationship(User, lazy="selectin")
    mission: Mapped["Mission"] = relationship(Mission, lazy="selectin")

    def __str__(self):
        return (
            f"UserMissionSubmission(id={self.id}, user_id={self.user_id}, "
            f"mission_id={self.mission_id}, created_at={self.created_at})"
        )


class Achievement(BaseTable):
    __tablename__ = "achievement"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=True)

    def __eq__(self, other):
        if isinstance(other, Achievement):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return f"Achievement(id={self.id}, name={self.name})"


class UserAchievement(BaseTable):
    __tablename__ = "user_achievement"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    achievement_id: Mapped[int] = mapped_column(ForeignKey("achievement.id"))

    user: Mapped["User"] = relationship(User, lazy="selectin")
    achievement: Mapped["Achievement"] = relationship(Achievement, lazy="selectin")

    def __str__(self):
        return f"UserAchievement(id={self.id}, user_id={self.user_id}, achievement_id={self.achievement_id})"
