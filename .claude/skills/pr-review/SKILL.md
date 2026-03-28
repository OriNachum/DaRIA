---
name: pr-review
description: >
  Full PR lifecycle: branch, commit, create PR, wait for reviewer comments,
  fix or pushback, reply, resolve threads, wait for manual merge.
  Use after completing any code change that should go through review.
---

# PR Review Workflow

Complete lifecycle for getting code reviewed and merged.

## Workflow

### 1. Branch (if on main)

If you're on main, create a feature branch first:

```bash
git checkout -b <branch-name>
```

### 2. Commit and push

```bash
git add <files>
git commit -m "message"
git push -u origin <branch-name>
```

### 3. Create PR

```bash
gh pr create --title "Title" --body "$(cat <<'EOF'
## Summary
- What changed

## Test plan
- How to verify

🤖 Generated with [Claude Code](https://claude.com/claude-code)

- Claude
EOF
)"
```

### 4. Wait for reviewers

Reviewers (Qodo, Copilot, humans) need time to post comments. Wait **5 minutes** after creating the PR before checking.

```bash
sleep 300
```

### 5. Poll for comments

Check every **1 minute** until comments appear:

```bash
bash ~/.claude/skills/pr-review/scripts/pr-comments.sh <PR_NUMBER>
```

If no inline comments found, wait 1 minute and check again. After 3 empty checks, assume reviewers are done.

### 6. Triage each comment

For each comment, decide:
- **FIX** — valid concern, make the code change
- **PUSHBACK** — disagree, explain why in the reply

### 7. Fix and push

Make fixes, commit, push to the same branch:

```bash
git add <files>
git commit -m "fix: address review findings"
git push
```

### 8. Reply and resolve

Reply to every comment thread and resolve it. Use batch mode:

```bash
bash ~/.claude/skills/pr-review/scripts/pr-batch.sh --resolve <PR_NUMBER> <<'EOF'
{"comment_id": 123, "body": "Fixed in <sha> — description of fix"}
{"comment_id": 456, "body": "Pushback — reasoning why this is intentional"}
EOF
```

Sign replies with `- Claude`.

### 9. Wait for merge

**Never merge PRs yourself.** Tell the user the PR is ready and wait for them to squash-merge on GitHub.

## Scripts

The pr-review scripts are at `~/.claude/skills/pr-review/scripts/`:

| Script | Purpose |
|--------|---------|
| `pr-comments.sh <PR>` | Fetch all inline review comments with IDs |
| `pr-reply.sh --resolve <PR> <ID> "body"` | Reply to one comment and resolve |
| `pr-batch.sh --resolve <PR>` | Batch reply+resolve from JSONL on stdin |

## Rules

- Every comment thread must be replied to and resolved before declaring PR ready
- Fixed comments: reference the commit SHA in the reply
- Pushback comments: explain reasoning clearly
- Never merge — always wait for human to merge
- Never skip the wait period — reviewers need time
