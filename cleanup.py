import os
import json
from datetime import datetime, timedelta , timezone

def cleanup_files(max_age_hours=30):
    try:
        # Read metadata
        with open("metadata/metadata_list.json", "r") as f:
            metadata_list = json.load(f)
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

        files_to_remove = []
        
        for metadata in metadata_list:
            try:
                # Check JSON file age
                json_path = metadata["json_filename"]
                if not os.path.exists(json_path):
                    continue
                    
                uploadedAt = datetime.fromisoformat(metadata["upload_timestamp"])

                # If file is old enough, delete it
                if uploadedAt <= cutoff_time:
                    # Delete JSON file
                    os.unlink(json_path)
                    
                files_to_remove.append(metadata["uuid"])
                print(f"Deleted files for job: {metadata['uuid']}")
                    
            except Exception as e:
                print(f"Error processing {metadata.get('uuid', 'unknown')}: {e}")
        
        # Update metadata file
        if files_to_remove:
            updated_metadata = [m for m in metadata_list if m["uuid"] not in files_to_remove]
            with open("metadata/metadata_list.json", "w") as f:
                json.dump(updated_metadata, f, indent=4)
            print(f"Removed {len(files_to_remove)} entries from metadata")
                
    except Exception as e:
        print(f"Cleanup error: {e}")