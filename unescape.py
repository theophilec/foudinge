import os
import json


def unescape_xml_strings(file_path):
    """
    Takes a file containing a JSON string representation of XML and
    converts it to properly formatted XML.

    Args:
        file_path (str): Path to the file containing the XML string.

    Returns:
        str: Path to the new file with unescaped XML.
    """
    try:
        # Read the file
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()

        # If the content is wrapped in quotes, try to parse it as a JSON string
        if (content.startswith('"') and content.endswith('"')) or (
            content.startswith("'") and content.endswith("'")
        ):
            try:
                # Use JSON parsing to handle the escape sequences
                unescaped_content = json.loads(content)
            except json.JSONDecodeError:
                # If it's not valid JSON, try a more direct approach
                if content.startswith('"') and content.endswith('"'):
                    # Remove outer quotes and unescape
                    unescaped_content = (
                        content[1:-1]
                        .replace('\\"', '"')
                        .replace("\\\\", "\\")
                        .replace("\\n", "\n")
                    )
                else:
                    unescaped_content = content
        else:
            # If not wrapped in quotes, assume it's already properly formatted
            unescaped_content = content

        # Create output path
        base_name = os.path.basename(file_path)
        dir_name = os.path.dirname(file_path)
        file_name, ext = os.path.splitext(base_name)
        output_path = os.path.join(dir_name, f"{file_name}_unescaped.gexf")

        # Write the unescaped content to the new file
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(unescaped_content)

        print(f"Successfully unescaped XML and saved to {output_path}")
        return output_path

    except Exception as e:
        print(f"Error processing file: {e}")
        return None


unescaped_file = unescape_xml_strings("network-post-gephi.gexf")
print(f"Unescaped file saved at: {unescaped_file}")
