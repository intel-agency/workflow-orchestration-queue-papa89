"""
Tests for GitHub Queue implementation.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from src.queue.github_queue import GitHubQueue, ITaskQueue
from src.models.work_item import WorkItem, TaskType, WorkItemStatus


class TestGitHubQueueInit:
    """Tests for GitHubQueue initialization."""

    def test_init_with_all_params(self):
        """Test initialization with all parameters."""
        queue = GitHubQueue(token="test-token", org="test-org", repo="test-repo")
        assert queue.token == "test-token"
        assert queue.org == "test-org"
        assert queue.repo == "test-repo"

    def test_init_with_token_only(self):
        """Test initialization with token only (for notifier use)."""
        queue = GitHubQueue(token="test-token")
        assert queue.token == "test-token"
        assert queue.org == ""
        assert queue.repo == ""


class TestGitHubQueueAddToQueue:
    """Tests for add_to_queue method."""

    @pytest.mark.asyncio
    async def test_add_to_queue_success(self, sample_work_item_data):
        """Test successful queue addition."""
        queue = GitHubQueue(token="test-token")
        item = WorkItem(**sample_work_item_data)

        # Mock successful response
        queue._client = AsyncMock()
        queue._client.post.return_value = MagicMock(status_code=200)

        result = await queue.add_to_queue(item)
        assert result is True

    @pytest.mark.asyncio
    async def test_add_to_queue_failure(self, sample_work_item_data):
        """Test failed queue addition."""
        queue = GitHubQueue(token="test-token")
        item = WorkItem(**sample_work_item_data)

        # Mock failed response
        queue._client = AsyncMock()
        queue._client.post.return_value = MagicMock(status_code=404)

        result = await queue.add_to_queue(item)
        assert result is False


class TestGitHubQueueFetchQueuedTasks:
    """Tests for fetch_queued_tasks method."""

    @pytest.mark.asyncio
    async def test_fetch_requires_org_and_repo(self):
        """Test that fetch requires org and repo to be set."""
        queue = GitHubQueue(token="test-token")  # No org/repo
        result = await queue.fetch_queued_tasks()
        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_returns_empty_on_error(self):
        """Test that fetch returns empty list on API error."""
        queue = GitHubQueue(token="test-token", org="test-org", repo="test-repo")
        queue._client = AsyncMock()
        queue._client.get.return_value = MagicMock(status_code=500, text="Server error")

        result = await queue.fetch_queued_tasks()
        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_raises_on_rate_limit(self):
        """Test that fetch raises HTTPStatusError on rate limit."""
        queue = GitHubQueue(token="test-token", org="test-org", repo="test-repo")
        queue._client = AsyncMock()

        # Create a mock response that will raise for status
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Rate limited", request=MagicMock(), response=mock_response
        )
        queue._client.get.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await queue.fetch_queued_tasks()


class TestGitHubQueueUpdateStatus:
    """Tests for update_status method."""

    @pytest.mark.asyncio
    async def test_update_status_with_comment(self, sample_work_item_data):
        """Test status update with comment."""
        queue = GitHubQueue(token="test-token")
        item = WorkItem(**sample_work_item_data)

        queue._client = AsyncMock()
        queue._client.delete.return_value = MagicMock(status_code=200)
        queue._client.post.return_value = MagicMock(status_code=201)

        await queue.update_status(item, WorkItemStatus.SUCCESS, comment="Task completed")

        # Verify both label and comment posts were made
        assert queue._client.delete.called
        assert queue._client.post.call_count == 2  # labels + comment


class TestGitHubQueueClose:
    """Tests for close method."""

    @pytest.mark.asyncio
    async def test_close_releases_client(self):
        """Test that close properly releases the HTTP client."""
        queue = GitHubQueue(token="test-token")
        queue._client = AsyncMock()

        await queue.close()
        queue._client.aclose.assert_called_once()
