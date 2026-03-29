"""
Tests for WorkItem model and utility functions.
"""

import pytest
from src.models.work_item import (
    TaskType,
    WorkItemStatus,
    WorkItem,
    scrub_secrets,
)


class TestTaskType:
    """Tests for TaskType enum."""

    def test_task_type_values(self):
        """Test that TaskType has expected values."""
        assert TaskType.PLAN.value == "PLAN"
        assert TaskType.IMPLEMENT.value == "IMPLEMENT"
        assert TaskType.BUGFIX.value == "BUGFIX"


class TestWorkItemStatus:
    """Tests for WorkItemStatus enum."""

    def test_status_values(self):
        """Test that WorkItemStatus has expected label values."""
        assert WorkItemStatus.QUEUED.value == "agent:queued"
        assert WorkItemStatus.IN_PROGRESS.value == "agent:in-progress"
        assert WorkItemStatus.SUCCESS.value == "agent:success"
        assert WorkItemStatus.ERROR.value == "agent:error"
        assert WorkItemStatus.INFRA_FAILURE.value == "agent:infra-failure"


class TestWorkItem:
    """Tests for WorkItem Pydantic model."""

    def test_work_item_creation(self, sample_work_item_data):
        """Test creating a WorkItem with all required fields."""
        item = WorkItem(**sample_work_item_data)
        assert item.id == "12345"
        assert item.issue_number == 42
        assert item.task_type == TaskType.IMPLEMENT
        assert item.status == WorkItemStatus.QUEUED

    def test_work_item_from_dict(self, sample_work_item_data):
        """Test WorkItem creation from dictionary."""
        item = WorkItem.model_validate(sample_work_item_data)
        assert item.target_repo_slug == "test-org/test-repo"


class TestScrubSecrets:
    """Tests for the scrub_secrets utility function."""

    def test_scrub_github_pat(self):
        """Test that GitHub PATs are redacted."""
        text = "Token: ghp_1234567890abcdefghijklmnopqrstuvwxyz1234"
        result = scrub_secrets(text)
        assert "ghp_" not in result
        assert "***REDACTED***" in result

    def test_scrub_openai_key(self):
        """Test that OpenAI-style keys are redacted."""
        text = "API key: sk-1234567890abcdefghijklmnop"
        result = scrub_secrets(text)
        assert "sk-" not in result
        assert "***REDACTED***" in result

    def test_scrub_bearer_token(self):
        """Test that Bearer tokens are redacted."""
        text = "Authorization: Bearer abc123xyz789token"
        result = scrub_secrets(text)
        assert "Bearer abc" not in result.lower()
        assert "***REDACTED***" in result

    def test_scrub_preserves_normal_text(self):
        """Test that normal text without secrets is preserved."""
        text = "This is a normal message without any secrets."
        result = scrub_secrets(text)
        assert result == text

    def test_scrub_custom_replacement(self):
        """Test custom replacement string."""
        text = "Token: ghp_1234567890abcdefghijklmnopqrstuvwxyz1234"
        result = scrub_secrets(text, replacement="[HIDDEN]")
        assert "[HIDDEN]" in result

    def test_scrub_github_server_token(self):
        """Test that GitHub server tokens are redacted."""
        text = "Token: ghs_1234567890abcdefghijklmnopqrstuvwxyz1234"
        result = scrub_secrets(text)
        assert "ghs_" not in result

    def test_scrub_github_fine_grained_pat(self):
        """Test that GitHub fine-grained PATs are redacted."""
        text = "Token: github_pat_1234567890abcdefghij"
        result = scrub_secrets(text)
        assert "github_pat_" not in result
