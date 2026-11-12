from app.reports.report_generator import create_report_content, save_report

content = create_report_content(
    total_events=10,
    created_events=3,
    modified_events=5,
    deleted_events=1,
    moved_events=1,
    total_alerts=0,
)

report_path = save_report(content)

print("Report generated successfully:")
print(report_path)