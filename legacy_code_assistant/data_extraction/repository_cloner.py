import git


def clone_repository(repo_url, destination_path):
    """
    Clones a GitHub repository to a specified local path.

    :param repo_url: URL of the GitHub repository to clone.
    :param destination_path: Local path where the repository should be cloned.
    :return: None
    """
    try:
        git.Repo.clone_from(repo_url, destination_path)
        print(f"Repository cloned successfully to {destination_path}")
    except Exception as e:
        print(f"Error occurred while cloning the repository: {e}")
