import subprocess
import os

def clone_and_commit_repo(repo_url: str, commit_message: str, clone_dir: str):
    """
    Clone a Git repository and make a commit.
    """
    try:
        # Clone the repository
        if not os.path.exists(clone_dir):
            print(f"Cloning repository from {repo_url} into {clone_dir}...")
            subprocess.check_call(['git', 'clone', repo_url, clone_dir])

        # Change working directory to the cloned repo
        os.chdir(clone_dir)
        
        # Example: Create a new file or modify an existing one
        with open("new_file.txt", "w") as f:
            f.write("This is a new file added via the automation script.")
        
        # Add and commit changes
        subprocess.check_call(['git', 'add', '.'])
        subprocess.check_call(['git', 'commit', '-m', commit_message])
        
        print(f"Successfully committed changes: {commit_message}")
        return "Successfully cloned and committed to the repo"
    
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return f"Failed to clone and commit: {e}"

# Example Usage
repo_url = "https://github.com/VarunKarthik-18/dataworks-agent.git"  # Actual repo URL
commit_message = "Automated commit: added new file"
clone_dir = "C:/Users/B Varun karthik/dataworks-agent/cloned_repo"  # Actual path for cloning

result = clone_and_commit_repo(repo_url, commit_message, clone_dir)
print(result)
