import re

# Sample from actual dump
statement = '''INSERT INTO "hr_department" 
("id","dept_code","dept_name","dept_parentcode","dept_operationmode","middleware_id","defaultDepartment","company_id","shift_id")
VALUES (1,3,'Moldeo',0,0,0,1,1,3);'''

table_name = "hr_department"

# Current regex
pattern = rf'INSERT INTO "{re.escape(table_name)}"\s+\((?P<cols>.+?)\)\s+VALUES\s+(?P<values>.+);'

print("Testing regex...")
print(f"Pattern: {pattern}")
print(f"\nStatement:\n{statement}")
print("\n" + "="*80)

match = re.search(pattern, statement, flags=re.DOTALL)

if match:
    print("✅ MATCH FOUND!")
    print(f"\nColumns group: {match.group('cols')[:100]}...")
    print(f"\nValues group: {match.group('values')[:100]}...")
    
    # Extract column names
    columns = re.findall(r'"([^"]+)"', match.group("cols"))
    print(f"\nExtracted columns ({len(columns)}): {columns}")
else:
    print("❌ NO MATCH")
    
    # Try simpler patterns to debug
    print("\n\nTrying simpler patterns...")
    
    simple1 = rf'INSERT INTO "{re.escape(table_name)}"'
    if re.search(simple1, statement):
        print(f"✅ Found: {simple1}")
    else:
        print(f"❌ Not found: {simple1}")
    
    simple2 = rf'INSERT INTO "{re.escape(table_name)}"\s+'
    if re.search(simple2, statement):
        print(f"✅ Found: {simple2}")
    else:
        print(f"❌ Not found: {simple2}")
    
    simple3 = rf'INSERT INTO "{re.escape(table_name)}"\s+\('
    if re.search(simple3, statement):
        print(f"✅ Found: {simple3}")
    else:
        print(f"❌ Not found: {simple3}")
