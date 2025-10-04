"""
Smoke Test Execution Script
Executes smoke tests from the Excel test suite
"""

from src.core.multi_sheet_controller import MultiSheetTestController
from datetime import datetime

def execute_smoke_tests():
    print('🚀 EXECUTING SMOKE TESTS FROM EXCEL TEST SUITE')
    print('=' * 60)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'Generated: {timestamp}')
    print('Test Suite: sdm_test_suite.xlsx')
    print('Target Sheet: SMOKE')
    print()

    # Initialize controller
    controller = MultiSheetTestController('sdm_test_suite.xlsx')
    controller.load_workbook()
    controller.load_controller_data()

    print('📋 EXECUTING SMOKE TESTS ONLY...')
    print('-' * 40)

    # Execute only SMOKE sheet
    smoke_results = controller.execute_controlled_tests(sheet_names=['SMOKE'])

    print('\n📊 SMOKE TEST EXECUTION RESULTS')
    print('=' * 50)

    if 'SMOKE' in smoke_results:
        results = smoke_results['SMOKE']
        
        total_tests = len(results)
        passed_tests = len([r for r in results if r.status == 'PASS'])
        failed_tests = len([r for r in results if r.status == 'FAIL'])
        skipped_tests = len([r for r in results if r.status == 'SKIP'])
        error_tests = len([r for r in results if r.status == 'ERROR'])
        
        total_duration = sum(r.duration_seconds for r in results)
        
        print('📈 SUMMARY:')
        print(f'   Total Tests: {total_tests}')
        print(f'   ✅ Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)')
        print(f'   ❌ Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)')
        print(f'   ⏭️  Skipped: {skipped_tests} ({skipped_tests/total_tests*100:.1f}%)')
        if error_tests > 0:
            print(f'   💥 Errors: {error_tests} ({error_tests/total_tests*100:.1f}%)')
        print(f'   ⏱️  Duration: {total_duration:.2f}s')
        
        execution_rate = ((total_tests - skipped_tests)/total_tests*100) if total_tests > 0 else 0
        print(f'   📊 Execution Rate: {execution_rate:.1f}%')
        
        print('\n📋 DETAILED TEST RESULTS:')
        print('-' * 30)
        
        # Group results by status for better organization
        passed_results = [r for r in results if r.status == 'PASS']
        failed_results = [r for r in results if r.status == 'FAIL']
        skipped_results = [r for r in results if r.status == 'SKIP']
        
        if passed_results:
            print(f'\n✅ PASSED TESTS ({len(passed_results)}):')
            for i, result in enumerate(passed_results, 1):
                print(f'   {i:2d}. {result.test_case_id} - {result.test_case_name}')
                print(f'       Category: {result.category} | Duration: {result.duration_seconds:.3f}s')
        
        if failed_results:
            print(f'\n❌ FAILED TESTS ({len(failed_results)}):')
            for i, result in enumerate(failed_results, 1):
                print(f'   {i:2d}. {result.test_case_id} - {result.test_case_name}')
                print(f'       Category: {result.category} | Duration: {result.duration_seconds:.3f}s')
                if result.error_message:
                    print(f'       Error: {result.error_message}')
        
        if skipped_results:
            print(f'\n⏭️  SKIPPED TESTS ({len(skipped_results)}):')
            for i, result in enumerate(skipped_results, 1):
                print(f'   {i:2d}. {result.test_case_id} - {result.test_case_name}')
                print(f'       Category: {result.category}')
                if result.error_message:
                    print(f'       Reason: {result.error_message}')
                else:
                    print(f'       Reason: Category not implemented')
                
    else:
        print('❌ No SMOKE test results found!')

    print('\n🎯 SMOKE TEST ANALYSIS:')
    print('-' * 25)
    if 'SMOKE' in smoke_results and smoke_results['SMOKE']:
        results = smoke_results['SMOKE']
        core_tests = [r for r in results if r.category in ['SETUP', 'CONFIGURATION', 'SECURITY', 'CONNECTION', 'QUERIES']]
        core_passed = len([r for r in core_tests if r.status == 'PASS'])
        
        print(f'✅ Core Framework Tests: {core_passed}/{len(core_tests)} passed')
        framework_status = 'YES' if core_passed == len(core_tests) else 'PARTIAL'
        print(f'📊 Core functionality operational: {framework_status}')
        readiness = 'READY' if core_passed >= 3 else 'NEEDS ATTENTION'
        print(f'🚀 Framework readiness: {readiness}')

    print('\n✅ SMOKE TEST EXECUTION COMPLETE!')

if __name__ == "__main__":
    execute_smoke_tests()