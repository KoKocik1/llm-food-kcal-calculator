import os
from bs4 import BeautifulSoup
from typing import Set, Optional
from pathlib import Path


class HTMLCleaner:
    def __init__(self):
        self.allowed_classes: Set[str] = {
            "MuiBox-root jss365",
            "MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-lg-8",
        }

        self.disallowed_classes: Set[str] = {
            "MuiListItemAvatar-root",
            "MuiBox-root jss417",
            "MuiBox-root jss419",
            "jss5",
        }

        self.disallowed_class_section: Set[str] = {
            "jss10",
        }

    def process_html(self, file_path: Path) -> Optional[BeautifulSoup]:
        """Process a single HTML file and return cleaned BeautifulSoup object"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")

            # Remove disallowed divs
            for div in soup.find_all(
                "div", class_=lambda c: c in self.disallowed_classes if c else False
            ):
                div.decompose()

            for section in soup.find_all(
                "section",
                class_=lambda c: c in self.disallowed_class_section if c else False,
            ):
                section.decompose()

            # Keep only allowed divs
            filtered_divs = soup.find_all(
                "div", class_=lambda c: c in self.allowed_classes if c else False
            )

            # Create a new soup with only allowed divs
            new_soup = BeautifulSoup(
                "<html><body></body></html>", "html.parser")
            body = new_soup.body

            for div in filtered_divs:
                body.append(div)

            return new_soup

        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            return None

    def save_processed_html(
        self, original_path: Path, processed_soup: BeautifulSoup
    ) -> None:
        """Save processed HTML while maintaining the folder structure"""
        try:
            base_dir = Path("calories_info")
            output_base_dir = Path("calories_info_processed")

            # Construct new file path
            relative_path = original_path.relative_to(base_dir)
            output_path = output_base_dir / relative_path

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save the processed file
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(str(processed_soup.prettify()))

            print(f"Processed and saved: {output_path}")

        except Exception as e:
            print(f"Error saving {original_path}: {str(e)}")

    def process_directory(self, base_dir: Path) -> None:
        """Process all HTML files in directory and subdirectories"""
        try:
            # Walk through all directories and files
            for html_file in base_dir.rglob("*.html"):
                processed_soup = self.process_html(html_file)
                if processed_soup:
                    self.save_processed_html(html_file, processed_soup)

        except Exception as e:
            print(f"Error processing directory {base_dir}: {str(e)}")


def main():
    try:
        base_dir = Path("calories_info")
        if not base_dir.exists():
            raise FileNotFoundError(f"Directory {base_dir} not found")

        cleaner = HTMLCleaner()
        cleaner.process_directory(base_dir)

    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
