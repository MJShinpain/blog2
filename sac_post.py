import csv
import os
import re

# Set the base directory of the project
base_directory = os.path.dirname(os.path.abspath(__file__))

# Set the relative paths for the CSV file and output directory
csv_file = os.path.join(base_directory, "data", "sac.csv")
output_directory = os.path.join(base_directory, "content", "post")

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Open the CSV file and iterate over each row
with open(csv_file, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Extract the relevant information from the row
        name = row["name"]
        date = row["date"]
        price = row["price"]
        additional_info = row["additional_info"]
        link = row["link"]

        # Remove invalid characters from the name
        name = re.sub(r'[<>:"/\\|?*]', '', name)

        # Replace newline characters with <br> tags or double spaces for markdown
        additional_info = additional_info.replace('\n', '  \n')

        # Generate the markdown file name
        file_name = f"{date}-{name}.md"
        file_path = os.path.join(output_directory, file_name)

        # Generate the markdown content
        markdown_content = f"""---
title: "({date}) {name}"
---

# 제목
{name}

# 일시
{date}

# 가격
{price}

# 공연정보
{additional_info}

# 링크
[자세히 보기]({link}, "{link}")
"""

        # Write the markdown content to the file
        with open(file_path, "w", encoding="utf-8") as markdown_file:
            markdown_file.write(markdown_content)

print("Markdown files generated successfully!")