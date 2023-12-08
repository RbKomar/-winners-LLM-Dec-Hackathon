import os

import git


def extract_code_files(repo_path, file_types=('.py',)):
    """
    Extracts code files from the repository.

    :param repo_path: Path to the cloned repository.
    :param file_types: Tuple of file extensions to consider as code files.
    :return: List of paths to the code files.
    """
    code_files = []
    for root, dirs, files in os.walk(repo_path):
        code_files.extend(os.path.join(root, file) for file in files if file.endswith(file_types))
    return code_files


def extract_documentation(repo_path, doc_types=('.md', '.txt')):
    """
    Extracts documentation files from the repository.

    :param repo_path: Path to the cloned repository.
    :param doc_types: Tuple of file extensions to consider as documentation.
    :return: List of paths to the documentation files.
    """
    doc_files = []
    for root, dirs, files in os.walk(repo_path):
        doc_files.extend(os.path.join(root, file) for file in files if file.endswith(doc_types))
    return doc_files


def extract_commit_history(repo_path):
    """
    Extracts the commit history from the repository.

    :param repo_path: Path to the cloned repository.
    :return: List of dictionaries containing commit information.
    """
    try:
        repo = git.Repo(repo_path)
        commits = []
        for commit in repo.iter_commits():
            commit_data = {'author': commit.author.name, 'email': commit.author.email, 'date': commit.authored_datetime,
                           'message': commit.message.strip()}
            commits.append(commit_data)
        return commits
    except Exception as e:
        print(f"Error occurred while extracting commit history: {e}")
        return []
