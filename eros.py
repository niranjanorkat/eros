import argparse
from src.log import add_log, add_log_continuous
from src.vector import update_vector_db
from src.query import query_cli, query_continuous
from src.profile import generate_profile_summary, export_profile_to_pdf


def main():
    parser = argparse.ArgumentParser(description="Eros CLI - Personal RAG Logger")
    subparsers = parser.add_subparsers(dest="command")

    # Add log command
    add_parser = subparsers.add_parser("add", help="Add a log")
    add_parser.add_argument("text", nargs="?", help="Log text")
    add_parser.add_argument(
        "--continuous", action="store_true", help="Enter multiline input mode"
    )

    # Update vector DB command
    subparsers.add_parser("update", help="Sync new logs to vector DB")

    query_parser = subparsers.add_parser("query", help="Ask a question")
    query_parser.add_argument("text", nargs="?", help="Question")
    query_parser.add_argument(
        "--continuous", action="store_true", help="Interactive Q&A loop"
    )

    profile_parser = subparsers.add_parser("profile", help="Generate profile summary")
    profile_parser.add_argument("--export", action="store_true", help="Export as PDF")

    args = parser.parse_args()

    if args.command == "add":
        if args.continuous:
            add_log_continuous()
        elif args.text:
            add_log(args.text)
        else:
            print("Error: Provide text or use --continuous.")
            exit(1)
    elif args.command == "update":
        update_vector_db()
    elif args.command == "query":
        if args.continuous:
            query_continuous()
        elif args.text:
            query_cli(args.text)
    elif args.command == "profile":
        summary = generate_profile_summary()
        if args.export:
            export_profile_to_pdf(summary, args.export)
        else:
            print(f"\n📝 Summary:\n{summary}\n")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
