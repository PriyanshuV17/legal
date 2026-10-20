import os
import json
import time
import pandas as pd

from rag import get_case_db
from llm_extractor import extract_case_info

# =========================
# CONFIG
# =========================
OUTPUT_CSV = r"D:\legal\data\case_dataset.csv"
CHECKPOINT_FILE = r"D:\legal\data\dataset_progress.json"

BATCH_SIZE = 1000
STEP_SIZE = 5000   # 🔥 process per run
SLEEP_TIME = 0.2


# =========================
# LOAD / SAVE CHECKPOINT
# =========================
def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            data = json.load(f)
            print(f"🔁 Resuming from offset {data['offset']}")
            return data["offset"]
    return 0


def save_checkpoint(offset):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"offset": offset}, f)


# =========================
# LOAD EXISTING DATASET
# =========================
def load_existing_data():
    if os.path.exists(OUTPUT_CSV):
        df = pd.read_csv(OUTPUT_CSV)
        print(f"📂 Loaded existing dataset: {len(df)} rows")
        return df.to_dict("records")
    return []


# =========================
# MAIN (ONE STEP ONLY)
# =========================
def main():
    db = get_case_db()

    print("📥 Incremental Dataset Builder (ONE STEP MODE)")

    offset = load_checkpoint()
    all_data = load_existing_data()

    start_offset = offset
    end_offset = offset + STEP_SIZE

    print(f"🎯 This run: {start_offset} → {end_offset}")

    while offset < end_offset:
        try:
            print(f"\n📦 Fetching batch: {offset}")

            results = db.get(
                limit=BATCH_SIZE,
                offset=offset,
                include=["documents", "metadatas"]
            )

            documents = results.get("documents", [])
            metadatas = results.get("metadatas", [])

            if not documents:
                print("✅ End of DB reached")
                break

            # =========================
            # GROUP BY FILE
            # =========================
            case_map = {}

            for text, meta in zip(documents, metadatas):
                file = meta.get("file", "unknown")

                if file not in case_map:
                    case_map[file] = ""

                case_map[file] += " " + text

            # =========================
            # LLM EXTRACTION
            # =========================
            for file, full_text in case_map.items():

                info = extract_case_info(full_text)

                if not info:
                    continue

                if info["outcome"] == "Unknown":
                    continue

                all_data.append({
                    "text": full_text[:1500],
                    "label": info["outcome"]
                })

            offset += BATCH_SIZE

            print(f"📊 Dataset size: {len(all_data)}")

            time.sleep(SLEEP_TIME)

        except Exception as e:
            print(f"⚠️ Error at offset {offset}: {e}")
            print("⏳ Retrying in 5 seconds...")
            time.sleep(5)

    # =========================
    # SAVE DATA + PROGRESS
    # =========================
    print("\n💾 Saving progress...")

    df = pd.DataFrame(all_data)
    df.to_csv(OUTPUT_CSV, index=False)

    save_checkpoint(offset)

    print(f"✅ Saved dataset (size: {len(all_data)})")
    print(f"📍 Next start offset: {offset}")
    print("🛑 Run script again to continue")


if __name__ == "__main__":
    main()