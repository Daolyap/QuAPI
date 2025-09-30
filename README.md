# QuAPI
Qualys API GUI for the gang.

## Features
- **Modern UI**: Dark theme with enhanced styling and smooth user experience
- **Dual Output**: Automatically displays both formatted (sortable table) and raw (XML/JSON) output
- **Sortable Columns**: Click column headers to sort data in formatted output
- **Comprehensive API Coverage**:
  - Vulnerability Management (scans, targets, results)
  - Asset Management (search by IP/DNS/NetBIOS, host details, cloud agents)
  - Reports (list, launch, fetch, delete)
  - Knowledge Base (vulnerability search, QID details)
  - Custom requests for advanced users

## Requirements
- Python 3.x
- Required packages: `tkinter`, `requests`

## Installation
```bash
pip install requests
```

## Usage
1. Run the script:
   ```bash
   python QuAPI.py
   ```
2. Enter your Qualys credentials (ensure API access is enabled in your Qualys settings)
3. Select an operation from the sidebar
4. View results in either Formatted or Raw output tabs

## API Operations

### Vulnerability Management
- **List Scans**: View all vulnerability scans
- **Launch Scan**: Start a new scan with customizable targets
- **Get Scan Results**: Retrieve detailed scan results by reference
- **List Scan Targets**: View configured scan targets

### Asset Management
- **Search Assets**: Find assets by IP address, DNS hostname, or NetBIOS name
- **List Cloud Agents**: View all cloud agents with status and version info
- **Get Host Details**: Retrieve comprehensive host information

### Reports
- **List Reports**: View all available reports
- **List Report Templates**: Fetch and cache report templates
- **Launch Report**: Create new reports with templates, tags, and formats (CSV, PDF, XML, HTML)
- **Fetch Report**: Download completed reports
- **Delete Report**: Remove reports by ID

### Knowledge Base
- **Search Vulnerabilities**: Search Qualys KB by QID, severity, or date
- **Get QID Details**: Retrieve detailed vulnerability information

### Utilities
- **Get User Info**: View user account details
- **Custom Request**: Make advanced API calls with full control
- **Clear Output**: Reset all output displays

## Changelog

### v2.0 - Major Redux
**Fixed Bugs:**
- Report template fetching now works correctly
- Asset search now supports IP, DNS, and NetBIOS properly
- UI consistency improved throughout application
- Cloud agents endpoint fixed (updated to correct API path)
- Custom request now fully functional with parameter and body support
- Dual output now generated automatically
- Report operations unified with single fetch mechanism
- Launch scan and Get scan results fully implemented
- Column sorting now functional in formatted output

**Improvements:**
- Enhanced dark theme with modern color scheme
- Larger default window size (1200x850) with minimum size constraints
- Improved button organization with scrollable sidebar
- Better error handling with timeout and connection error messages
- Enhanced dialog windows with consistent styling
- Keyboard shortcuts (Enter key) for all dialogs
- Input validation on all forms
- Status bar with real-time request feedback
- Confirmation dialogs for destructive operations
- Better XML/JSON parsing and display
- PDF support for report downloads

**New Features:**
- List Scan Targets operation
- Get Host Details operation
- Search Vulnerabilities operation
- Get QID Details operation
- Sortable columns (click headers to sort)
- Both formatted and raw output generated simultaneously
- Enhanced custom request builder with parameter parsing 