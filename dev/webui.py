import os
import subprocess
import sys


def main():
    command = ["open-webui", "serve"]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    custom_env = os.environ.copy()

    custom_env["DATA_DIR"] = data_dir
    custom_env["ENABLE_RAG"] = "False"
    custom_env["HF_HUB_OFFLINE"] = "1"
    custom_env["ENABLE_OLLAMA_API"] = "False"

    custom_env["OPENAI_API_BASE_URL"] = "http://localhost:30000/v1"
    custom_env["OPENAI_API_KEY"] = "dummy-key"

    print("Starting open-webui server in lightweight mode...")
    print(f"Data directory set to: {data_dir}")

    try:
        process = subprocess.Popen(command, env=custom_env)
        process.wait()

    except KeyboardInterrupt:
        print("\nInterrupt received. Shutting down...")
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            print("Timeout expired. Forcing shutdown...")
            process.kill()
            process.wait()
        sys.exit(0)

    except FileNotFoundError:
        print("Error: The 'open-webui' executable was not found.")
        print("Ensure you are running this within your uv environment.")
        sys.exit(1)


if __name__ == "__main__":
    main()
