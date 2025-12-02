import tempfile
import logging
import shutil
import yaml
import time
import os
import io
import re
import zipfile
from git import Repo, Actor

class RascalRunner:

    def __init__(self, target, workflow, wrapper, branch_name, commit_message, only_delete_logs):
        self._target = target
        self._workflow = workflow
        self._branch_name = branch_name
        self._commit_message = commit_message
        self._only_delete_logs = only_delete_logs
        self._github_wrapper = wrapper

    @property
    def target(self):
        return self._target
    
    @target.setter
    def target(self, target):
        if "/" not in target:
            raise Exception("Target repository doesn't contain a Github account. Please provide in the 'account/repo' format.")
        self._target = target
    
    @property
    def workflow(self):
        return self._workflow
    
    @workflow.setter
    def workflow(self, workflow):
        try:
            with open(workflow, "r") as fh:
                try:
                    config = yaml.safe_load(fh)
                    self._workflow = workflow
                except Exception as e:
                    raise Exception(f"Workflow file doesn't contain valid YAML: {e}")
        except Exception as e:
            raise Exception(f"Couldn't open workflow file: {e}")


    def _clone_repository(self):
        self._tmp_dir = tempfile.TemporaryDirectory()
        logging.debug(f"Created tmp directory {self._tmp_dir.name}")
        repo_url = f"https://{self._github_wrapper._token}@github.com/{self._target}.git"
        try:
            self._repo = Repo.clone_from(repo_url, self._tmp_dir.name)
            logging.debug(f"Cloned {repo_url} to {self._tmp_dir.name}")
        except Exception as e:
            raise Exception(f"Failed to clone repository: {e}")


    def _push_workflow(self):
        branch = self._repo.create_head(self._branch_name).checkout()
        self._branch = branch

        # remove existing workflows to make sure we don't trigger anything
        shutil.rmtree(f"{self._tmp_dir.name}/.github/workflows/")
        self._repo.index.remove([f"{self._tmp_dir.name}/.github/workflows/"], working_tree=True, r=True)
        os.mkdir(f"{self._tmp_dir.name}/.github/workflows/")
        logging.debug(f"Removed any previously committed workflow files from .github/workflows")
        os.makedirs(f"{self._tmp_dir.name}/.github/workflows/", exist_ok=True)

        workflow_basename = os.path.basename(self._workflow)
        shutil.copy2(self._workflow, f"{self._tmp_dir.name}/.github/workflows/{workflow_basename}")

        self._repo.git.add(f".github/workflows/{workflow_basename}")
        self._repo.git.commit("-m", self._commit_message)

        remote = self._repo.remote("origin")
        remote.push(refspec=f"{self._branch_name}:{self._branch_name}", set_upstream=True)

        logging.info(f"Pushed new branch to remote with provided workflow")


    def _delete_deployments(self):
        gh_repo = self._github_wrapper.github.get_repo(self._target)
        deployments = gh_repo.get_deployments(ref=self._branch_name)
        logging.info(f"Found {deployments.totalCount} deployments associated with the workflow")
        for deployment in deployments:
            deployment.create_status(state="inactive")
            logging.info(f"Marked deployment with id={deployment.id} as inactive")
            resp = self._github_wrapper.api_call("DELETE", deployment.url)
            if resp.status_code != 204:
                logging.info(f"Could not delete deployment with id={deployment.id} - please clean up manually")
            else:
                logging.info(f"Cleaned up deployment with id={deployment.id}")


    def _remove_remote_branch(self):
        remote = self._repo.remote("origin")
        remote.push(refspec=(f":refs/heads/{self._branch_name}"))
        logging.info(f"Removed remote branch")


    def _download_run_logs(self, run_logs_url):
        resp = self._github_wrapper.api_call("GET", run_logs_url)
        zip_buf = io.BytesIO(resp.content)

        with zipfile.ZipFile(zip_buf, "r") as zip_ref:
            # extract the 0_<job_name>.txt file from the downloaded zip - throw out the rest
            pattern = re.compile(r"0_.*\.txt$")
            matches = [name for name in zip_ref.namelist() if pattern.match(name)]
            if matches:
                zipped_name = matches[0]
                output_bytes = zip_ref.read(zipped_name)

                repo_name = self._github_wrapper._github.get_repo(self._target).name
                workflow_filename = os.path.basename(self._workflow).split(".")[0]
                with open(f"{repo_name}-{workflow_filename}-{int(time.time())}.txt", "wb") as output_file:
                    output_file.write(output_bytes)
                    logging.info(f"Wrote workflow output to {workflow_filename}")


    def _wait_for_workflow(self):
        gh_repo = self._github_wrapper.github.get_repo(self._target)
        while True:
            # once we find a single workflow run, we know the code correctly kicked off a run and remove the branch remotely
            logging.debug(f"Waiting for workflow job to get kicked off")
            time.sleep(3)
            run = next(iter(gh_repo.get_workflow_runs(branch=self._branch_name)), None)
            if run:
                self._remove_remote_branch()
                logging.info(f"Found a running job, waiting for it to exit")
                while True:
                    time.sleep(3)
                    run = next(iter(gh_repo.get_workflow_runs(branch=self._branch_name)), None)
                    if run.status == "completed":
                        logging.info(f"Job completed")
                        self._download_run_logs(run.logs_url)
                        if self._only_delete_logs:
                            resp = self._github_wrapper.api_call("DELETE", run.logs_url)
                            if resp.status_code != 204:
                                logging.info(f"Could not remove run logs - please clean up manually")
                            else:
                                logging.info(f"Removed run logs")
                        else:
                            run.delete()
                            logging.info(f"Removed workflow and logs from the github UI")
                        return


    def _cleanup(self):
        self._tmp_dir.cleanup()


    def run(self):
        self._clone_repository()
        self._push_workflow()
        self._wait_for_workflow()
        self._delete_deployments()
        self._cleanup()
        return