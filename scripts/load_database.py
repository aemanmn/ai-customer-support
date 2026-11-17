import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    supabase_cli = shutil.which("supabase")
    if supabase_cli is None:
        raise SystemExit("Supabase CLI is required to apply database migrations.")

    migrations = PROJECT_ROOT / "supabase" / "migrations"
    if not any(migrations.glob("*.sql")):
        raise SystemExit(f"No SQL migrations found in {migrations}.")

    subprocess.run(
        [supabase_cli, "db", "push", "--linked"],
        cwd=PROJECT_ROOT,
        check=True,
    )


if __name__ == "__main__":
    main()
