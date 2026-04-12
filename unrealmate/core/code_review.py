"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         UnrealMate - Code Review                             ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  Purpose: GitHub/GitLab code review integration                              ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Code review integration for GitHub and GitLab.
Create PRs, list reviews, and manage review workflows.

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

import json
import logging
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ReviewPlatform(Enum):
    """Supported code review platforms."""
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"


class ReviewState(Enum):
    """Pull/Merge request states."""
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"
    DRAFT = "draft"


@dataclass
class ReviewComment:
    """Represents a review comment."""
    id: str
    author: str
    body: str
    file_path: Optional[str]
    line_number: Optional[int]
    created_at: datetime
    resolved: bool = False


@dataclass
class PullRequest:
    """Represents a pull/merge request."""
    id: str
    number: int
    title: str
    description: str
    author: str
    source_branch: str
    target_branch: str
    state: ReviewState
    created_at: datetime
    updated_at: datetime
    url: str
    comments: List[ReviewComment] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    reviewers: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "number": self.number,
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "source_branch": self.source_branch,
            "target_branch": self.target_branch,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "url": self.url,
            "labels": self.labels,
            "reviewers": self.reviewers,
        }


@dataclass
class DiffSummary:
    """Summary of code changes."""
    files_changed: int
    additions: int
    deletions: int
    file_list: List[str]
    
    def __str__(self) -> str:
        return f"{self.files_changed} files: +{self.additions} -{self.deletions}"


class CodeReviewProvider(ABC):
    """Abstract base class for code review providers."""
    
    @abstractmethod
    def authenticate(self, token: str) -> bool:
        """Authenticate with the platform."""
        pass
    
    @abstractmethod
    def create_pull_request(self, 
                           title: str,
                           description: str,
                           source_branch: str,
                           target_branch: str) -> Optional[PullRequest]:
        """Create a new pull request."""
        pass
    
    @abstractmethod
    def list_pull_requests(self, state: ReviewState = ReviewState.OPEN) -> List[PullRequest]:
        """List pull requests."""
        pass
    
    @abstractmethod
    def add_comment(self, pr_number: int, comment: str, file_path: Optional[str] = None,
                   line_number: Optional[int] = None) -> bool:
        """Add a comment to a pull request."""
        pass
    
    @abstractmethod
    def get_diff(self, pr_number: int) -> DiffSummary:
        """Get diff summary for a pull request."""
        pass


