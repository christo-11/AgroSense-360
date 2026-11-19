"""Record an allowlisted administrative review in the dataset source inventory."""

import argparse
from pathlib import Path

from dataset_governance import (
    APPROVAL_STATUSES,
    DatasetEligibilityError,
    approval_key,
    record_admin_review,
    reviewer_allowlist,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = PROJECT_ROOT / "data" / "metadata" / "source_inventory.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--status", required=True, choices=sorted(APPROVAL_STATUSES))
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()

    try:
        record_admin_review(
            INVENTORY_PATH,
            args.dataset_id,
            args.status,
            args.reviewer,
            reviewer_allowlist(PROJECT_ROOT),
            args.reason,
            approval_key(PROJECT_ROOT),
        )
    except DatasetEligibilityError as error:
        parser.error(str(error))
    print(f"Recorded {args.status} review for {args.dataset_id}.")


if __name__ == "__main__":
    main()
