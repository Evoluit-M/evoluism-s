import runpy
from pathlib import Path


def main():
    """
    Entry point for the spurious regression Streamlit app.

    This file is a thin wrapper so that Streamlit Cloud
    can find `app.py` at the repository root and run the
    existing application located in the `app/` folder.
    """

    repo_root = Path(__file__).parent
    app_dir = repo_root / "app"

    # 1) Явно проверяем самые ожидаемые имена
    explicit_candidates = [
        app_dir / "streamlit_spurious_test.py",
        app_dir / "SpuriousRisk_app.py",
    ]

    for p in explicit_candidates:
        if p.is_file():
            runpy.run_path(str(p), run_name="__main__")
            return

    # 2) Если ничего не нашли — пытаемся автоматически найти любой .py в app/
    if app_dir.is_dir():
        py_files = sorted(
            f for f in app_dir.glob("*.py") if f.name != "__init__.py"
        )
        if py_files:
            # Берём первый по алфавиту .py как основной Streamlit-скрипт
            target = py_files[0]
            runpy.run_path(str(target), run_name="__main__")
            return

    # 3) Если и тут пусто — выдаём понятную ошибку
    raise FileNotFoundError(
        "Could not find a Streamlit app script in the 'app/' folder. "
        "Expected one of:\n"
        "  - app/streamlit_spurious_test.py\n"
        "  - app/SpuriousRisk_app.py\n"
        "or at least one '*.py' file inside 'app/' (excluding __init__.py)."
    )


if __name__ == "__main__":
    main()

