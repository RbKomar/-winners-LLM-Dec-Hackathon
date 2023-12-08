import os

import git

from data_extraction.data_extractor import extract_code_files, extract_commit_history, extract_documentation
from data_extraction.repository_cloner import clone_repository


def test_clone_repository_success(mocker):
    mocker.patch("git.Repo.clone_from")
    clone_repository("https://github.com/adigunsherif/Django-School-Management-System.git", "tests/test_repo")
    git.Repo.clone_from.assert_called_once_with("https://github.com/adigunsherif/Django-School-Management-System.git",
                                                "tests/test_repo")


def test_extract_code_files(mocker):
    mocker.patch("os.walk", return_value=[('root', 'dirs', ['file.py', 'file.txt'])])
    files = extract_code_files("tests/test_repo", ('.py',))
    assert files == [os.path.join('root', 'file.py')]


def test_extract_documentation(mocker):
    mocker.patch("os.walk", return_value=[('root', 'dirs', ['file.py', 'file.txt', 'README.md'])])
    files = extract_documentation("tests/test_repo", ('.md',))
    assert files == [os.path.join('root', 'README.md')]


def test_extract_commit_history_success(mocker):
    commit = mocker.Mock()
    commit.author.name = "Author"
    commit.author.email = "author@example.com"
    commit.authored_datetime = "2023-04-01 12:00:00"
    commit.message = "commit message"
    mocker.patch("git.Repo", return_value=mocker.Mock(iter_commits=mocker.Mock(return_value=iter([commit]))))
    commits = extract_commit_history("tests/test_repo")
    assert commits == [
        {'author': 'Author', 'email': 'author@example.com', 'date': '2023-04-01 12:00:00', 'message': 'commit message'}]


def test_extract_commit_history_failure(mocker):
    mocker.patch("git.Repo", side_effect=Exception("Error occurred while extracting commit history"))
    commits = extract_commit_history("tests/test_repo")
    assert commits == []
