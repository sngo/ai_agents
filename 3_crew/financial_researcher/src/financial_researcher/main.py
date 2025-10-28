#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from financial_researcher.crew import FinancialResearcher

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    inputs = {
        'company': 'Apple',
    }
    
    try:
        result = FinancialResearcher().crew().kickoff(inputs=inputs)
        # Print the result
        print("\n\n=== FINAL REPORT ===\n\n")
        print(result.raw)

        print("\n\nReport has been saved to output/report.md")
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

   
