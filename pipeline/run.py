"""Daily entrypoint: rebuild the CSVs from fresh Dune data, then upload to Dune.

  python -m pipeline.run              # build + upload
  python -m pipeline.run --no-upload  # build only (CSVs land in out/)
"""
import argparse
from . import build, upload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-upload", action="store_true", help="build CSVs but do not upload to Dune")
    args = ap.parse_args()
    build.main()
    if args.no_upload:
        print("skipped upload (--no-upload)")
    else:
        upload.main()


if __name__ == "__main__":
    main()
