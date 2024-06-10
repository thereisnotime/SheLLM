import subprocess

def get_git_info():
    """Returns the current git branch and status if in a git repository."""
    try:
        if subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).returncode == 0:
            branch = subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip()
            status = subprocess.check_output(['git', 'status', '--porcelain'], text=True)
            changes = len(status.split('\n')) - 1 if status else 0
            return f"{branch} | {changes} changes" if branch else ""
        return ""
    except subprocess.CalledProcessError:
        return ""
