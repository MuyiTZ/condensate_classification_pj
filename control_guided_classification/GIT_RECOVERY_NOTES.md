# Git Recovery Notes

The Git repository for this project lives at `D:\Tianzi\condensate_classification_pj`.

```bash
# See recent commits
git log --oneline

# See changed files
git status

# See changes in a file
git diff path/to/file

# Restore one file to the last committed version
git restore path/to/file

# Restore the whole project to the last committed version
git restore .

# Go back to a previous commit temporarily
git checkout COMMIT_HASH

# Return to main
git checkout main
```

These notes are for recovery only. They are not run automatically.
