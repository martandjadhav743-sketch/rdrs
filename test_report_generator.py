from app.reports.report_generator import create_report_content, save_report

content = create_report_content(
    total_events=36,
    created_events=12,
    modified_events=19,
    deleted_events=0,
    moved_events=5,
    total_alerts=1,
)

report_path = save_report(content)

print("Report created successfully:")
print(report_path)