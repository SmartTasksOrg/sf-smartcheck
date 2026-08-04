# SmartCheck — Go port

```bash
go run main.go ../conformance/vectors.json     # batch
go run main.go --answer "grew 340%" --sources ""
```
Standard library only (RE2 regex, encoding/json). Verified via `../conformance/run.sh`.
