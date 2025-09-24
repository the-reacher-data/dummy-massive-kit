# PR Comment Update Action

Creates or updates a PR/Issue comment identified by one or more hidden HTML tags.  
Useful for posting reports (pytest, coverage, changelog, etc.) without duplicating comments.

## Usage

```yaml
- uses: org/devops-actions/pr-comment-update@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    tags: "<!-- pytest-report -->,<!-- branch-source:feature/foo -->"
    body-file: pytest_comment.md
````
## Inputs

| Name           | Required | Description                                                                 |
|----------------|----------|-----------------------------------------------------------------------------|
| `github-token` | ✅       | GitHub token (usually `${{ secrets.GITHUB_TOKEN }}`)                        |
| `tags`         | ✅       | Comma-separated list of hidden HTML tags that identify the comment uniquely |
| `body-file`    | ✅       | Path to a Markdown file with the comment body                               |

## Behavior

- If a comment already exists in the PR/Issue with **all the tags**, it is updated.  
- If no comment matches, a new one is created.  
- The final comment will always begin with the tags, followed by the body content.

## Example in a workflow

```yaml
jobs:
  comment:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate report
        run: echo "# ✅ All tests passed" > pytest_comment.md

      - name: Update PR comment
        uses: ./actions/devops/pr-comment-update
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          tags: "<!-- pytest-report -->,<!-- branch-source:${{ github.head_ref }} -->"
          body-file: pytest_comment.md
````
## Example output in PR

The comment posted/updated in the PR will look like this:

```bash
<!-- pytest-report --> # HIDDEN tag

<!-- branch-source:feature/foo --> # HIDDEN tag
```

# ✅ All tests passed


If the job runs again, the same comment will be **updated** with the new content instead of creating duplicates.
