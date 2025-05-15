import os
import subprocess
import argparse
from datetime import datetime
from deep_translator import GoogleTranslator
import langdetect
from langdetect import detect, DetectorFactory

def log_to_file(message, LOG_FILE):
    """Logs a message to the log file with a timestamp."""
    with open(LOG_FILE, "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} - {message}\n")
        log_file.write("-" * 40 + "\n")  # Separator for readability

def translate(message, target_lang):
    """Translate a message to the target language."""
    if target_lang == "en":
        return message  # No translation needed
    try:
        return GoogleTranslator(source="en", target=target_lang).translate(message)
    except Exception:
        return message  # Fallback to English if translation fails

def detect_language(user_input):
    try:
        detected = detect(user_input)
        if detected not in ["fr", "de", "es"]:
            detected = "en"
        print(f"Detected language: {detected}, Using translation: en-{detected}")
        return detected
    except:
        return "en"  # Default to English if detection fails

def find_file_in_repo(repo_path, file_name, LOG_FILE, detected_lang):
    """Search for the file in the repository folder and subfolders."""
    log_to_file(translate(f"Searching for file '{file_name}' in repository '{repo_path}'", detected_lang), LOG_FILE)
    for root, _, files in os.walk(repo_path):
        if file_name in files:
            file_path = os.path.join(root, file_name)
            log_to_file(translate(f"File found: {file_path}", detected_lang), LOG_FILE)
            return file_path
    log_to_file(translate(f"File '{file_name}' not found in repository '{repo_path}'", detected_lang), LOG_FILE)
    return None

def ensure_on_branch(clone_path, LOG_FILE, detected_lang):
    """Ensure the repository is on a valid branch."""
    try:
        result = subprocess.run(
            ['git', '-C', clone_path, 'symbolic-ref', '--short', 'HEAD'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        current_branch = result.stdout.strip()
        log_to_file(translate(f"Currently on branch: {current_branch}", detected_lang), LOG_FILE)
        return current_branch
    except subprocess.CalledProcessError:
        log_to_file(translate("Repository is in a detached HEAD state.", detected_lang), LOG_FILE)
        new_branch = "fix-detached-head"
        subprocess.run(['git', '-C', clone_path, 'checkout', '-b', new_branch], check=True)
        log_to_file(translate(f"Switched to a new branch: {new_branch}", detected_lang), LOG_FILE)
        return new_branch

def main(repo_name, base_url, file_name, commit_message, active_folder_path, user_input):
    """Main function to clone the repo, find or create the file, and commit changes."""
    LOG_FILE = os.path.join(active_folder_path, "internet_connection_log.txt")

    # Detect user language
    detected_lang = detect_language(user_input)
    log_to_file(f"Detected language: {detected_lang}, Using translation: en-{detected_lang}", LOG_FILE)
    print(translate(f"Detected language: {detected_lang}, Using translation: en-{detected_lang}", detected_lang))

    repo_url = f"{base_url}/{repo_name}.git"
    clone_path = os.path.join(active_folder_path, repo_name)

    log_to_file((f"Starting process for repository: {repo_name}", detected_lang), LOG_FILE)
    print(translate(f"Starting process for repository: {repo_name}", detected_lang))

    if not os.path.exists(clone_path):
        log_to_file((f"Cloning repository from {repo_url} to {clone_path}", detected_lang), LOG_FILE)
        subprocess.run(["git", "clone", repo_url, clone_path], check=True)
        log_to_file(("Repository cloned successfully", detected_lang), LOG_FILE)
    else:
        log_to_file((f"Repository {repo_name} already exists at {clone_path}", detected_lang), LOG_FILE)

    file_path = find_file_in_repo(clone_path, file_name, LOG_FILE, detected_lang)

    if file_path:
        log_to_file((f"File {file_name} found in repository", detected_lang), LOG_FILE)
        print(translate(f"File {file_name} found in repository", detected_lang))
    else:
        file_path = os.path.join(clone_path, file_name)
        open(file_path, 'w').close()
        log_to_file((f"File {file_name} not found. Created new file at {file_path}", detected_lang), LOG_FILE)
        print(translate(f"File {file_name} not found. Created new file at {file_path}", detected_lang))

    # Ensure we are on a valid branch
    current_branch = ensure_on_branch(clone_path, LOG_FILE, detected_lang)

    try:
        log_to_file(("Checking for untracked files", detected_lang), LOG_FILE)
        result = subprocess.run(['git', '-C', clone_path, 'status', '--porcelain'], stdout=subprocess.PIPE, text=True)
        if result.stdout.strip():
            log_to_file(("Staging all changes", detected_lang), LOG_FILE)
            subprocess.run(['git', '-C', clone_path, 'add', '.'], check=True)
        else:
            log_to_file(("No changes to stage", detected_lang), LOG_FILE)
            print(translate("No changes detected. Please make changes before committing.", detected_lang))
            return

        log_to_file(("Staging and committing changes", detected_lang), LOG_FILE)
        subprocess.run(['git', '-C', clone_path, 'commit', '-m', commit_message], check=True)
        log_to_file((f"Committing changes with message: {commit_message}", detected_lang), LOG_FILE)

        log_to_file(translate("Pushing changes to the remote repository", detected_lang), LOG_FILE)
        subprocess.run(['git', '-C', clone_path, 'push', 'origin', current_branch], check=True)
        log_to_file("Changes pushed to the remote repository successfully", detected_lang), LOG_FILE
        print(translate("Changes pushed to the remote repository successfully.", detected_lang))
    except subprocess.CalledProcessError as e:
        log_to_file((f"Error during Git operations: {e}", detected_lang), LOG_FILE)
        print(translate(f"Error processing Git operations: {e}", detected_lang))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process repository name, base URL, file name, commit message, and user input.")
    parser.add_argument("repo_name", type=str, help="The name of the repository to process")
    parser.add_argument("base_url", type=str, help="The base URL of the repository")
    parser.add_argument("file_name", type=str, help="The name of the file to open or create")
    parser.add_argument("commit_message", type=str, help="The commit message for changes")
    parser.add_argument("active_folder_path", type=str, help="The path of the active workspace folder")
    parser.add_argument("user_input", type=str, help="User input to detect language")
    
    args = parser.parse_args()
    main(args.repo_name, args.base_url, args.file_name, args.commit_message, args.active_folder_path, args.user_input)

#  python3 commit_detect.py MortgageApplication https://github.com hello.cbl changedd /Users/thrisham/Desktop/cobol_code/Internationalization "Guten Morgen"