import subprocess

import platform
import os
import time
import requests
import streamlit as st


def update_loading_status(status):
    st.write(status)


def mark_loading_finish() :
    update_loading_status("加载完成！")

__process = None

def auto_destroy_process():
    global  __process
    if __process :
        stop_ollama_server(__process)

def get_process():
    global __process
    if __process: return __process
    __process = setup_ollama()
    return __process



def get_ollama_cli_path():
    """Determine the platform (Windows or macOS) and return the path to the appropriate Ollama CLI."""
    current_directory = os.path.dirname(os.path.abspath(__file__))

    system_platform = platform.system().lower()
    update_loading_status(f"系统平台 {system_platform}")

    # Construct the path based on the platform
    if system_platform == "darwin":  # macOS
        ollama_cli_path = os.path.join(current_directory, 'platform', 'darwin', 'ollama-darwin')
    elif system_platform == "windows":  # Windows
        ollama_cli_path = os.path.join(current_directory, 'platform', 'windows', 'ollama.exe')
    else:
        raise Exception(f"Unsupported platform: {system_platform}")

    # Check if the Ollama CLI exists at the given path
    if not os.path.isfile(ollama_cli_path):
        raise FileNotFoundError(f"Ollama CLI not found at {ollama_cli_path}")

    return ollama_cli_path


def check_model_exists(ollama_cli_path, model_name):
    """Check if the model exists using the 'ollama list' command."""
    try:
        # Run the 'ollama list' command to get the list of available models
        command = [ollama_cli_path, "list"]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Check if the model_name appears in the output
        if model_name in result.stdout:
            return True
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error checking model: {e}")
        return False


def pull_model(ollama_cli_path, model_name):
    """Pull the model using the Ollama CLI if it is not found locally."""
    print(f"Model {model_name} not found. Pulling model...")
    command = [ollama_cli_path, "pull", model_name]

    try:
        subprocess.run(command, check=True)
        print(f"Model {model_name} pulled successfully.")
        update_loading_status("端侧模型文件下载完成！")
    except subprocess.CalledProcessError as e:
        print(f"Error pulling model: {e}")


def start_ollama_serve(ollama_cli_path, model_name):
    """Start the Ollama server using subprocess."""
    command = [ollama_cli_path, "serve"]

    try:
        # Start the Ollama server process
        print(f"Starting Ollama server with command: {' '.join(command)}")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)



        # Allow some time for the server to start
        time.sleep(5)

        return process
    except Exception as e:
        print(f"Error starting Ollama server: {e}")
        return None


def stop_ollama_server(process):
    """Stop the Ollama server by terminating the subprocess."""
    print("Stopping Ollama server...")
    process.terminate()
    try:
        # Wait for the process to terminate and capture any output
        stdout, stderr = process.communicate(timeout=5)
        if stdout:
            print(f"stdout: {stdout.decode()}")
        if stderr:
            print(f"stderr: {stderr.decode()}")
    except subprocess.TimeoutExpired:
        print("Timeout while waiting for process to terminate.")
        process.kill()


def query_ollama_server(model_name, input_text):
    """Query the Ollama server and return the response."""
    url = "http://localhost:11434/api/chat"

    # Construct the structured JSON payload
    payload = {
        "model": model_name,  # Ensure this is the correct model name
        "stream": False,  # False means we want the full response, not streamed
        "messages": [
            {"role": "user", "content": input_text}  # User input message
        ]
    }

    headers = {
        "Content-Type": "application/json"  # Set Content-Type to JSON
    }

    try:
        # Send a POST request to the Ollama server
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response
        else:
            print(f"Error querying Ollama server: {response.text}")
            return None
    except Exception as e:
        print(f"Error making request to Ollama server: {e}")
        return None


def setup_ollama():
    """Run the Ollama server and perform tasks."""
    model_name = "llama3.1:8b"
    update_loading_status(f"开始加载模型 {model_name}")

    try:
        # Get the correct Ollama CLI based on the platform
        ollama_cli_path = get_ollama_cli_path()
        update_loading_status(f"模型服务器位置{ollama_cli_path}")

        # Start the Ollama server
        server_process = start_ollama_serve(ollama_cli_path, model_name)
        update_loading_status("唤醒服务器")

        # Check if the model exists locally, otherwise pull it
        if not check_model_exists(ollama_cli_path, model_name):
            update_loading_status(f"未发现{model_name} 即将开始下载")
            pull_model(ollama_cli_path, model_name)




        if server_process:
            mark_loading_finish()
            return server_process

    except Exception as e:
        print(f"Error during Ollama task: {e}")
