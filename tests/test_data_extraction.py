import unittest
from unittest import mock
from legacy_code_assistant.data_extraction.repository_cloner import clone_repository

repo_url = 'https://github.com/adigunsherif/Django-School-Management-System.git'
dest_path = './test_repo'


class TestRepositoryCloner(unittest.TestCase):

    @mock.patch("repository_cloner.git.Repo")
    def test_clone_repository(self, mock_repo):
        # No Exception scenario
        clone_repository(repo_url, dest_path)
        mock_repo.clone_from.assert_called_once_with(repo_url, dest_path)

    @mock.patch("repository_cloner.git.Repo")
    def test_clone_repository_exception(self, mock_repo):
        repo_url = "https://github.com/user/repo.git"
        dest_path = "/path/to/destination"

        # Scenario when exception is raised
        mock_repo.clone_from.side_effect = Exception("Error in cloning")
        with self.assertRaises(Exception) as context:
            clone_repository(repo_url, dest_path)

        self.assertTrue("Error in cloning" in str(context.exception))


if __name__ == "__main__":
    unittest.main()
