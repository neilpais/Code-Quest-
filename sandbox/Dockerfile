FROM python:3.11-slim

RUN useradd -m sandboxuser
WORKDIR /workspace
USER sandboxuser

CMD ["python3", "solution.py"]
