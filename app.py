import runpy
from pathlib import Path


def main():
    """
    Entry point for the spurious regression Streamlit app.

    This file is a thin wrapper so that Streamlit Cloud
    can find `app.py` at the repository root and run the
    existing application located in the `app/` folder.
    """

    candidates = [
        Path("app") / "streamlit_spurious_test.py",
        Path("app") / "SpuriousRisk_app.py",
    ]

    for p in candidates:
        if p.exists():
            runpy.run_path(str(p), run_name="__main__")
            return

    raise FileNotFoundError(
        "Could not find Streamlit app script. "
        "Expected one of: "
        "app/streamlit_spurious_test.py or app/SpuriousRisk_app.py"
    )


if __name__ == "__main__":
    main()
