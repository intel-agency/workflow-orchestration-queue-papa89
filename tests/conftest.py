"""
OS-APOW Test Configuration

Shared fixtures and configuration for pytest.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient for testing without network calls."""
    client = AsyncMock()
    return client


@pytest.fixture
def sample_work_item_data():
    """Sample work item data for tests."""
    return {
        "id": "12345",
        "issue_number": 42,
        "source_url": "https://github.com/test-org/test-repo/issues/42",
        "context_body": "Create a new feature for the application",
        "target_repo_slug": "test-org/test-repo",
        "task_type": "IMPLEMENT",
        "status": "agent:queued",
        "node_id": "I_kwDOtest123",
    }


@pytest.fixture
def sample_github_issue():
    """Sample GitHub issue response for tests."""
    return {
        "id": 12345,
        "node_id": "I_kwDOtest123",
        "number": 42,
        "title": "[Application Plan] Create new feature",
        "body": "Create a new feature for the application",
        "html_url": "https://github.com/test-org/test-repo/issues/42",
        "state": "open",
        "labels": [
            {"id": 1, "name": "agent:queued", "color": "ff0000"},
        ],
        "user": {
            "id": 1,
            "login": "testuser",
            "avatar_url": "https://github.com/avatar.png",
            "html_url": "https://github.com/testuser",
        },
        "assignees": [],
    }
