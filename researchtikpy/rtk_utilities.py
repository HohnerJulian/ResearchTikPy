from logging import getLogger
from pathlib import Path
import pandas as pd


logger = getLogger(__name__)


def append_df_to_file(
    df: pd.DataFrame, path: Path, jsonl: bool = False, quiet: bool = False
) -> None:
    if len(df) == 0:
        logger.info("df is empty, no rows to append to file")
        return

    data_dir = path.parent
    data_dir.mkdir(parents=True, exist_ok=True)
    if jsonl:
        df.to_json(path, mode="a", orient="records", lines=True)
    else:
        df.to_csv(path, mode="a", header=not path.exists(), index=False)
    if not quiet:
        logger.info(f"Appended {len(df)} rows to '{path.absolute()}'")
