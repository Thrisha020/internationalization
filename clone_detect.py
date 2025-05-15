"""

Author: Thrisha
CLONE FILE 


"""

import os
import subprocess
import shutil
import argparse
import gettext
from datetime import datetime
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0  # Ensure consistent language detection

LOCALE_PATH = os.path.join(os.path.dirname(__file__), "locale")

# Detect Language
def detect_language(user_input):
    try:
        detected = detect(user_input)
        if detected not in ["fr", "de", "es"]:
            detected = "en"
        print(f"Detected language: {detected}, Using translation: en-{detected}")  # ✅ Proper logging
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
def log_to_file(message, log_file):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{timestamp} - {message}\n"
    with open(log_file, "a") as log:
        log.write(log_message)
    print(log_message)  # ✅ Ensure logs are shown properly

# Clone Repository
def clone_repo(repo_url, clone_path, _):
    try:
        log_to_file(_("Cloning repository..."), log_file)
        subprocess.run(['git', 'clone', repo_url, clone_path], check=True, stderr=subprocess.PIPE)
        log_to_file(_("Repository cloned successfully."), log_file)
        return _("Repository cloned successfully.")
    except subprocess.CalledProcessError as e:
        error_message = _("Error cloning repository.")
        log_to_file(f"{error_message} - {e.stderr.decode().strip()}", log_file)
        return error_message

# Check if Git Repository
def is_git_repo(folder_path):
    return os.path.isdir(os.path.join(folder_path, ".git"))

# Pull Latest Changes with Fixes for "Cannot Lock Ref"
def pull_latest_changes(repo_path, branch, _):
    try:
        log_to_file(_("Repository already cloned. Pulling latest changes..."), log_file)
        subprocess.run(['git', '-C', repo_path, 'fetch', '--prune'], check=True)
        result = subprocess.run(['git', '-C', repo_path, 'pull'], check=True, stderr=subprocess.PIPE)
        log_to_file(_("Latest changes pulled successfully."), log_file)
        return _("Latest changes pulled successfully.")
    except subprocess.CalledProcessError as e:
        error_message = _("Error pulling latest changes.")
        log_to_file(f"{error_message} - {e.stderr.decode().strip()}", log_file)
        subprocess.run(['git', '-C', repo_path, 'reset', '--hard', f'origin/{branch}'], check=False)
        return error_message

# Delete Folder
def delete_folder(folder_path, _):
    permission = input(_("The folder '{folder_path}' is not a git repository. Do you want to delete it? (yes/no): ")).lower()
    if permission == 'yes':
        shutil.rmtree(folder_path)
        log_to_file(_("Folder deleted."), log_file)
        return True
    else:
        log_to_file(_("Operation canceled."), log_file)
        return False

# Main Execution
def main(repo_name, base_url, active_path, user_input, branch="Feature/Demo"):
    global log_file
    selected_lang = detect_language(user_input)
    _ = setup_translation(selected_lang)

    log_file = os.path.join(active_path, "internet_connection_log.txt")
    repo_url = f"{base_url}/{repo_name}.git"
    clone_path = os.path.join(active_path, repo_name)

    if not os.path.isdir(clone_path):
        return clone_repo(repo_url, clone_path, _)

    if is_git_repo(clone_path):
        return pull_latest_changes(clone_path, branch, _)
    else:
        if delete_folder(clone_path, _):
            return clone_repo(repo_url, clone_path, _)
        else:
            return _("Operation canceled.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process repository cloning and updating.")

    parser.add_argument("repo_name", type=str, help="Repository name")
    parser.add_argument("base_url", type=str, help="Base URL of the repository")
    parser.add_argument("active_path", type=str, help="Download directory")
    parser.add_argument("user_input", type=str, help="User input to detect language")
    parser.add_argument("--branch", type=str, default="Feature/Demo", help="Branch to clone")

    args = parser.parse_args()
    result = main(args.repo_name, args.base_url, args.active_path, args.user_input, args.branch)



#  python3 clone_detect.py MortgageApplication https://github.com/gmsadmin-git /Users/thrisham/Desktop/cobol_code/Internationalization "Bonjour" feature/Test-Demo

# python3 clone_detect.py MortgageApplication https://github.com/gmsadmin-git /Users/prabhakaran/Desktop/internationalisation/ "Bonjour"


#        python3 clone_detect.py MortgageApplication https://github.com/gmsadmin-git /Users/prabhakaran/Desktop/internationalisation/ "Buena"
