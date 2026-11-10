from datetime import datetime, timedelta, timezone

from app.core.events import FileEvent
from app.detectors.window_detector import SlidingWindowDetector


def create_test_event(
    event_type,
    source_path,
    destination_path=None,
    extension=None,
    previous_extension=None,
    age_seconds=0,
):
    timestamp = datetime.now(timezone.utc) - timedelta(seconds=age_seconds)

    return FileEvent(
        event_type=event_type,
        source_path=source_path,
        timestamp=timestamp,
        extension=extension,
        destination_path=destination_path,
        previous_extension=previous_extension,
    )


def main():
    detector = SlidingWindowDetector(window_seconds=60)

    detector.add_event(
        create_test_event(
            event_type="modified",
            source_path="C:/test/file1.txt",
            extension=".txt",
        )
    )

    detector.add_event(
        create_test_event(
            event_type="moved",
            source_path="C:/test/file2.txt",
            destination_path="C:/test/file2.locked",
            extension=".locked",
            previous_extension=".txt",
        )
    )

    detector.add_event(
        create_test_event(
            event_type="modified",
            source_path="C:/test/file3.txt",
            extension=".txt",
            age_seconds=70,
        )
    )

    summary = detector.get_window_summary()

    print("Sliding window summary:")
    print(summary)

    if summary["total_events"] == 2:
        print("PASS: Old event was removed correctly.")
    else:
        print("FAIL: Old event was not removed correctly.")

    if summary["modified_events"] == 1:
        print("PASS: Modified event count is correct.")
    else:
        print("FAIL: Modified event count is incorrect.")

    if summary["extension_changes"] == 1:
        print("PASS: Extension change count is correct.")
    else:
        print("FAIL: Extension change count is incorrect.")


if __name__ == "__main__":
    main()