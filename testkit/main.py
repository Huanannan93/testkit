"""CLI 入口"""
import typer
from rich.console import Console

console = Console()
app = typer.Typer(
    name="testkit",
    help="test-ecosystem 底座 CLI — 个人 AI 测试生态系统管理器",
    no_args_is_help=True,
)

from testkit.commands import init, update, status, project, skill, knowledge, agent

app.command(name="init")(init.init)
app.command(name="update")(update.update)
app.command(name="status")(status.status)
app.command(name="project")(project.project)
app.command(name="skill")(skill.skill)
app.command(name="knowledge")(knowledge.knowledge)
app.command(name="agent")(agent.agent)

if __name__ == "__main__":
    app()
