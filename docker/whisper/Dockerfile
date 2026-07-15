FROM python:3.11-slim

# watch.py always uploads mono mp3 — no ffmpeg needed in the container.
RUN pip install --no-cache-dir \
    faster-whisper==1.1.1 \
    fastapi==0.115.12 \
    uvicorn==0.34.0 \
    python-multipart==0.0.20 \
    requests==2.32.3 \
    huggingface-hub==0.29.3 \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app
COPY server.py .

ENV WHISPER_MODEL=base \
    WHISPER_DEVICE=cpu \
    WHISPER_COMPUTE_TYPE=int8 \
    WHISPER_THREADS=4

EXPOSE 9000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "9000"]
