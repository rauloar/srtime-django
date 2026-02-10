import re

# Read the actual line from the file
with open("C:/Proyectos/srtime-django/caso_real_sql/ZKTimeNet.db.sql", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()
    hr_company_line = lines[1903264]  # 0-based index

table_name = "hr_company"

print(f"Line length: {len(hr_company_line)}")
print(f"First 200 chars: {hr_company_line[:200]}")
print(f"Contains ';': {';' in hr_company_line}")
print(f"Starts with correct prefix: {hr_company_line.startswith('INSERT INTO \"hr_company\"')}")
print("\n" + "="*80)

# Test the regex
pattern = rf'INSERT INTO "{re.escape(table_name)}"\s+\((?P<cols>.+?)\)\s+VALUES\s+(?P<values>.+);'
match = re.search(pattern, hr_company_line, flags=re.DOTALL)

if match:
    print("✅ REGEX MATCHED!")
    columns = re.findall(r'"([^"]+)"', match.group("cols"))
    print(f"Columns found ({len(columns)}): {columns[:5]}...")
else:
    print("❌ REGEX DID NOT MATCH")
    
    # Try to understand why
    print("\n\nDebugging:")
    
    # Check if it has the right structure visually
    if "VALUES" in hr_company_line:
        idx = hr_company_line.index("VALUES")
        print(f"Found 'VALUES' at position {idx}")
        print(f"Context around VALUES: ...{hr_company_line[idx-20:idx+30]}...")
    
    # Try without \s+ to see if spacing is the issue
    pattern2 = rf'INSERT INTO "{re.escape(table_name)}" \((?P<cols>.+?)\) VALUES (?P<values>.+);'
    match2 = re.search(pattern2, hr_company_line, flags=re.DOTALL)
    if match2:
        print("\n✅ Works with literal spaces instead of \\s+")
    else:
        print("\n❌ Still doesn't work with literal spaces")
