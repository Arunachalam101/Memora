import requests
import re

response = requests.get('http://localhost:5000/caregiver-dashboard', headers={'Cookie': 'session=test'})

# Save the full HTML to a file for inspection
with open('caregiver_dashboard_response.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print(f'HTML response length: {len(response.text)} characters')
print(f'Status code: {response.status_code}')

# Check for where the HTML ends
lines = response.text.split('\n')
print(f'Total lines: {len(lines)}')

# Find where patient overview ends
for i, line in enumerate(lines):
    if 'patient-overview' in line or 'Patient Overview' in line:
        print(f'Patient Overview found at line {i}')
        
# Find where progress charts section should be
for i, line in enumerate(lines):
    if 'progress-charts' in line:
        print(f'Progress Charts found at line {i}')

# Look for the container div and its closing
for i, line in enumerate(lines):
    if '<div class="container">' in line:
        print(f'Container div opens at line {i}')
    if '</div>' in line and i > 50:
        # Count divs to find the main container close
        preceding = response.text[:response.text.find(lines[i])].count('<div') - response.text[:response.text.find(lines[i])].count('</div>')
        if preceding == 1:
            print(f'Container div closes at line {i}')
            break

# Look for the last thing in the HTML
print(f'\nLast 500 characters of HTML:')
print(response.text[-500:])

