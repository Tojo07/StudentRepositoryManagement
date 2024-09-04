import os
import subprocess

# Prompt the user for the directory containing student repositories
hw_submissions_dir = input(
    "Enter the directory containing student repositories (e.g., /Users/hamiltonn/assignment-name-submissions): ")
deadline = input("enter the deadline of the assignment in format yyyy-mm-dd: ")
deadline = "".join(deadline.split(" "))
print(deadline)
deadline = deadline.split("-")
deadline_year = deadline[0]
deadline_month = deadline[1]
deadline_day = deadline[-1]

# Initialize a dictionary to store repositories with issues
repo_issues = {}
missed_deadline = []

# Iterate over each directory in the hw_submissions_dir
for repo_dir in os.listdir(hw_submissions_dir):
    repo_path = os.path.join(hw_submissions_dir, repo_dir)
    if os.path.isdir(repo_path):
        print(f"Checking repository in {repo_path}")

        try:
            # Change to the repository directory
            os.chdir(repo_path)

            # Check if the directory is a valid git repository
            if not os.path.exists(".git"):
                repo_issues[repo_dir] = "Not a valid git repository"
                continue

            # Fetch all branches
            subprocess.run(["git", "fetch", "--all"], check=True)

            # Determine the branch with the latest commit and trim whitespace
            try:
                latest_branch = \
                    subprocess.check_output(["git", "branch", "-r", "--sort=-committerdate"]).decode().split("\n")[
                        0].replace("HEAD -> ", "").replace("origin/", "").strip()
                print(latest_branch)
            except subprocess.CalledProcessError:
                repo_issues[repo_dir] = "Failed to determine the latest branch"
                continue

            # Checkout the branch with the latest commit
            try:
                subprocess.run(["git", "checkout", latest_branch], check=True)
            except subprocess.CalledProcessError:
                repo_issues[repo_dir] = f"Branch '{latest_branch}' does not exist"
                continue

            # Update the branch to the latest version from the remote
            subprocess.run(
                ["git", "pull", "origin", latest_branch], check=True)

            """
            check if latest commit is within the deadline.
            Note: Students have up to 7 days after deadline to submit assignments
            """
            commit_time = subprocess.run(
                ["git", "log", "-1", "--format=%cs", "."], capture_output=True)
            commit_time = commit_time.stdout.decode("utf-8")
            commit_time = commit_time.split("-")
            commit_year = commit_time[0]
            commit_month = commit_time[1]
            commit_day = commit_time[-1]

            if int(commit_year) > int(deadline_year) and repo_dir not in missed_deadline:
                missed_deadline.append(repo_dir)

            else:
                if int(commit_month) > int(deadline_month) and repo_dir not in missed_deadline:
                    missed_deadline.append(repo_dir)

                elif int(commit_day) > int(deadline_day) and repo_dir not in missed_deadline:
                    if int(commit_day) - int(deadline_day) > 7:
                        missed_deadline.append(repo_dir)

        except subprocess.CalledProcessError as e:
            repo_issues[repo_dir] = f"Error: {str(e)}"

        finally:
            # Change back to the hw_submissions_dir before processing the next repository
            os.chdir(hw_submissions_dir)

# Print the summary of repositories with issues
if repo_issues:
    print("\nRepositories with issues:")
    for repo, issue in repo_issues.items():
        print(f"{repo}: {issue}")
else:
    print("\nAll repositories have been updated successfully.")

print("********************************************************")

if missed_deadline:
    print("\nThe following repositories missed the deadline:")
    for repo in missed_deadline:
        print("\n" + repo)
