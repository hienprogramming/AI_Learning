#!/usr/bin/env python3
"""Test enhanced logging with TestReport class"""

from main import TestReport
import json
from pathlib import Path

def demo_test_report():
    """Demonstrate TestReport functionality"""
    print("\n" + "="*70)
    print("[DEMO] Enhanced Logging with TestReport")
    print("="*70 + "\n")
    
    # Create a test report
    report = TestReport("MCU Base", ["Boot_Mcu.h", "Boot_Mcu.c"])
    
    # Simulate code generation
    generated_code = """
    #ifndef BOOT_MCU_H
    #define BOOT_MCU_H
    
    void Boot_Mcu_Init(void);
    void Boot_Mcu_DeInit(void);
    void Boot_Mcu_DisableInterrupts(void);
    void Boot_Flash_Erase(uint32_t address, uint32_t length);
    void Boot_Flash_Write(uint32_t address, const uint8_t* data, uint32_t length);
    
    #endif
    """
    report.log_code_generation(generated_code)
    
    # Simulate test feedback with multiple issues
    test_feedback = """
    [TEST] Testing Boot_Mcu module
    
    [ERROR] Function Boot_Flash_Erase: Missing error handling for invalid address
    [ERROR] Function Boot_Flash_Write: Buffer overflow risk - missing bounds check
    [WARNING] Function Boot_Mcu_DisableInterrupts: Missing documentation for atomic operation
    [WARNING] Missing CRC validation after flash write operation
    [INFO] Code structure is good, follows embedded standards
    
    Recommendation: Add input validation and error codes before production use.
    """
    report.log_test_feedback(test_feedback)
    
    # Simulate fix application
    fixed_code = generated_code + "\n// Fixed: Added error handling and bounds checking\n"
    report.log_fix_applied(fixed_code, "Added validation and error handling for flash operations")
    
    # Print the report
    print("\n[DETAILED TEST REPORT OUTPUT]")
    print("-" * 70)
    report.print_report()
    
    # Show JSON format
    print("[JSON FORMAT]")
    print("-" * 70)
    report_dict = report.to_dict()
    print(json.dumps(report_dict, indent=2, ensure_ascii=False))
    
    # Show summary
    print("\n[SUMMARY]")
    print("-" * 70)
    summary = report_dict['summary']
    print(f"  Total Stages:    {summary['total_stages']}")
    print(f"  Issues Found:    {summary['issues_found']}")
    print(f"  Fixes Applied:   {summary['fixes_applied']}")

if __name__ == "__main__":
    demo_test_report()
    print("\n[SUCCESS] Test report demo completed!\n")
