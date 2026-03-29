"""
OS-APOW Queue Package

Contains the task queue interface and implementations.
"""

from src.queue.github_queue import (
    ITaskQueue,
    GitHubQueue,
)

__all__ = [
    "ITaskQueue",
    "GitHubQueue",
]
