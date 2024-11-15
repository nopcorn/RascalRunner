# RascalRunner ㊙️

RascalRunner is a command-line red teaming tool designed to deploy malicious workflows to a Github repository covertly. The tool requires a GitHub personal access token (PAT) with `repo` and `workflow` permissions to function properly. 

**If you've found a PAT during a red team engagement, RascalRunner has a "recon" mode that will tell you what is possible with the token (see below)**

It creates a temporary branch, uploads your workflow file, gets it executed, captures the logs, and then automatically cleans up all artifacts - including the temporary branch, workflow runs, and any deployments. This makes it ideal for testing runner-based attacks, secrets leaking, or OIDC abuse without alerting blue team to your actions. 

Check out the sister repository, [RascalRunner-Workflows](https://github.com/nopcorn/RascalRunner-Workflows), for some example workflows. Please keep in mind that RascalRunner is an advanced tool and you can easily mess up deployment and get caught if you don't know what you're doing.

## Features

- Given a PAT, finds repositories you should focus on for pipeline exploitation by checking for available secrets, permissions, and runs
- Uploads a workflow file and kick off a malicious run covertly on a temporary branch
- Automatically downloads run logs when the run completes
- Automatically cleans up evidence of the run, and removes potential deployments the event generated

Github actions are complex enough that if the `recon` or `run` steps fail, it doesn't mean you're cooked. There are also many ways to still mess up a deployment via RascalRunner and get caught by defenders. Be sure you understand the existing workflows in the repository you're targeting and look for clues to security and alerting measures in place.

## Install

```
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
│ Email(s)       │ lol@lol.com, lol+nopcorn@users.noreply.github.com                         │
│ Org(s)         │ figment-networks, BlockchainSecurityStandardsCouncil                      │
│ Token Scopes   │ repo, user, workflow                                                      │
└────────────────┴───────────────────────────────────────────────────────────────────────────┘

Repository Targets (at minimum push permissions)
┌────────────────────────────────────┬─────────────────────────────────────┬─────────────┬──────────┬──────────────────────────────────────────────────────────────┐
│ Target                             │ Permission(s)                       │ Num Secrets │ Num Runs │ Last Run Info                                                │
├────────────────────────────────────┼─────────────────────────────────────┼─────────────┼──────────┼──────────────────────────────────────────────────────────────┤
│ nopcorn/env_test                   │ admin, maintain, push, triage, pull │ 0           │ 10       │ Update env.yaml (Deploy Test) - 2024-10-31T11:40:45Z         │
│ nopcorn/force-push-test            │ admin, maintain, push, triage, pull │ 0           │ 8        │ test (test linter) - 2024-08-29T23:38:59Z                    │
│ nopcorn/githubaudit-vulnerablerepo │ admin, maintain, push, triage, pull │ 1           │ 0        │                                                              │
│ nopcorn/malicious-workflow-test    │ admin, maintain, push, triage, pull │ 1           │ 34       │ Test  (Test prior to running linter) - 2024-08-28T18:42:56Z  │
│ nopcorn/nopcorn.github.io          │ admin, maintain, push, triage, pull │ 0           │ 23       │ pages build and deployment (too long) - 2024-07-18T21:02:32Z │
└────────────────────────────────────┴─────────────────────────────────────┴─────────────┴──────────┴──────────────────────────────────────────────────────────────┘
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
```

Remember that failed runs will automatically send an email to Github repository admins. I recommend adding `continue-on-error: true` to each step in your workflow.

## Some improvements to come

- automatically add `continue-on-error: true` to all steps to prevent failed runs from alerting
- add support for environments
    - find secrets in environments without protection rules
    - allow for injecting a workflow in an environment from the command line
- add job and workflow ids to verbose logging
- make the temporary branch name configurable
- allow renaming the workflow file from the command line
- allow for customized commit messages
- implement double commits to make it a bit harder to find the malicious code
- support a max run time before the RascalRunner will kill the run

## Contributing

Happy to review and accept fixes and enhancements. Open a PR.
