"""ETL-style pipelines."""

from job_platform.pipeline.multi_source_pipeline import (
    run_all_sources,
    run_sources_by_type,
    SourceIngestResult,
    PipelineRunResult,
)

__all__ = [
    "run_all_sources",
    "run_sources_by_type",
    "SourceIngestResult",
    "PipelineRunResult",
]
