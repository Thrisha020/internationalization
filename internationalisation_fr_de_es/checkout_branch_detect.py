"""

Author: Thrisha
CHECKOUT FILE 


"""



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

# Check if Git Repository
def is_git_repo(folder_path, LOG_FILE):
    """Check if a folder is a valid Git repository."""
    is_repo = os.path.isdir(os.path.join(folder_path, ".git"))
    log_to_file(_("Checked if {folder_path} is a Git repository: {is_repo}").format(folder_path=folder_path, is_repo=is_repo), LOG_FILE)
    return is_repo

# List Git Branches
def list_branches(repo_path, LOG_FILE):
    """List all available branches in the repository."""
    try:
        result = subprocess.run(['git', '-C', repo_path, 'branch', '-a'], check=True, text=True, capture_output=True)
        branches = result.stdout.strip().split('\n')
        log_to_file(_("Listed branches in repository {repo_path}.").format(repo_path=repo_path), LOG_FILE)
        return branches
    except subprocess.CalledProcessError as e:
        log_to_file(_("Error listing branches in {repo_path}: {error}").format(repo_path=repo_path, error=e), LOG_FILE)
        return []

# Checkout Git Branch
def checkout_branch(repo_path, branch_name, LOG_FILE):
    """Try to checkout a branch, handle errors, and fallback if needed."""
    try:
        subprocess.run(['git', '-C', repo_path, 'checkout', branch_name], check=True)
        message = _("Checked out branch '{branch_name}'.").format(branch_name=branch_name)
        log_to_file(message, LOG_FILE)
        return message
    except subprocess.CalledProcessError as e:
        log_to_file(_("Error checking out branch '{branch_name}': {error}").format(branch_name=branch_name, error=e), LOG_FILE)
        fallback_branch = "main"  
        try:
            subprocess.run(['git', '-C', repo_path, 'checkout', fallback_branch], check=True)
            message = _("Checked out fallback branch '{fallback_branch}' successfully.").format(fallback_branch=fallback_branch)
            log_to_file(message, LOG_FILE)
            return message
        except subprocess.CalledProcessError as fallback_error:
            log_to_file(_("Failed to checkout both '{branch_name}' and fallback branch '{fallback_branch}'.").format(branch_name=branch_name, fallback_branch=fallback_branch), LOG_FILE)
            return _("Failed to checkout both '{branch_name}' and fallback branch '{fallback_branch}'.").format(branch_name=branch_name, fallback_branch=fallback_branch)

# Push Git Branch
def push_branch(repo_path, branch_name, LOG_FILE):
    """Push a new branch to the remote repository."""
    try:
        subprocess.run(['git', '-C', repo_path, 'push', '-u', 'origin', branch_name], check=True)
        message = _("Branch '{branch_name}' pushed to remote repository.").format(branch_name=branch_name)
        log_to_file(message, LOG_FILE)
        print(message)
    except subprocess.CalledProcessError as e:
        log_to_file(_("Error pushing branch '{branch_name}': {error}").format(branch_name=branch_name, error=e), LOG_FILE)

# Main Execution
def main(repo_name, base_url, branch_name, active_path, user_input):
    """Main function to process the repository."""
    selected_lang = detect_language(user_input)
    global _  # Set the global translation function
    _ = setup_translation(selected_lang)

    LOG_FILE = os.path.join(active_path, "internet_connection_log.txt")
    repo_url = f"{base_url}/{repo_name}.git"
    clone_path = os.path.join(active_path, repo_name)

    if not is_git_repo(clone_path, LOG_FILE):
        message = _("Error: {clone_path} is not a valid Git repository.").format(clone_path=clone_path)
        log_to_file(message, LOG_FILE)
        return message

    return checkout_branch(clone_path, branch_name, LOG_FILE)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process repository name and base URL.")
    parser.add_argument("repo_name", type=str, help="The name of the repository to process")
    parser.add_argument("base_url", type=str, help="The base URL of the repository")
    parser.add_argument("branch_name", type=str, help="The branch to checkout to")
    parser.add_argument("active_path", type=str, help="It will download in the current path")
    parser.add_argument("user_input", type=str, help="User input to detect language")

    args = parser.parse_args()
    print(main(args.repo_name, args.base_url, args.branch_name, args.active_path, args.user_input))


#   python3 checkout_branch_detect.py MortgageApplication https://github.com/gmsadmin-git Feature/Demo /Users/thrisham/Desktop/cobol_code/Internationalization "Guten Morgen"
