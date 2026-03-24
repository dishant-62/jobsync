"""ORM models."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from job_platform.db.base import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    jobs: Mapped[list[Job]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    job_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    apply_url: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True)
    posted_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Parsed job fields
    skills: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    experience_level: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    is_remote: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, index=True)

    company: Mapped[Company] = relationship(back_populates="jobs")


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="guest",  # Mock user ID for now
        index=True,
    )
    job_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("jobs.job_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationship to Job (optional, for eager loading)
    job: Mapped[Job] = relationship(
        foreign_keys=[job_id],
        primaryjoin="SavedJob.job_id == Job.job_id",
    )
