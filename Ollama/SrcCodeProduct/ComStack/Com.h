### Explanation of Changes

1. **Error Handling**:
   - Added `E_BUSY` error code in the `Com_SendSignal` and `Com_ReceiveSignal` functions to indicate that the main function is already running.
   - Added checks to ensure that the main function is not already running before attempting to trigger it.

2. **Reentrancy Protection**:
   - Implemented a mechanism to prevent reentrant calls by checking if the main function is already running and returning `E_BUSY` if it is.

3. **Synchronization Mechanisms**:
   - Added flags (`txMainFunctionRunning` and `rxMainFunctionRunning`) to indicate whether the main functions are currently running.
   - Set these flags before triggering the main functions and reset them after their execution.

4. **Enhanced Signal Filtering and Triggering Logic**:
   - Provided a placeholder for signal filtering and triggering logic in the main functions (`Com_MainFunctionTx` and `Com_MainFunctionRx`). You can implement more sophisticated logic based on your application requirements.

### Usage

1. **Initialization**:
