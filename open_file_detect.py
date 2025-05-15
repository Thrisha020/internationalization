import os
import subprocess
import argparse
import gettext
from datetime import datetime
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0  # Ensures consistent language detection

# Define locale path for translations
LOCALE_PATH = os.path.join(os.path.dirname(__file__), "locale")

# Detect Language
def detect_language(user_input):
    try:
        detected = detect(user_input)
        if detected not in ["fr", "de", "es"]:
            detected = "en"
        print(f"Detected language: {detected}, Using translation: en-{detected}")
        return detected
    except:
        return "en"

# Setup Translation
def setup_translation(selected_lang):
    output_lang = f"en-{selected_lang}"
    translation = gettext.translation(
        "messages", localedir=LOCALE_PATH, languages=[output_lang], fallback=True
    )
    translation.install()
    return translation.gettext

# Log Messages
def log_to_file(message, LOG_FILE):
    """Logs a message to the log file with a timestamp."""
    with open(LOG_FILE, "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} - {message}\n")
        log_file.write("-" * 40 + "\n")
    print(message)  # Ensure messages are printed

# Find File in Repo
def find_file_in_repo(repo_path, file_name, LOG_FILE):
    """Search for the file in the repo and return its path if found."""
    log_to_file(_("Searching for file '{file_name}' in repository '{repo_path}'").format(file_name=file_name, repo_path=repo_path), LOG_FILE)
    for root, dirs, files in os.walk(repo_path):
        if file_name in files:
            file_path = os.path.join(root, file_name)
            log_to_file(_("File found: {file_path}").format(file_path=file_path), LOG_FILE)
            return file_path
    log_to_file(_("File '{file_name}' not found in repository '{repo_path}'").format(file_name=file_name, repo_path=repo_path), LOG_FILE)
    return None

# Open in VSCode
def open_in_vscode(file_path, LOG_FILE):
    """Open the file in VSCode."""
    try:
        log_to_file(_("Attempting to open file in VSCode: {file_path}").format(file_path=file_path), LOG_FILE)
        subprocess.run(["code", file_path], check=True)
        log_to_file(_("File opened successfully in VSCode: {file_path}").format(file_path=file_path), LOG_FILE)
        return _( "Successfully opened: {file_path}").format(file_path=file_path)
    except FileNotFoundError:
        log_to_file(_("VSCode not installed"), LOG_FILE)
        return _("VSCode not installed")
    except subprocess.CalledProcessError as e:
        log_to_file(_("Error opening file in VSCode: {error}").format(error=e), LOG_FILE)
        return _("Error opening file in VSCode: {error}").format(error=e)

# Main Execution
def main(repo_name, base_url, file_name, active_folder_path, user_input):
    """Main function to process the repository."""
    selected_lang = detect_language(user_input)
    global _  # Set the global translation function
    _ = setup_translation(selected_lang)

    LOG_FILE = os.path.join(active_folder_path, "internet_connection_log.txt")
    repo_url = f"{base_url}/{repo_name}.git"
    clone_path = os.path.join(active_folder_path, repo_name)

    log_to_file(_("Starting process for repository: {repo_name} at {base_url}").format(repo_name=repo_name, base_url=base_url), LOG_FILE)
    log_to_file(_("Local repository path: {clone_path}").format(clone_path=clone_path), LOG_FILE)

    file_path = find_file_in_repo(clone_path, file_name, LOG_FILE)
    if file_path:
        result = open_in_vscode(file_path, LOG_FILE)
        log_to_file(result, LOG_FILE)
        return result
    else:
        message = _("File '{file_name}' not found in repository '{repo_name}'.").format(file_name=file_name, repo_name=repo_name)
        log_to_file(message, LOG_FILE)
        return message

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process repository name, base URL, file name, and active folder path.")
    parser.add_argument("repo_name", type=str, help="The name of the repository to process")
    parser.add_argument("base_url", type=str, help="The base URL of the repository")
    parser.add_argument("file_name", type=str, help="The name of the file which is to open")
    parser.add_argument("active_folder_path", type=str, help="The path of the active workspace folder")
    parser.add_argument("user_input", type=str, help="User input to detect language")
    
    args = parser.parse_args()
    print(main(args.repo_name, args.base_url, args.file_name, args.active_folder_path, args.user_input))


#  python3 open_file_detect.py MortgageApplication https://github.com/gmsadmin-git hello.cbl /Users/thrisham/Desktop/cobol_code/Internationalization "Bonjour"

# Guten Morgen

# Bonjour