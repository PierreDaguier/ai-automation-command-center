from fastapi import FastAPI

app = FastAPI(title="AI Automation Command Center API")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
