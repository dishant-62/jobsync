"""ETL-style pipelines."""

from job_platform.pipeline.main_pipeline import (
    run_main_pipeline,
    JobProcessingResult,
    SourceProcessingResult,
    PipelineMetrics,
    PipelineRunResult as MainPipelineRunResult,
)
from job_platform.pipeline.multi_source_pipeline import (
    run_all_sources,
    run_sources_by_type,
    SourceIngestResult,
    PipelineRunResult,
)

__all__ = [
    # New integrated pipeline
    "run_main_pipeline",
    "JobProcessingResult",
    "SourceProcessingResult",
    "PipelineMetrics",
    "MainPipelineRunResult",

    # Legacy pipeline
    "run_all_sources",
    "run_sources_by_type",
    "SourceIngestResult",
    "PipelineRunResult",
]
