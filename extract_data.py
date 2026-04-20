"""Extract knowledge data from HTML file and write Python knowledge files."""
import os

INPUT_FILE = 'D:/dachuang/4.12_quanwen_qianru.html'
OUTPUT_DIR = 'D:/dachuang/zhibei_backend/knowledge'

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()


def extract_template_literal(start_line_1indexed, end_line_1indexed):
    """Extract content between backticks from HTML file.
    start_line is the line with `const XXX = `...`
    Returns the text content between backticks."""
    start_idx = start_line_1indexed - 1  # Convert to 0-indexed
    first_line = lines[start_idx]
    # Extract text after the opening backtick on the first line
    after_backtick = first_line.split('= `', 1)[1] if '= `' in first_line else first_line.split('= `', 1)[-1]

    content_lines = [after_backtick]
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        # Check for closing backtick (may be on its own line or at end of content)
        stripped = line.rstrip('\n').rstrip('\r')
        if stripped.endswith('`;'):
            # Content before closing backtick
            before_close = stripped[:-2]  # Remove `; at end
            content_lines.append(before_close)
            break
        elif stripped == '`':
            break
        else:
            content_lines.append(stripped)

    return '\n'.join(content_lines)


def python_escape_string(s):
    """Escape a string for use in Python triple-quoted string."""
    # Replace backslashes first, then triple quotes
    s = s.replace('\\', '\\\\')
    s = s.replace('"""', '\\"\\"\\"')
    return s


def write_template_var(var_name, content, filename):
    """Write a Python file with a string variable."""
    escaped = python_escape_string(content)
    py_content = f'# Auto-generated from HTML extraction\n{var_name} = """{escaped}"""\n'
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(py_content)
    print(f"Written {filename}: {len(content)} chars")


# Extract KEBIAO_FULL_TEXT (lines 2447-11807)
kebiao_text = extract_template_literal(2447, 11807)
write_template_var('KEBIAO_FULL_TEXT', kebiao_text, 'kebiao_full_text.py')

# Extract GRADE4A_TEACHING_FOCUS_FULL (lines 11816-11882)
grade4a_focus = extract_template_literal(11816, 11882)
write_template_var('GRADE4A_TEACHING_FOCUS_FULL', grade4a_focus, 'grade4a_teaching_focus_full.py')

# Extract GRADE4A_READING_GUIDE_FULL (lines 11885-12130)
grade4a_guide = extract_template_literal(11885, 12130)
write_template_var('GRADE4A_READING_GUIDE_FULL', grade4a_guide, 'grade4a_reading_guide_full.py')

print("\nDone! Large template literals extracted.")
