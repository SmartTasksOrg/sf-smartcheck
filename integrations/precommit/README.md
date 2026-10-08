# SmartCheck — pre-commit

This repo ships [`.pre-commit-hooks.yaml`](../../.pre-commit-hooks.yaml). Add to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/SmartTasksOrg/smartcheck
  rev: v3.0.0
  hooks: [{id: smartcheck}]
```
