import argparse
import sys
import logging
import random
import string
from .github_wrapper import GithubWrapper
from .rascalrunner import RascalRunner
from .reconrunner import ReconRunner

ascii_banner = """
 ██▀███   ▄▄▄        ██████  ▄████▄   ▄▄▄       ██▓        ██▀███   █    ██  ███▄    █  ███▄    █ ▓█████  ██▀███  
▓██ ▒ ██▒▒████▄    ▒██    ▒ ▒██▀ ▀█  ▒████▄    ▓██▒       ▓██ ▒ ██▒ ██  ▓██▒ ██ ▀█   █  ██ ▀█   █ ▓█   ▀ ▓██ ▒ ██▒
▓██ ░▄█ ▒▒██  ▀█▄  ░ ▓██▄   ▒▓█    ▄ ▒██  ▀█▄  ▒██░       ▓██ ░▄█ ▒▓██  ▒██░▓██  ▀█ ██▒▓██  ▀█ ██▒▒███   ▓██ ░▄█ ▒
▒██▀▀█▄  ░██▄▄▄▄██   ▒   ██▒▒▓▓▄ ▄██▒░██▄▄▄▄██ ▒██░       ▒██▀▀█▄  ▓▓█  ░██░▓██▒  ▐▌██▒▓██▒  ▐▌██▒▒▓█  ▄ ▒██▀▀█▄  
░██▓ ▒██▒ ▓█   ▓██▒▒██████▒▒▒ ▓███▀ ░ ▓█   ▓██▒░██████▒   ░██▓ ▒██▒▒▒█████▓ ▒██░   ▓██░▒██░   ▓██░░▒████▒░██▓ ▒██▒
░ ▒▓ ░▒▓░ ▒▒   ▓▒█░▒ ▒▓▒ ▒ ░░ ░▒ ▒  ░ ▒▒   ▓▒█░░ ▒░▓  ░   ░ ▒▓ ░▒▓░░▒▓▒ ▒ ▒ ░ ▒░   ▒ ▒ ░ ▒░   ▒ ▒ ░░ ▒░ ░░ ▒▓ ░▒▓░
  ░▒ ░ ▒░  ▒   ▒▒ ░░ ░▒  ░ ░  ░  ▒     ▒   ▒▒ ░░ ░ ▒  ░     ░▒ ░ ▒░░░▒░ ░ ░ ░ ░░   ░ ▒░░ ░░   ░ ▒░ ░ ░  ░  ░▒ ░ ▒░
  ░░   ░   ░   ▒   ░  ░  ░  ░          ░   ▒     ░ ░        ░░   ░  ░░░ ░ ░    ░   ░ ░    ░   ░ ░    ░     ░░   ░ 
   ░           ░  ░      ░  ░ ░            ░  ░    ░  ░      ░        ░              ░          ░    ░  ░   ░     
                            ░                                                                                     
https://github.com/nopcorn/rascalrunner
"""

logging.basicConfig(
    format="%(asctime)s %(message)s",
    stream=sys.stdout,
    level=logging.INFO
)

