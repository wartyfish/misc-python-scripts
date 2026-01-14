import os, zipfile, re, logging, sys
from pathlib import Path
from datetime import datetime, timedelta
from winotify import Notification, audio

log_path = Path(__file__).with_name("vault_snapshots.log")
logging.basicConfig(
    level=logging.INFO,
    filename=log_path,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
    )

logger = logging.getLogger(__name__)

# Windows notification for when program fails
def notify(title: str, message: str) -> None:
    toast = Notification(
        app_id="Obsidian Vault Backup",
        title=title,
        msg=message,
        duration="long"
    )
    toast.set_audio(audio.Default, loop=False)
    toast.show()

# Validate if P: drive is accessible
def validate_destination_path(destination_path) -> None:
    try:
        if not destination_path.exists():
            logger.error("Destination path does not exist or is not accessible")
            raise FileNotFoundError(destination_path)

    except OSError:
        logger.exception("Failed while attempting to access destination path")
        raise

def main():
    logger.info("Vault snapshot task started")
    completion_message = ""

    target_path = Path(r"C:\Users\Eem\Dropbox\Jamies Vault")
    destination_path = Path(r"\\192.168.1.106\home\Obsidian vault backups")
    create_snapshot = False

    try:
        validate_destination_path(destination_path)
    except Exception as e:
        notify(
            "Vault Backup Failed",
            "Destination path is not accessible.\nCheck network connection."
        )
        sys.exit(1)

    # date snapshot to yesterdays date
    yesterdays_date = datetime.today() - timedelta(days=1)
    snapshot_name = f"{yesterdays_date.strftime('%y%m%d')}_JamiesVaultSnapshot.zip"

    # specify how frequently to make snapshots
    interval_between_snapshots = 7

    snapshots = list(destination_path.glob("*_JamiesVaultSnapshot.zip"))

    # validate if any snapshots exist
    # if not, proceed and create snapshot
    # else, find date of most recent snapshot
    if not snapshots:
        create_snapshot = True
        logger.info("No existing snapshots found; snapshot will be created")
    else:
        latest_snapshot = max(snapshots)
        latest_snapshot_date = datetime.strptime(
        re.search(r"(\d{6})_JamiesVaultSnapshot\.zip", latest_snapshot.name).group(1),
        "%y%m%d"
        )
        days_since_last_snapshot = (yesterdays_date - latest_snapshot_date).days

        if days_since_last_snapshot >= interval_between_snapshots:
            create_snapshot = True
            logger.info("Snapshot interval exceeded; snapshot will be created")
        else:
            logger.info("Snapshot interval not exceeded; no snapshot created")
            completion_message = "Snapshot interval not exceeded; no new snapshot created."

    # create zipfile 
    if create_snapshot:
        try:
            with zipfile.ZipFile(destination_path / snapshot_name, "w") as zipf:
                for root, dirs, files in os.walk(target_path):
                    dirs[:] = [x for x in dirs if x != ".obsidian"]
                    for file in files:
                        full_path = Path(root) / file
                        arcname = full_path.relative_to(target_path)
                        zipf.write(full_path, arcname, compress_type=zipfile.ZIP_DEFLATED)
            
            logger.info("Snapshot created successfully: %s", snapshot_name)
            completion_message = "New snapshot created\n"
        
        except Exception:
            logger.exception("Snapshot creation failed")
            notify(
                "Vault Backup Failed",
                "An error occured while creating the snapshot.\nCheck logs.\n"
            )
            sys.exit(1)

    logger.info("Vault snapshot task finished")
    notify(
    "Vault Snapshot tast finished successfully",
    completion_message
    )

try:
    main()
except Exception as e:
    logger.exception("Snapshot failed; program encountered an unforeseen error")
    notify(
        "Vault Backup Failed",
        f"Program encountered an unforeseen error:\n{e}\n"
    )
    sys.exit(1)




