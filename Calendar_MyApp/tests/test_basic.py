import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import parse_file, create_ics

def test_workflow():
    sample_csv = os.path.join(os.path.dirname(__file__), 'sample.csv')
    print(f"Testing parse on {sample_csv}...")
    
    events = parse_file(sample_csv)
    print(f"Extracted {len(events)} events:")
    for e in events:
        print(e)
        
    if len(events) != 3:
        print("FAIL: Expected 3 events.")
        sys.exit(1)
        
    print("\nTesting ICS generation...")
    ics_data = create_ics(events)
    print("ICS Content Preview:")
    print(ics_data[:200])
    
    if "BEGIN:VCALENDAR" not in ics_data:
        print("FAIL: Invalid ICS content")
        sys.exit(1)
        
    print("\nSUCCESS: Basic workflow verified.")

if __name__ == "__main__":
    test_workflow()
