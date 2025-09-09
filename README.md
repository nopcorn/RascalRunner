# RascalRunner ㊙️

RascalRunner is a command-line red teaming tool designed to deploy malicious workflows to a Github repository covertly. The tool requires a GitHub personal access token (PAT) with `repo` and `workflow` permissions to function properly.

**If you've found a PAT during a red team engagement, RascalRunner has a "recon" mode that will tell you what is possible with the token (see below)**

It creates a temporary branch, uploads your workflow file, gets it executed, captures the logs, and then automatically cleans up all artifacts - including the temporary branch, workflow runs, and any deployments. This makes it ideal for testing runner-based attacks, secrets leaking, or OIDC abuse without alerting blue team to your actions.

Check out the sister repository, [RascalRunner-Workflows](https://github.com/nopcorn/RascalRunner-Workflows), for some example workflows. Please keep in mind that RascalRunner is an advanced tool and you can easily mess up deployment and get caught if you don't know what you're doing.

## Features

- Given a PAT (classic or fine-grained), finds repositories you should focus on for pipeline exploitation by checking for available secrets, permissions, and runs
- Uploads a workflow file and kick off a malicious run covertly on a temporary branch
- Automatically downloads run logs when the run completes
- Automatically cleans up evidence of the run, and removes potential deployments the event generated. Also supports only removing run logs but leaving the workflow to avoid some blue team detections.

Github actions are complex enough that if the `recon` or `run` steps fail, it doesn't mean you're cooked. There are also many ways to still mess up a deployment via RascalRunner and get caught by defenders. Be sure you understand the existing workflows in the repository you're targeting and look for clues to security and alerting measures in place.

## Install

```
mkdir working && cd working
python -m venv venv
source venv/bin/activate
pip install rascalrunner
```

## Usage

Use in recon mode if you've found a Github PAT but are unsure how to leverage it. Output will show details about the token and curate a list of potential repository targets (ones that have workflows set up or with secrets)

```shell
$ rascalrunner recon --auth GITHUB_PAT

Token Information                                                                             
┌────────────────┬───────────────────────────────────────────────────────────────────────────┐
│ Key            │ Value                                                                     │
├────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ Owner          │ nopcorn (@nopcorn)                                                        │
│ Account Type   │ User                                                                      │
│ 2FA Configured │ Yes                                                                       │
│ Email(s)       │ lol@lol.com, 143365389+nopcorn@users.noreply.github.com                   │
│ Org(s)         │ testorg                                                                   │
│ Token Scopes   │ repo, user, workflow                                                      │
└────────────────┴───────────────────────────────────────────────────────────────────────────┘
                                                                                                                                                                                                                     
Repository Targets                                                                                                                                                                                                                          
┌──────────────────────────────────────────────────────┬───────────────────┬─────────────────────────────────────┬─────────────┬──────────┬────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Target                                               │ Status            │ Permission(s)                       │ Num Secrets │ Num Runs │ Last Run Info                                                                                  │
├──────────────────────────────────────────────────────┼───────────────────┼─────────────────────────────────────┼─────────────┼──────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤
│ nopcorn/artifact-exploit-poc                         │ Public            │ admin, maintain, push, triage, pull │ 0           │ 27       │ Vulnerable Workflow (Vulnerable Workflow) - 2025-05-27T00:01:33Z                               │
│ nopcorn/auto-merge-test                              │ Private, Archived │ admin, maintain, push, triage, pull │ 0           │ 0        │                                                                                                │
│ nopcorn/CuteRAT                                      │ Public            │ admin, maintain, push, triage, pull │ 0           │ 0        │                                                                                                │
│ nopcorn/DuckDuckC2                                   │ Public            │ admin, maintain, push, triage, pull │ 0           │ 0        │                                                                                                │
│ nopcorn/env_test                                     │ Public            │ admin, maintain, push, triage, pull │ 0           │ 10       │ Update env.yaml (Deploy Test) - 2024-10-31T11:40:45Z                                           │
│ nopcorn/gha-intercept                                │ Public            │ admin, maintain, push, triage, pull │ 0           │ 0        │                                                                                                │
│ nopcorn/githubaudit                                  │ Public            │ admin, maintain, push, triage, pull │ 0           │ 0        │                                                                                                │
│ nopcorn/githubaudit-vulnerablerepo                   │ Public            │ admin, maintain, push, triage, pull │ 1           │ 0        │                                                                                                │
│ nopcorn/hacktricks-cloud                             │ Public            │ admin, maintain, push, triage, pull │ 0           │ 0        │                                                                                                │
│ nopcorn/nopcorn                                      │ Public            │ admin, maintain, push, triage, pull │ 0           │ 0        │                                                                                                │
│ nopcorn/nopcorn.github.io                            │ Public            │ admin, maintain, push, triage, pull │ 0           │ 20       │ pages build and deployment (pages build and deployment) - 2025-05-27T00:54:15Z                 │
│ nopcorn/RascalRunner                                 │ Public            │ admin, maintain, push, triage, pull │ 0           │ 0        │                                                                                                │
│ nopcorn/RascalRunner-Workflows                       │ Public            │ admin, maintain, push, triage, pull │ 0           │ 0        │                                                                                                │
│ nopcorn/redteam-stuff                                │ Private           │ admin, maintain, push, triage, pull │ 0           │ 51       │ try out linter temporarily (Test prior to running linter) - 2024-05-28T14:59:35Z               │
│ nopcorn/workflow-test                                │ Private           │ admin, maintain, push, triage, pull │ 1           │ 24       │ deploy (deploy) - 2025-05-30T14:07:55Z                                                         │
└──────────────────────────────────────────────────────┴───────────────────┴─────────────────────────────────────┴─────────────┴──────────┴────────────────────────────────────────────────────────────────────────────────────────────────┘
```

When you've found a target, invoke the `run` mode and supply a malicious workflow for inclusion into the remote target

```
$ rascalrunner run -a GITHUB_PAT -t nopcorn/githubaudit-vulnerablerepo -w ./dump-secrets.yaml

2024-11-06 10:32:44,074 Pushed new branch to remote with provided workflow
2024-11-06 10:32:51,345 Removed remote branch
2024-11-06 10:32:51,345 Found a running job, waiting for it to exit
2024-11-06 10:32:57,794 Job completed
2024-11-06 10:32:58,633 Wrote workflow output to nopcorn-dump-secrets-1730907178.txt
2024-11-06 10:32:59,357 Removed workflow from the github UI
2024-11-06 10:33:00,191 Found 0 deployments associated with the workflow

$ cat nopcorn-dump-secrets-1730907178.txt 
<run output>
</run>
```

Remember that failed runs will automatically send an email to Github repository admins. I recommend adding `continue-on-error: true` to each step in your workflow.

### GitLab Reconnaissance (Self-hosted or Public Instance)

RascalRunner also supports GitLab instances for reconnaissance operations. Use the `glrecon` command to analyze GitLab projects and tokens:

```shell
$ rascalrunner glrecon --gitlab-url https://gitlab.example.com/api/v4 --auth GITLAB_TOKEN
```

The `--gitlab-url` parameter specifies the GitLab instance URL (use https://gitlab.com for the public GitLab instance). The `--show-all` flag displays comprehensive information including all accessible projects and detailed permissions.

The output will show token information, accessible projects, and permission levels, helping identify potential targets for pipeline exploitation. The permissions output includes project access levels, group memberships, and available CI/CD variables.

<img width="849" height="457" alt="image" src="https://github.com/user-attachments/assets/6935c0eb-2351-4f32-aece-9152fd998344" />

## Some improvements to come

- automatically add `continue-on-error: true` to all steps to prevent failed runs from alerting
- add support for environments
    - find secrets in environments without protection rules
    - allow for injecting a workflow in an environment from the command line
- add job and workflow ids to verbose logging
- allow renaming the workflow file from the command line
- support a max run time before the RascalRunner will kill the run

## Contributing

Happy to review and accept fixes and enhancements. Open a PR.
