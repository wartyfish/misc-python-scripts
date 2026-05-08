## Obsidian Snapshot Generator
A simple script that compresses obsidian vault back ups to NAS as ZIP files every week.

## Devlog

### 20/04/26
Script now copies new images to a seperate repo to avoid unecessary folder bloat.

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