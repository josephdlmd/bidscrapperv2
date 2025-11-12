"""
Daily Summary Report Generator for PhilGEPS Scraper
Generates reports in JSON, HTML, and CSV formats
"""
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging


# Create reports directory
REPORTS_DIR = Path(__file__).parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Report subdirectories
JSON_REPORTS_DIR = REPORTS_DIR / "json"
HTML_REPORTS_DIR = REPORTS_DIR / "html"
CSV_REPORTS_DIR = REPORTS_DIR / "csv"

for dir_path in [JSON_REPORTS_DIR, HTML_REPORTS_DIR, CSV_REPORTS_DIR]:
    dir_path.mkdir(exist_ok=True)


@dataclass
class ScrapeStats:
    """Statistics from a scraping session"""
    start_time: str
    end_time: str
    duration_seconds: float
    total_pages_scraped: int
    total_bids_found: int
    new_bids_added: int
    existing_bids_updated: int
    bids_skipped: int
    errors_count: int
    success_rate: float
    filters_applied: Dict[str, Any]
    scrape_mode: str  # 'full', 'incremental', 'test'


@dataclass
class ErrorSummary:
    """Summary of errors encountered"""
    error_type: str
    error_message: str
    count: int
    first_occurrence: str
    last_occurrence: str


@dataclass
class BidSummary:
    """Summary of a bid for reporting"""
    reference_number: str
    title: str
    classification: str
    approved_budget: Optional[float]
    closing_date: Optional[str]
    agency_name: str
    status: str  # 'new', 'updated', 'skipped'


