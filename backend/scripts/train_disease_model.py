"""Train an image classifier from a labeled ImageFolder dataset."""

import argparse
import json
from pathlib import Path

from dataset_governance import (
    DatasetEligibilityError,
    approval_key,
    require_training_dataset,
    reviewer_allowlist,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True, help="ImageFolder root with one folder per verified label.")
    parser.add_argument("--dataset-id", required=True, help="Approved source id from the dataset inventory.")
    parser.add_argument("--provenance", type=Path, required=True, help="Sidecar JSON provenance manifest.")
    parser.add_argument(
        "--inventory",
        type=Path,
        default=PROJECT_ROOT / "data" / "metadata" / "source_inventory.json",
    )
    parser.add_argument("--output", type=Path, default=Path("models/disease_resnet18.pt"))
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.epochs < 1 or args.batch_size < 1:
        raise SystemExit("--epochs and --batch-size must be positive.")

    try:
        require_training_dataset(
            args.dataset_id,
            args.data,
            args.provenance,
            args.inventory,
            reviewer_allowlist(PROJECT_ROOT),
            approval_key(PROJECT_ROOT),
        )
    except DatasetEligibilityError as error:
        raise SystemExit(f"Dataset rejected by commercial eligibility gate: {error}") from None

    import random

    import torch
    from sklearn.metrics import accuracy_score, classification_report
    from torch import nn
    from torch.utils.data import DataLoader, Subset
    from torchvision import datasets, models, transforms

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    validation_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    train_data = datasets.ImageFolder(args.data, transform=train_transform)
    validation_data = datasets.ImageFolder(args.data, transform=validation_transform)
    if len(train_data.classes) < 2:
        raise SystemExit("At least two labeled classes are required.")

    train_indices: list[int] = []
    validation_indices: list[int] = []
    class_counts = {index: 0 for index in range(len(train_data.classes))}
    for _, label in train_data.samples:
        class_counts[label] += 1
    for label, count in class_counts.items():
        if count < 5:
            raise SystemExit(f"Class {train_data.classes[label]!r} has {count} images; at least 5 are required.")
        indices = [index for index, (_, target) in enumerate(train_data.samples) if target == label]
        random.shuffle(indices)
        validation_count = max(1, round(count * 0.2))
        validation_indices.extend(indices[:validation_count])
        train_indices.extend(indices[validation_count:])

    train_loader = DataLoader(Subset(train_data, train_indices), batch_size=args.batch_size, shuffle=True, num_workers=0)
    validation_loader = DataLoader(Subset(validation_data, validation_indices), batch_size=args.batch_size, shuffle=False, num_workers=0)
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(train_data.classes))
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    criterion = nn.CrossEntropyLoss()
    for epoch in range(args.epochs):
        model.train()
        epoch_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        print(f"epoch={epoch + 1}/{args.epochs} train_loss={epoch_loss / len(train_loader):.4f}")

    model.eval()
    expected: list[int] = []
    predicted: list[int] = []
    with torch.inference_mode():
        for images, labels in validation_loader:
            logits = model(images.to(device))
            predicted.extend(logits.argmax(dim=1).cpu().tolist())
            expected.extend(labels.tolist())
    report = classification_report(
        expected, predicted, labels=list(range(len(train_data.classes))),
        target_names=train_data.classes, output_dict=True, zero_division=0
    )
    artifact = {
        "architecture": "resnet18",
        "state_dict": model.cpu().state_dict(),
        "classes": train_data.classes,
        "input_size": [224, 224],
        "validation_accuracy": float(accuracy_score(expected, predicted)),
        "validation_report": report,
        "training_samples": len(train_indices),
        "validation_samples": len(validation_indices),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save(artifact, args.output)
    print(json.dumps({key: value for key, value in artifact.items() if key != "state_dict"}, indent=2))


if __name__ == "__main__":
    main()
