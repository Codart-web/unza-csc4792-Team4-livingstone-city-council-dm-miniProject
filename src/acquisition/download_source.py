from pathlib import Path
import requests


def download_file(url: str, output_path: str) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(
        url,
        timeout=60,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "CSC4792-Livingstone-Research/1.0"
            )
        },
    )
    response.raise_for_status()

    output.write_bytes(response.content)

    return output


if __name__ == "__main__":
    print("Source acquisition utility loaded.")
    print("Provide a verified source URL before downloading.")