class GitHubProvider(CodeReviewProvider):
    """GitHub code review integration."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.token: Optional[str] = None
        self.repo_owner: Optional[str] = None
        self.repo_name: Optional[str] = None
        self._detect_repo_info()
    
    def _detect_repo_info(self) -> None:
        """Detect repository owner and name from git remote."""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                url = result.stdout.strip()
                # Parse GitHub URL
                if "github.com" in url:
                    # SSH: git@github.com:owner/repo.git
                    # HTTPS: https://github.com/owner/repo.git
                    if url.startswith("git@"):
                        parts = url.split(":")[-1].replace(".git", "").split("/")
                    else:
                        parts = url.replace(".git", "").split("/")[-2:]
                    
                    if len(parts) >= 2:
                        self.repo_owner = parts[-2]
                        self.repo_name = parts[-1]
                        logger.info(f"Detected GitHub repo: {self.repo_owner}/{self.repo_name}")
        except Exception as e:
            logger.warning(f"Could not detect repo info: {e}")
    
    def authenticate(self, token: str) -> bool:
        """Authenticate with GitHub token."""
        self.token = token
        # In a real implementation, validate the token
        logger.info("GitHub authentication configured")
        return True
    
    def create_pull_request(self,
                           title: str,
                           description: str,
                           source_branch: str,
                           target_branch: str) -> Optional[PullRequest]:
        """Create a GitHub pull request using gh CLI or API."""
        if not self.token:
            logger.error("GitHub token not configured")
            return None
        
        try:
            # Use gh CLI if available
            result = subprocess.run(
                [
                    "gh", "pr", "create",
                    "--title", title,
                    "--body", description,
                    "--head", source_branch,
                    "--base", target_branch,
                ],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                url = result.stdout.strip()
                pr_number = int(url.split("/")[-1])
                
                return PullRequest(
                    id=str(pr_number),
                    number=pr_number,
                    title=title,
                    description=description,
                    author="",  # Would need API call
                    source_branch=source_branch,
                    target_branch=target_branch,
                    state=ReviewState.OPEN,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    url=url,
                )
            else:
                logger.error(f"Failed to create PR: {result.stderr}")
                return None
                
        except FileNotFoundError:
            logger.warning("gh CLI not found, falling back to manual instructions")
            return None
        except Exception as e:
            logger.error(f"Error creating PR: {e}")
            return None
    
    def list_pull_requests(self, state: ReviewState = ReviewState.OPEN) -> List[PullRequest]:
        """List GitHub pull requests."""
        prs = []
        
        try:
            result = subprocess.run(
                ["gh", "pr", "list", "--state", state.value, "--json", 
                 "number,title,author,headRefName,baseRefName,state,createdAt,url"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for item in data:
                    pr = PullRequest(
                        id=str(item["number"]),
                        number=item["number"],
                        title=item["title"],
                        description="",
                        author=item.get("author", {}).get("login", "unknown"),
                        source_branch=item["headRefName"],
                        target_branch=item["baseRefName"],
                        state=ReviewState(item["state"].lower()),
                        created_at=datetime.fromisoformat(item["createdAt"].replace("Z", "+00:00")),
                        updated_at=datetime.now(),
                        url=item["url"],
                    )
                    prs.append(pr)
        except Exception as e:
            logger.error(f"Error listing PRs: {e}")
        
        return prs
    
    def add_comment(self, pr_number: int, comment: str, file_path: Optional[str] = None,
                   line_number: Optional[int] = None) -> bool:
        """Add a comment to a GitHub PR."""
        try:
            cmd = ["gh", "pr", "comment", str(pr_number), "--body", comment]
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error adding comment: {e}")
            return False
    
    def get_diff(self, pr_number: int) -> DiffSummary:
        """Get diff summary for a GitHub PR."""
        try:
            result = subprocess.run(
                ["gh", "pr", "diff", str(pr_number), "--stat"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                files = []
                additions = 0
                deletions = 0
                
                for line in lines[:-1]:  # Last line is summary
                    parts = line.split("|")
                    if len(parts) >= 1:
                        files.append(parts[0].strip())
                
                # Parse summary line
                summary = lines[-1] if lines else ""
                # Format: " X files changed, Y insertions(+), Z deletions(-)"
                import re
                match = re.search(r"(\d+) file.*?(\d+) insertion.*?(\d+) deletion", summary)
                if match:
                    additions = int(match.group(2))
                    deletions = int(match.group(3))
                
                return DiffSummary(
                    files_changed=len(files),
                    additions=additions,
                    deletions=deletions,
                    file_list=files
                )
        except Exception as e:
            logger.error(f"Error getting diff: {e}")
        
        return DiffSummary(0, 0, 0, [])


class GitLabProvider(CodeReviewProvider):
    """GitLab code review integration."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.token: Optional[str] = None
        self.project_id: Optional[str] = None
    
    def authenticate(self, token: str) -> bool:
        """Authenticate with GitLab token."""
        self.token = token
        logger.info("GitLab authentication configured")
        return True
    
    def create_pull_request(self,
                           title: str,
                           description: str,
                           source_branch: str,
                           target_branch: str) -> Optional[PullRequest]:
        """Create a GitLab merge request."""
        # GitLab uses glab CLI
        try:
            result = subprocess.run(
                [
                    "glab", "mr", "create",
                    "--title", title,
                    "--description", description,
                    "--source-branch", source_branch,
                    "--target-branch", target_branch,
                ],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Parse MR URL from output
                url = result.stdout.strip()
                return PullRequest(
                    id="",
                    number=0,
                    title=title,
                    description=description,
                    author="",
                    source_branch=source_branch,
                    target_branch=target_branch,
                    state=ReviewState.OPEN,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    url=url,
                )
        except Exception as e:
            logger.error(f"Error creating MR: {e}")
        
        return None
    
    def list_pull_requests(self, state: ReviewState = ReviewState.OPEN) -> List[PullRequest]:
        """List GitLab merge requests."""
        # Placeholder - would use glab CLI
        return []
    
    def add_comment(self, pr_number: int, comment: str, file_path: Optional[str] = None,
                   line_number: Optional[int] = None) -> bool:
        """Add a comment to a GitLab MR."""
        return False
    
    def get_diff(self, pr_number: int) -> DiffSummary:
        """Get diff summary for a GitLab MR."""
        return DiffSummary(0, 0, 0, [])


class CodeReviewManager:
    """
    Central manager for code review operations.
    Automatically detects and uses the appropriate provider.
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.provider: Optional[CodeReviewProvider] = None
        self.platform: Optional[ReviewPlatform] = None
        self._detect_platform()
    
    def _detect_platform(self) -> None:
        """Detect the code review platform from git remote."""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                url = result.stdout.strip().lower()
                
                if "github.com" in url:
                    self.platform = ReviewPlatform.GITHUB
                    self.provider = GitHubProvider(str(self.repo_path))
                elif "gitlab.com" in url or "gitlab" in url:
                    self.platform = ReviewPlatform.GITLAB
                    self.provider = GitLabProvider(str(self.repo_path))
                elif "bitbucket" in url:
                    self.platform = ReviewPlatform.BITBUCKET
                    # Bitbucket provider would go here
                
                logger.info(f"Detected platform: {self.platform}")
        except Exception as e:
            logger.warning(f"Could not detect platform: {e}")
    
    def set_token(self, token: str) -> bool:
        """Set authentication token."""
        if self.provider:
            return self.provider.authenticate(token)
        return False
    
    def create_pr(self,
                  title: str,
                  description: str,
                  source_branch: Optional[str] = None,
                  target_branch: str = "main") -> Optional[PullRequest]:
        """Create a pull/merge request."""
        if not self.provider:
            logger.error("No code review provider configured")
            return None
        
        # Get current branch if source not specified
        if source_branch is None:
            try:
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                source_branch = result.stdout.strip()
            except Exception:
                source_branch = "HEAD"
        
        return self.provider.create_pull_request(
            title, description, source_branch, target_branch
        )
    
    def list_prs(self, state: ReviewState = ReviewState.OPEN) -> List[PullRequest]:
        """List pull/merge requests."""
        if not self.provider:
            return []
        return self.provider.list_pull_requests(state)
    
    def comment(self, pr_number: int, message: str) -> bool:
        """Add a comment to a PR/MR."""
        if not self.provider:
            return False
        return self.provider.add_comment(pr_number, message)
    
    def get_diff_summary(self, pr_number: int) -> DiffSummary:
        """Get diff summary for a PR/MR."""
        if not self.provider:
            return DiffSummary(0, 0, 0, [])
        return self.provider.get_diff(pr_number)
    
    def generate_review_report(self, pr_number: int) -> str:
        """Generate a review report for a PR."""
        if not self.provider:
            return "No provider configured"
        
        prs = self.list_prs()
        pr = next((p for p in prs if p.number == pr_number), None)
        
        if not pr:
            return f"PR #{pr_number} not found"
        
        diff = self.get_diff_summary(pr_number)
        
        report = f"""
📋 Pull Request Review Report
{'=' * 40}

Title: {pr.title}
Author: {pr.author}
Branch: {pr.source_branch} → {pr.target_branch}
State: {pr.state.value.upper()}
Created: {pr.created_at.strftime('%Y-%m-%d %H:%M')}

📊 Changes Summary
{'-' * 20}
Files changed: {diff.files_changed}
Additions: +{diff.additions}
Deletions: -{diff.deletions}

📁 Modified Files
{'-' * 20}
"""
        for f in diff.file_list[:10]:
            report += f"  • {f}\n"
        
        if len(diff.file_list) > 10:
            report += f"  ... and {len(diff.file_list) - 10} more files\n"
        
        report += f"\n🔗 URL: {pr.url}\n"
        
        return report


# Developer signature
DEVELOPER_SIGNATURE = "G & E ZYNTH"
MODULE_VERSION = "1.0.0"

