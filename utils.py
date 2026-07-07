import time


def process_response(response, flush_interval=0.1):
    """Relay an SSE response as batched chunks.

    Each yield becomes one RunPod stream update, and those updates are
    rate-limited to a few per second. Yielding per SSE event caps client
    throughput at that update rate, so events are passed through verbatim
    and flushed together on a time window instead.
    """
    buffer = []
    last_flush = time.monotonic()
    for line in response.iter_lines():
        if not line:
            continue
        decoded = line.decode("utf-8").strip()
        if not decoded.startswith("data:"):
            decoded = f"data: {decoded}"
        buffer.append(decoded + "\n\n")
        now = time.monotonic()
        if now - last_flush >= flush_interval:
            yield "".join(buffer)
            buffer = []
            last_flush = now
    if buffer:
        yield "".join(buffer)
