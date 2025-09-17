#!/usr/bin/env python3
"""
Generate conventional commit messages from branch names and PR titles.

Examples:
- feature/api-new-endpoint -> feat(api): New endpoint
- fix/auth-login-bug -> fix(auth): Login bug  
- hotfix/security-patch -> fix: Security patch
- chore/deps-update -> chore: Deps update
"""
import re
import sys
from typing import Tuple, Optional


def parse_branch_name(branch_name: str) -> Tuple[str, Optional[str], str]:
    """
    Parse branch name into type, scope, and description.
    
    Args:
        branch_name: Branch name like 'feature/api-new-endpoint'
        
    Returns:
        Tuple of (type, scope, description)
    """
    # Remove refs/heads/ if present
    branch_name = branch_name.replace('refs/heads/', '')
    
    # Mapping of branch prefixes to conventional commit types
    type_mapping = {
        'feature': 'feat',
        'feat': 'feat', 
        'fix': 'fix',
        'hotfix': 'fix',
        'bugfix': 'fix',
        'patch': 'fix',
        'chore': 'chore',
        'docs': 'docs',
        'style': 'style',
        'refactor': 'refactor',
        'perf': 'perf',
        'test': 'test',
        'ci': 'ci'
    }
    
    # Pattern: type/scope-description or type/description
    pattern = r'^([^/]+)/(?:([^-_]+)[-_])?(.+)$'
    match = re.match(pattern, branch_name)
    
    if not match:
        # Fallback for simple branch names
        return 'feat', None, branch_name
    
    branch_type, scope, description = match.groups()
    
    # Map branch type to conventional commit type
    commit_type = type_mapping.get(branch_type.lower(), 'feat')
    
    # Clean up description (replace - and _ with spaces, title case)
    description = re.sub(r'[-_]+', ' ', description)
    description = description.strip().capitalize()
    
    return commit_type, scope, description


def generate_conventional_commit(branch_name: str, pr_title: str = None) -> str:
    """
    Generate a conventional commit message.
    
    Args:
        branch_name: Git branch name
        pr_title: Pull request title (optional)
        
    Returns:
        Formatted conventional commit message
    """
    commit_type, scope, description = parse_branch_name(branch_name)
    
    # Use PR title if provided and not already conventional
    if pr_title and not re.match(r'^(feat|fix|docs|style|refactor|perf|test|chore|ci)(\(.+\))?:', pr_title):
        description = pr_title
    
    # Format the commit message
    if scope:
        return f"{commit_type}({scope}): {description}"
    else:
        return f"{commit_type}: {description}"


def main() -> None:
    """CLI interface for the script."""
    min_args = 2
    if len(sys.argv) < min_args:
        print("Usage: python generate_conventional_commit.py <branch_name> [pr_title]")
        sys.exit(1)
    
    branch_name = sys.argv[1]
    pr_title = sys.argv[2] if len(sys.argv) > 2 else None
    
    conventional_commit = generate_conventional_commit(branch_name, pr_title)
    print(conventional_commit)


if __name__ == "__main__":
    main()
