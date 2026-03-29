"""
OS-APOW GitHub Events Models

Pydantic models for GitHub webhook event payloads.
Used by the Notifier service to validate and parse incoming webhooks.
"""

from typing import List, Optional
from pydantic import BaseModel


class GitHubLabel(BaseModel):
    """GitHub label object."""

    id: int
    node_id: str
    name: str
    color: str
    description: Optional[str] = None


class GitHubUser(BaseModel):
    """GitHub user object."""

    id: int
    node_id: str
    login: str
    avatar_url: str
    html_url: str
    type: str


class GitHubRepository(BaseModel):
    """GitHub repository object."""

    id: int
    node_id: str
    name: str
    full_name: str
    html_url: str
    owner: GitHubUser
    private: bool


class GitHubIssue(BaseModel):
    """GitHub issue object."""

    id: int
    node_id: str
    number: int
    title: str
    body: Optional[str] = None
    html_url: str
    state: str
    labels: List[GitHubLabel] = []
    user: GitHubUser
    assignees: List[GitHubUser] = []


class IssuesEvent(BaseModel):
    """GitHub 'issues' webhook event payload."""

    action: str
    issue: GitHubIssue
    repository: GitHubRepository
    sender: GitHubUser


class PullRequestEvent(BaseModel):
    """GitHub 'pull_request' webhook event payload."""

    action: str
    number: int
    pull_request: dict  # Simplified for now
    repository: GitHubRepository
    sender: GitHubUser


class PullRequestReviewEvent(BaseModel):
    """GitHub 'pull_request_review' webhook event payload."""

    action: str
    review: dict  # Simplified for now
    pull_request: dict
    repository: GitHubRepository
    sender: GitHubUser
