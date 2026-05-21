"""CLI 入口"""
import typer

app = typer.Typer(
    name="testkit",
    help="test-ecosystem 底座 CLI — 个人 AI 测试生态系统管理器",
    no_args_is_help=True,
)

from testkit.commands.init import init as cmd_init
from testkit.commands.update import update as cmd_update
from testkit.commands.status import status as cmd_status
from testkit.commands.project import project
from testkit.commands.skill import skill
from testkit.commands.knowledge import knowledge
from testkit.commands.agent import agent

app.command(name="init")(cmd_init)
app.command(name="update")(cmd_update)
app.command(name="status")(cmd_status)
app.add_typer(project, name="project")
app.add_typer(skill, name="skill")
app.add_typer(knowledge, name="knowledge")
app.add_typer(agent, name="agent")

if __name__ == "__main__":
    app()
