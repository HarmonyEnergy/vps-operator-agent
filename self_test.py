from vps_agent import run_task

if __name__ == "__main__":
    out = run_task("Using tools only: run 'pwd' and 'ls -lah' in the workspace and summarize what you see.", max_turns=5)
    print(out)
