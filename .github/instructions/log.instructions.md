### Logging
```json
{
  "timestamp": "ISO format",
  "level": "ERROR",
  "module": "module_name",
  "function": "function_name", 
  "line": 42,
  "message": "Error message",
  "traceback": "full traceback for errors"
}
```
1. Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
2. Console output with colors for different levels
3. Rotating file handler with 10MB limit keeping 5 backup files
4. JSON formatting option for structured logging
5. Function decorator to auto-log calls with timing
6. Error logging helper that captures stack traces
7. Configurable via environment variables or config file
8. Include example usage showing:
   - Basic logging
   - Function tracing
   - Error handling with context
   - Conditional debug logging

### Levels
- **INFO**: Fetch start/end, category completion
- **ERROR**: Network/parsing failures
- **DEBUG**: Skipped articles

### Rotation
- Daily rotation, keep 30 days