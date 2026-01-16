from __future__ import annotations

import argparse

from backend.db import init_db


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize the CRM database.")
    parser.add_argument(
        "--database-url",
        dest="database_url",
        help="Optional database URL to override the configured database.",
    )
    args = parser.parse_args()

    db_path = init_db(args.database_url)
    print(f"Database initialized at {db_path}")


if __name__ == "__main__":
    main()
