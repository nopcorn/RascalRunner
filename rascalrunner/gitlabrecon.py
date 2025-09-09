import logging
from rich.console import Console
from rich.table import Table

class GitlabRecon:
    def __init__(self, wrapper, show_all):
        self.wrapper = wrapper
        self.show_all = show_all

    def run(self):
        console = Console()
        user = self.wrapper.get_current_user()
        user_is_admin = user.get('username', '').lower() == 'root' or user.get('is_admin', False)

        table = Table(title="GitLab Token/Account Info")
        table.add_column("Key"); table.add_column("Value")
        table.add_row("Username", user.get("username"))
        table.add_row("Name", user.get("name"))
        table.add_row("ID", str(user.get("id")))
        table.add_row("Email", user.get("email") or "-")
        table.add_row("Is Admin", str(user_is_admin))
        console.print(table)

        proj_table = Table(title="Accessible GitLab Projects")
        proj_table.add_column("Project")
        proj_table.add_column("Visibility")
        proj_table.add_column("Permissions")

        projects = self.wrapper.list_projects()
        for proj in projects:
            name = proj.get("path_with_namespace")
            vis = proj.get("visibility")
            perms = []
            # Try various ways to display permissions
            access = proj.get("permissions", {})
            if user_is_admin:
                perms.append("Admin (all)")
            elif proj.get("owner"):
                perms.append("Owner")
            elif proj.get("archived"):
                perms.append("Archived")
            elif access.get("project_access"):
                perms.append(str(access["project_access"].get("access_level")))
            elif access.get("group_access"):
                perms.append(str(access["group_access"].get("access_level")))
            else:
                perms.append("-")
            proj_table.add_row(name, vis, ", ".join(perms))

        console.print(proj_table)
