#!/usr/bin/env python3
"""
Debug chart sections to see what's in the holding days chart implementation
"""

import requests

def debug_chart_sections():
    base_url = "http://localhost:5001"
    
    try:
        response = requests.get(f"{base_url}/static/js/expectation-comparison-manager.js")
        
        if response.status_code == 200:
            js_content = response.text
            
            # Find the holding days chart section
            holding_days_start = js_content.find('renderHoldingDaysChart')
            success_rate_start = js_content.find('renderSuccessRateChart')
            
            if holding_days_start != -1 and success_rate_start != -1:
                holding_days_section = js_content[holding_days_start:success_rate_start]
                
                print("Holding Days Chart Section:")
                print("=" * 50)
                print(holding_days_section[:1000])  # First 1000 chars
                print("=" * 50)
                
                print(f"Contains backgroundColor: {'backgroundColor' in holding_days_section}")
                print(f"Contains borderColor: {'borderColor' in holding_days_section}")
                print(f"Contains tooltip: {'tooltip' in holding_days_section}")
                
                # Search for specific color patterns
                if 'rgba(54, 162, 235' in holding_days_section:
                    print("✅ Found blue color (期望)")
                if 'rgba(255, 99, 132' in holding_days_section:
                    print("✅ Found red color (实际)")
                    
            else:
                print("Could not find chart sections")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_chart_sections()