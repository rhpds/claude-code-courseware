"""Pydantic models for MCP tool inputs and outputs."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class CsvWorkshopEntry(BaseModel):
    """A single workshop row for CSV generation."""

    ci: str = Field(description="Catalog item ID, e.g. openshift-cnv.ocp-virt-roadshow-multi-user.prod")
    namespace: str = Field(description="OpenShift namespace for deployment")
    users: Optional[int] = Field(None, ge=0, description="Seat count for num_users validation")
    instances: Optional[int] = Field(None, ge=1, description="WorkshopProvision spec.count")
    ci_name: Optional[str] = Field(None, description="Display name (defaults to CI)")
    workshop_name: Optional[str] = Field(None, description="Override display name in manifests")
    enable_workshop_interface: bool = Field(True, description="Create Workshop + WorkshopProvision")
    multi_asset: bool = Field(False, description="Legacy multi-asset mode")
    asset_cis: List[str] = Field(default_factory=list, description="Asset CIs for legacy multi-asset")
    multi_workshop_name: Optional[str] = Field(None, description="Group name for new-style multi-asset")
    count: Optional[int] = Field(None, ge=1, description="Row expansion count")
    aws_region: Optional[str] = Field(None, description="Comma-separated AWS regions")
    salesforce_ids: Optional[str] = Field(None, description="Semicolon-separated Salesforce IDs")
    salesforce_type: str = Field("opportunity", description="Default Salesforce ID type")
    redirect: bool = Field(True, description="Enable lab redirect")
    catalog_namespace: Optional[str] = Field(None, description="Override auto-detected catalog namespace")
    showroom_repo: Optional[str] = None
    showroom_ref: Optional[str] = None
    showroom_novnc: bool = False
    showroom_zerotouch: bool = False


class CsvGenerateInput(BaseModel):
    """Input for the flow-generate-csv tool."""

    workshops: List[CsvWorkshopEntry] = Field(min_length=1)
    start_time: str = Field(description="ISO 8601 datetime for first provisioning, e.g. 2026-05-07T11:45:00")
    interval_minutes: int = Field(10, ge=0, description="Minutes between staggered provisions")
    auto_stop_hours: int = Field(8, ge=1, description="Hours after provisioning to auto-stop")
    auto_destroy_days: int = Field(14, ge=1, description="Days after provisioning to auto-destroy")
    password: str = Field(description="Workshop password")
    concurrency: Optional[int] = Field(None, ge=1, description="WorkshopProvision concurrency")
    activity: str = Field("Admin", description="Activity field")
    purpose: str = Field("QA", description="Purpose field")


class ExtendInput(BaseModel):
    """Parameters for extend-stop or extend-destroy operations."""

    days: int = Field(0, ge=0, le=30)
    hours: int = Field(0, ge=0, le=720)
    ci_filter: Optional[str] = None


class ScaleInput(BaseModel):
    """Parameters for the scale operation."""

    target_count: int = Field(ge=0, le=1000)
    ci_filter: Optional[str] = None


class DeployInput(BaseModel):
    """Parameters for deploy (dry-run or live)."""

    dry_run: bool = False
    ci_filter: Optional[str] = None
    resource_lock: bool = True
    enable_resource_pools: bool = False
    white_glove: bool = True
    redirect: bool = True


class QaInput(BaseModel):
    """Parameters for QA run."""

    qa_type: Literal["1", "2", "3", "both", "all"] = "all"
    namespace: Optional[str] = None


class OperationsInput(BaseModel):
    """Unified input for flow-operations tool."""

    action: Literal["lock", "unlock", "extend-stop", "extend-destroy", "scale", "disable-autostop"]
    ci_filter: Optional[str] = None
    extend: Optional[ExtendInput] = None
    scale: Optional[ScaleInput] = None
