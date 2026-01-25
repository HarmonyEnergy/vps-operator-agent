import argparse
from vps_agent import run_task

def main():
    p = argparse.ArgumentParser(
        prog="agent",
        description="VPS Operator Agent - Execute tasks with AI assistance"
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    
    r = sub.add_parser("run", help="Run a task using the VPS agent")
    r.add_argument("task", nargs="+", help="Task description")
    r.add_argument("--model", default="gpt-4o-mini", help="Model to use")
    r.add_argument("--max-turns", type=int, default=25, help="Maximum tool-use turns")
    r.add_argument("--no-transcript", action="store_true", help="Hide tool IO transcript")
    
    test = sub.add_parser("test", help="Run test suite")
    
    args = p.parse_args()
    
    if args.cmd == "run":
        task = " ".join(args.task)
        print(run_task(
            task,
            model=args.model,
            max_turns=args.max_turns,
            include_transcript=(not args.no_transcript)
        ))
    elif args.cmd == "test":
        import subprocess
        import sys
        result = subprocess.run([sys.executable, "test_suite.py"])
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
