## Obsidian Snapshot Generator
A simple script that compresses obsidian vault back ups to NAS as ZIP files every week.

## Potential additions to the script:
- Add a log file to track:
	- When the script runs
	- Whether a snapshot was created
	- Any errors or exceptions
	- Timestamped success/failure messages 
		- Wrap main logic in try/except to catch and log unforeseen errors
	- Email or desktop notifications if a snapshot fails
- Snapshot rotation / retention (delete old snapshots)
- Integrity verification (check if ZIPs are readable)
- Password encryption? 