import subprocess
import sys


def main():
    command = [
        "vllm",
        "serve",
        "google/gemma-4-E4B-it",
        "--max-model-len",
        "8192",
        "--limit-mm-per-prompt",
        '{"video": 1, "audio": 1}',
        "--host",
        "0.0.0.0",
        "--port",
        "30000",
    ]

    print("Starting vLLM server...")

    try:
        process = subprocess.Popen(command)
        process.wait()

    except KeyboardInterrupt:
        print("\nInterrupt received. Allowing vLLM to clean up resources...")
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            print("vLLM shutdown timed out. Forcing process kill...")
            process.kill()
            process.wait()
        sys.exit(0)

    except FileNotFoundError:
        print("Error: The 'vllm' executable was not found.")
        print("Ensure you are running this within your uv environment.")
        sys.exit(1)


if __name__ == "__main__":
    main()
