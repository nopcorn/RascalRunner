import tempfile
import logging
import os
import shutil
import yaml
from git import Repo, Actor

class GitlabRunner:
    def __init__(self, target, pipeline_file, wrapper, branch_name, commit_message, only_delete_logs):
        self._target = target           # "group/project"
        self._pipeline_file = pipeline_file
        self._branch_name = branch_name
        self._commit_message = commit_message
        self._only_delete_logs = only_delete_logs
        self._gitlab_wrapper = wrapper

    def _clone_repository(self):
        self._tmp_dir = tempfile.TemporaryDirectory()
        repo_url = f"https://oauth2:{self._gitlab_wrapper._token}@gitlab.com/{self._target}.git"
        self._repo = Repo.clone_from(repo_url, self._tmp_dir.name)
        logging.info(f"Cloned repo to {self._tmp_dir.name}")

    def _push_pipeline(self):
        branch = self._repo.create_head(self._branch_name).checkout()
        shutil.copy2(self._pipeline_file, f"{self._tmp_dir.name}/.gitlab-ci.yml")
        author_name = self._repo.head.commit.author.name
        author_email = self._repo.head.commit.author.email
        actor = Actor(author_name, author_email)
        self._repo.git.add(".gitlab-ci.yml")
        self._repo.index.commit(self._commit_message, author=actor, committer=actor)
        remote = self._repo.remote("origin")
        remote.push(refspec=f"{self._branch_name}:{self._branch_name}")
        logging.info("Pushed branch with pipeline to remote")

    def _trigger_pipeline(self):
        # Trigger job & wait; for real-world: monitor / merge MR, etc.
        logging.info("NOTE: This is a stub - expand for full job/pipeline execution monitoring.")

    def _cleanup(self):
        # Optionally remove remote branch / pipeline / logs
        logging.info("NOTE: This is a stub - expand for full cleanup logic.")

    def run(self):
        self._clone_repository()
        self._push_pipeline()
        self._trigger_pipeline()
        self._cleanup()
