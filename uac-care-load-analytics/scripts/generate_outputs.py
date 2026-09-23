from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.analysis import executive_summary, research_paper, summarize
from src.metrics import add_metrics
from src.preprocessing import analysis_frame, load_and_clean


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "uac_dataset.csv"


def main() -> None:
    cleaned, quality = load_and_clean(RAW_PATH)
    data = add_metrics(analysis_frame(cleaned))
    (ROOT / "data" / "processed" / "cleaned_uac_data.csv").write_text(data.to_csv(index=False), encoding="utf-8")
    summary = summarize(data)
    (ROOT / "docs" / "executive_summary.md").write_text(executive_summary(summary, quality), encoding="utf-8")
    (ROOT / "docs" / "research_paper_support.md").write_text(research_paper(summary, quality), encoding="utf-8")
    print(f"Generated outputs for {summary['record_count']:,} observations.")


if __name__ == "__main__":
    main()