def main():
    parser = argparse.ArgumentParser(
        description=(
            "RascalRunner: Red Team tool to leverage GitHub Workflows and GitLab CI/CD pipelines.\n"
            "Supports GitHub.com and public/self-hosted GitLab instances."
        ),
        epilog=(
	    "Examples:\n"
	    "  # GitHub Reconnaissance\n"
	    "  rascalrunner recon --auth <GITHUB_TOKEN> [--show-all]\n"
	    "  # GitLab Reconnaissance (public or self-hosted)\n"
	    "  rascalrunner glrecon --auth <GITLAB_TOKEN> --gitlab-url https://gitlab.example.inc/api/v4\n"
	    "  # GitHub Run Malicious Workflow\n"
	    "  rascalrunner run --auth <GITHUB_TOKEN> --target org/repo --workflow-file ./malicious.yaml\n"
	    "  # GitLab Run Pipeline\n"
	    "  rascalrunner glrun --auth <GITLAB_TOKEN> --target group/repo --pipeline-file ./malicious-ci.yml --gitlab-url https://gitlab.example.inc/api/v4\n"
	    "\n"
	    "For self-hosted GitLab, always provide your own URL as --gitlab-url (e.g., https://gitlab.internal.lan/api/v4)."
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='mode', help='Choose the platform and operation.')

    # GitHub - original
    recon_parser = subparsers.add_parser(
        'recon',
        help="Analyze a GitHub token for repository access and workflow permissions.",
        description="GitHub Recon: Analyze token, find accessible repos, see available secrets, and workflow scope."
    )
    recon_parser.add_argument("-v", "--verbose", help="Enable verbose/debug logging.", action="store_true")
    recon_parser.add_argument("-a", "--auth", required=True, help="Your GitHub Personal Access Token (PAT)")
    recon_parser.add_argument("--show-all", help="Show all repos, even those not accessible with the token.", action="store_true")

    run_parser = subparsers.add_parser(
        'run',
        help="Deploy a GitHub Actions workflow for Red Team operations.",
        description="GitHub Run: Pushes a workflow to a repository using provided GitHub token, triggers run, collects logs, cleans up."
    )
    run_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose/debug logging.")
    run_parser.add_argument("-a", "--auth", required=True, help="Your GitHub Personal Access Token (PAT)")
    run_parser.add_argument("-t", "--target", required=True, help="GitHub repo (format: owner/repo)")
    run_parser.add_argument("-w", "--workflow-file", required=True, help="YAML workflow file to deploy")
    run_parser.add_argument("-b", "--branch", default=f"lint-testing-{''.join(random.choice(string.ascii_letters) for _ in range(5))}", help="Branch name to use")
    run_parser.add_argument("-m", "--commit-message", default="testing out new linter workflow", help="Commit message")
    run_parser.add_argument("--only-delete-logs", action="store_true", default=False, help="Only delete run logs; leaves workflow visible.")

    # GitLab - improved, generic domain names/descriptions
    glrecon_help = (
        "Analyze a GitLab personal token for accessible projects and pipeline permissions.\n"
        "Supports both gitlab.com and self-hosted: use --gitlab-url https://gitlab.example.inc/api/v4"
    )
    gl_recon_parser = subparsers.add_parser(
        'glrecon',
        help="Analyze a GitLab token for accessible projects and permissions.",
        description=glrecon_help
    )
    gl_recon_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose/debug logging.")
    gl_recon_parser.add_argument("-a", "--auth", required=True, help="Your GitLab personal access token")
    gl_recon_parser.add_argument("--show-all", action="store_true", help="Show all available projects.")
    gl_recon_parser.add_argument(
        "--gitlab-url",
        required=True,
        help="Base GitLab API URL, e.g., https://gitlab.example.inc/api/v4"
    )

    glrun_help = (
        "Deploy and run a GitLab CI/CD pipeline for Red Team operations.\n"
        "Use --gitlab-url to specify your GitLab server (public or self-hosted)."
    )
    gl_run_parser = subparsers.add_parser(
        'glrun',
        help="Deploy a GitLab pipeline for Red Team operations.",
        description=glrun_help
    )
    gl_run_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose/debug logging.")
    gl_run_parser.add_argument("-a", "--auth", required=True, help="Your GitLab personal access token")
    gl_run_parser.add_argument("-t", "--target", required=True, help="GitLab project: group/project")
    gl_run_parser.add_argument("-p", "--pipeline-file", required=True, help="Pipeline YAML file (.gitlab-ci.yml)")
    gl_run_parser.add_argument("-b", "--branch", default="rascalrunner-test", help="Branch name to use")
    gl_run_parser.add_argument("-m", "--commit-message", default="Automated pipeline run", help="Commit message")
    gl_run_parser.add_argument("--only-delete-logs", action="store_true", default=False, help="Only delete pipeline logs; leaves pipeline visible.")
    gl_run_parser.add_argument(
        "--gitlab-url",
        required=True,
        help="Base GitLab API URL, e.g., https://gitlab.example.inc/api/v4"
    )

    args = vars(parser.parse_args())
    print(ascii_banner)
    if args.get("verbose"):
        logging.getLogger().setLevel(logging.DEBUG)

    # GitHub
    if args.get("mode") == "recon":
        wrapper = GithubWrapper(args["auth"], args["mode"])
        recon = ReconRunner(wrapper, show_all=args['show_all'])
        recon.run()
    elif args.get("mode") == "run":
        wrapper = GithubWrapper(args["auth"], args["mode"])
        rascal = RascalRunner(
            args["target"], args["workflow_file"], wrapper,
            branch_name=args["branch"], commit_message=args["commit_message"],
            only_delete_logs=args["only_delete_logs"]
        )
        rascal.run()
    # GitLab
    elif args.get("mode") == "glrecon":
        wrapper = GitlabWrapper(args["auth"], args["mode"], base_url=args["gitlab_url"])
        recon = GitlabRecon(wrapper, show_all=args['show_all'])
        recon.run()
    elif args.get("mode") == "glrun":
        wrapper = GitlabWrapper(args["auth"], args["mode"], base_url=args["gitlab_url"])
        runner = GitlabRunner(
            args["target"], args["pipeline_file"], wrapper,
            branch_name=args["branch"], commit_message=args["commit_message"],
            only_delete_logs=args["only_delete_logs"]
        )
        runner.run()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
