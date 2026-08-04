# SmartCheck — Java port

```bash
cd src && javac SmartCheck.java
java SmartCheck ../../conformance/vectors.json   # batch
java SmartCheck --answer "grew 340%"
```
JDK-only (no dependencies; includes a tiny JSON reader). Verified via `../conformance/run.sh`.