class ReportGenerator:
    """Generates daily summary reports for scraping sessions"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    def generate_report(
        self,
        stats: ScrapeStats,
        bids: List[BidSummary],
        errors: List[ErrorSummary],
        report_formats: List[str] = ['json', 'html', 'csv']
    ) -> Dict[str, Path]:
        """
        Generate reports in specified formats

        Args:
            stats: Scraping statistics
            bids: List of bid summaries
            errors: List of error summaries
            report_formats: List of formats to generate ('json', 'html', 'csv')

        Returns:
            Dictionary mapping format to file path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_files = {}

        try:
            if 'json' in report_formats:
                json_file = self._generate_json_report(stats, bids, errors, timestamp)
                report_files['json'] = json_file
                self.logger.info(f"JSON report generated: {json_file}")

            if 'html' in report_formats:
                html_file = self._generate_html_report(stats, bids, errors, timestamp)
                report_files['html'] = html_file
                self.logger.info(f"HTML report generated: {html_file}")

            if 'csv' in report_formats:
                csv_file = self._generate_csv_report(stats, bids, errors, timestamp)
                report_files['csv'] = csv_file
                self.logger.info(f"CSV report generated: {csv_file}")

        except Exception as e:
            self.logger.error(f"Error generating reports: {str(e)}", exc_info=True)

        return report_files

    def _generate_json_report(
        self,
        stats: ScrapeStats,
        bids: List[BidSummary],
        errors: List[ErrorSummary],
        timestamp: str
    ) -> Path:
        """Generate JSON format report"""
        report_data = {
            "report_generated_at": datetime.now().isoformat(),
            "statistics": asdict(stats),
            "bids": [asdict(bid) for bid in bids],
            "errors": [asdict(error) for error in errors]
        }

        file_path = JSON_REPORTS_DIR / f"scrape_report_{timestamp}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        return file_path

    def _generate_html_report(
        self,
        stats: ScrapeStats,
        bids: List[BidSummary],
        errors: List[ErrorSummary],
        timestamp: str
    ) -> Path:
        """Generate HTML format report"""
        # Separate bids by status
        new_bids = [b for b in bids if b.status == 'new']
        updated_bids = [b for b in bids if b.status == 'updated']
        skipped_bids = [b for b in bids if b.status == 'skipped']

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PhilGEPS Scraper Report - {timestamp}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .header .timestamp {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-card .label {{
            color: #666;
            font-size: 0.85em;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-card .subtext {{
            color: #999;
            font-size: 0.85em;
            margin-top: 5px;
        }}
        .section {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .section h2 {{
            margin-top: 0;
            color: #667eea;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #f0f0f0;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #555;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        .badge-new {{
            background-color: #d4edda;
            color: #155724;
        }}
        .badge-updated {{
            background-color: #fff3cd;
            color: #856404;
        }}
        .badge-skipped {{
            background-color: #e2e3e5;
            color: #383d41;
        }}
        .badge-error {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        .filters {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin-top: 15px;
        }}
        .filters h3 {{
            margin-top: 0;
            font-size: 1em;
            color: #666;
        }}
        .filter-item {{
            display: inline-block;
            margin-right: 15px;
            margin-bottom: 5px;
        }}
        .filter-label {{
            font-weight: 500;
            color: #555;
        }}
        .empty-state {{
            text-align: center;
            padding: 40px;
            color: #999;
        }}
        .success-badge {{
            background-color: #28a745;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        .warning-badge {{
            background-color: #ffc107;
            color: #000;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 PhilGEPS Scraper Daily Report</h1>
        <div class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        <div class="timestamp">Scrape Mode: {stats.scrape_mode.upper()}</div>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="label">Duration</div>
            <div class="value">{stats.duration_seconds:.1f}s</div>
            <div class="subtext">{stats.start_time} - {stats.end_time}</div>
        </div>
        <div class="stat-card">
            <div class="label">Total Bids Found</div>
            <div class="value">{stats.total_bids_found}</div>
            <div class="subtext">{stats.total_pages_scraped} pages scraped</div>
        </div>
        <div class="stat-card">
            <div class="label">New Bids</div>
            <div class="value">{stats.new_bids_added}</div>
            <div class="subtext">Added to database</div>
        </div>
        <div class="stat-card">
            <div class="label">Updated Bids</div>
            <div class="value">{stats.existing_bids_updated}</div>
            <div class="subtext">Details refreshed</div>
        </div>
        <div class="stat-card">
            <div class="label">Success Rate</div>
            <div class="value">{stats.success_rate:.1f}%</div>
            <div class="subtext">{stats.errors_count} errors encountered</div>
        </div>
    </div>

    <div class="section">
        <h2>🎯 Applied Filters</h2>
        <div class="filters">
            <div class="filter-item">
                <span class="filter-label">Date Range:</span> {stats.filters_applied.get('date_from', 'N/A')} to {stats.filters_applied.get('date_to', 'N/A')}
            </div>
            <div class="filter-item">
                <span class="filter-label">Classification:</span> {stats.filters_applied.get('classification', 'All')}
            </div>
            <div class="filter-item">
                <span class="filter-label">Budget Range:</span> ₱{stats.filters_applied.get('budget_min', 0):,.2f} - ₱{stats.filters_applied.get('budget_max', 'unlimited')}
            </div>
            <div class="filter-item">
                <span class="filter-label">Keywords:</span> {stats.filters_applied.get('keywords', 'None')}
            </div>
        </div>
    </div>

    <div class="section">
        <h2>✨ New Bids ({len(new_bids)})</h2>
        {self._generate_bid_table(new_bids, 'new')}
    </div>

    <div class="section">
        <h2>🔄 Updated Bids ({len(updated_bids)})</h2>
        {self._generate_bid_table(updated_bids, 'updated')}
    </div>

    <div class="section">
        <h2>⚠️ Errors ({len(errors)})</h2>
        {self._generate_error_table(errors)}
    </div>

    <footer style="text-align: center; margin-top: 30px; padding: 20px; color: #999;">
        <p>PhilGEPS Scraper v2.0 | Report generated automatically</p>
    </footer>
</body>
</html>
"""

        file_path = HTML_REPORTS_DIR / f"scrape_report_{timestamp}.html"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return file_path

    def _generate_bid_table(self, bids: List[BidSummary], status: str) -> str:
        """Generate HTML table for bids"""
        if not bids:
            return '<div class="empty-state">No bids in this category</div>'

        badge_class = f"badge-{status}"
        rows = []

        for bid in bids[:50]:  # Limit to first 50 for readability
            budget_str = f"₱{bid.approved_budget:,.2f}" if bid.approved_budget else "N/A"
            closing_date_str = bid.closing_date if bid.closing_date else "N/A"

            rows.append(f"""
                <tr>
                    <td><strong>{bid.reference_number}</strong></td>
                    <td>{bid.title[:80]}{'...' if len(bid.title) > 80 else ''}</td>
                    <td>{bid.classification}</td>
                    <td>{budget_str}</td>
                    <td>{closing_date_str}</td>
                    <td>{bid.agency_name[:40]}{'...' if len(bid.agency_name) > 40 else ''}</td>
                </tr>
            """)

        table = f"""
        <table>
            <thead>
                <tr>
                    <th>Reference Number</th>
                    <th>Title</th>
                    <th>Classification</th>
                    <th>Budget</th>
                    <th>Closing Date</th>
                    <th>Agency</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """

        if len(bids) > 50:
            table += f'<p style="color: #999; margin-top: 10px;">Showing first 50 of {len(bids)} bids</p>'

        return table

    def _generate_error_table(self, errors: List[ErrorSummary]) -> str:
        """Generate HTML table for errors"""
        if not errors:
            return '<div class="empty-state">✅ No errors encountered</div>'

        rows = []
        for error in errors:
            rows.append(f"""
                <tr>
                    <td><span class="badge badge-error">{error.error_type}</span></td>
                    <td>{error.error_message}</td>
                    <td>{error.count}</td>
                    <td>{error.first_occurrence}</td>
                </tr>
            """)

        return f"""
        <table>
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Message</th>
                    <th>Count</th>
                    <th>First Occurred</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """

    def _generate_csv_report(
        self,
        stats: ScrapeStats,
        bids: List[BidSummary],
        errors: List[ErrorSummary],
        timestamp: str
    ) -> Path:
        """Generate CSV format report"""
        file_path = CSV_REPORTS_DIR / f"scrape_report_{timestamp}.csv"

        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write statistics section
            writer.writerow(['SCRAPING STATISTICS'])
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Start Time', stats.start_time])
            writer.writerow(['End Time', stats.end_time])
            writer.writerow(['Duration (seconds)', stats.duration_seconds])
            writer.writerow(['Total Pages Scraped', stats.total_pages_scraped])
            writer.writerow(['Total Bids Found', stats.total_bids_found])
            writer.writerow(['New Bids Added', stats.new_bids_added])
            writer.writerow(['Existing Bids Updated', stats.existing_bids_updated])
            writer.writerow(['Bids Skipped', stats.bids_skipped])
            writer.writerow(['Errors Count', stats.errors_count])
            writer.writerow(['Success Rate (%)', stats.success_rate])
            writer.writerow(['Scrape Mode', stats.scrape_mode])
            writer.writerow([])

            # Write filters section
            writer.writerow(['APPLIED FILTERS'])
            writer.writerow(['Filter', 'Value'])
            for key, value in stats.filters_applied.items():
                writer.writerow([key, value])
            writer.writerow([])

            # Write bids section
            writer.writerow(['BIDS PROCESSED'])
            writer.writerow([
                'Reference Number', 'Title', 'Classification',
                'Approved Budget', 'Closing Date', 'Agency Name', 'Status'
            ])

            for bid in bids:
                writer.writerow([
                    bid.reference_number,
                    bid.title,
                    bid.classification,
                    bid.approved_budget or '',
                    bid.closing_date or '',
                    bid.agency_name,
                    bid.status
                ])

            writer.writerow([])

            # Write errors section
            writer.writerow(['ERRORS ENCOUNTERED'])
            writer.writerow(['Type', 'Message', 'Count', 'First Occurrence', 'Last Occurrence'])

            for error in errors:
                writer.writerow([
                    error.error_type,
                    error.error_message,
                    error.count,
                    error.first_occurrence,
                    error.last_occurrence
                ])

        return file_path

    def get_latest_report(self, format_type: str = 'html') -> Optional[Path]:
        """
        Get the path to the most recent report of specified format

        Args:
            format_type: Report format ('json', 'html', 'csv')

        Returns:
            Path to latest report or None if no reports exist
        """
        dir_map = {
            'json': JSON_REPORTS_DIR,
            'html': HTML_REPORTS_DIR,
            'csv': CSV_REPORTS_DIR
        }

        report_dir = dir_map.get(format_type)
        if not report_dir:
            return None

        reports = sorted(report_dir.glob(f"scrape_report_*.{format_type}"))
        return reports[-1] if reports else None

    def cleanup_old_reports(self, days_to_keep: int = 30):
        """
        Remove report files older than specified days

        Args:
            days_to_keep: Number of days to keep reports (default 30)
        """
        import time
        cutoff_time = time.time() - (days_to_keep * 86400)

        for report_dir in [JSON_REPORTS_DIR, HTML_REPORTS_DIR, CSV_REPORTS_DIR]:
            for report_file in report_dir.glob("scrape_report_*"):
                if report_file.stat().st_mtime < cutoff_time:
                    report_file.unlink()
                    self.logger.info(f"Deleted old report: {report_file.name}")


if __name__ == "__main__":
    # Test report generation
    from datetime import datetime, timedelta

    print("Testing report generator...")

    # Sample data
    stats = ScrapeStats(
        start_time="2024-01-15 08:00:00",
        end_time="2024-01-15 08:45:30",
        duration_seconds=2730.5,
        total_pages_scraped=10,
        total_bids_found=150,
        new_bids_added=45,
        existing_bids_updated=105,
        bids_skipped=0,
        errors_count=2,
        success_rate=98.7,
        filters_applied={
            'date_from': '2024-01-01',
            'date_to': '2024-01-31',
            'classification': 'Goods',
            'budget_min': 100000,
            'budget_max': 5000000,
            'keywords': 'office supplies'
        },
        scrape_mode='incremental'
    )

    bids = [
        BidSummary(
            reference_number="REF-2024-001",
            title="Supply and Delivery of Office Equipment",
            classification="Goods",
            approved_budget=1250000.00,
            closing_date="2024-01-30",
            agency_name="Department of Education",
            status="new"
        ),
        BidSummary(
            reference_number="REF-2024-002",
            title="Construction of School Building",
            classification="Civil Works",
            approved_budget=15000000.00,
            closing_date="2024-02-15",
            agency_name="Department of Public Works",
            status="new"
        ),
        BidSummary(
            reference_number="REF-2023-999",
            title="IT Infrastructure Upgrade",
            classification="Goods",
            approved_budget=3500000.00,
            closing_date="2024-01-25",
            agency_name="Department of Health",
            status="updated"
        ),
    ]

    errors = [
        ErrorSummary(
            error_type="NetworkError",
            error_message="Connection timeout while fetching page 7",
            count=1,
            first_occurrence="2024-01-15 08:23:15",
            last_occurrence="2024-01-15 08:23:15"
        ),
        ErrorSummary(
            error_type="ParseError",
            error_message="Failed to parse approved budget field",
            count=1,
            first_occurrence="2024-01-15 08:35:42",
            last_occurrence="2024-01-15 08:35:42"
        ),
    ]

    # Generate reports
    generator = ReportGenerator()
    report_files = generator.generate_report(stats, bids, errors)

    print("\n✅ Test reports generated:")
    for format_type, file_path in report_files.items():
        print(f"   {format_type.upper()}: {file_path}")

    print(f"\n📁 Reports directory: {REPORTS_DIR}")
