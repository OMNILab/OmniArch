# SmartMeeting Agent Tests

This directory contains comprehensive unit tests and integration tests for the migrated `smartmeeting.agent` module.

## 📁 Test Structure

```
tests/
├── test_agent_state.py      # Tests for AgentState TypedDict
├── test_agent_config.py     # Tests for configuration and LLM setup
├── test_agent_tools.py      # Tests for booking tools (recommend, book, cancel, etc.)
├── test_agent_nodes.py      # Tests for graph nodes (llm_call, interrupt_handler)
├── test_agent_graph.py      # Tests for graph building and compilation
├── test_agent_integration.py # Integration tests for complete workflows
├── test_agent_runner.py     # Test runner script
└── AGENT_TESTS_README.md    # This file
```

## 🧪 Test Coverage

### 1. Agent State Tests (`test_agent_state.py`)
- **AgentState TypedDict creation and validation**
- **Optional field handling** (current_user_id, current_username)
- **Message list management**
- **Type annotation verification**

### 2. Agent Config Tests (`test_agent_config.py`)
- **LLM initialization** with environment variables
- **Tools list generation** and validation
- **System prompt generation** with user context
- **HITL tools identification** (dangerous vs safe tools)
- **Error handling** for missing API keys

### 3. Agent Tools Tests (`test_agent_tools.py`)
- **Room recommendation** with various filters (capacity, equipment, location)
- **Time conflict detection** and resolution
- **Room booking** success and failure scenarios
- **User booking lookup** with future/past filtering
- **Booking cancellation** with partial failure handling
- **Booking alteration** (currently returns guidance)

### 4. Agent Nodes Tests (`test_agent_nodes.py`)
- **LLM call node** with and without tool calls
- **Interrupt handler** for safe and dangerous tools
- **User interaction simulation** (accept, ignore, edit, respond)
- **State management** and message flow
- **Error handling** for unknown response types

### 5. Agent Graph Tests (`test_agent_graph.py`)
- **Graph building** and compilation
- **Node and edge verification**
- **Checkpointer integration**
- **Custom checkpointer support**
- **Error handling** in graph construction

### 6. Agent Integration Tests (`test_agent_integration.py`)
- **Complete conversation workflows**
- **Safe tool execution** without user intervention
- **Dangerous tool execution** with user confirmation
- **State persistence** across multiple calls
- **User information integration**
- **Error propagation** and handling

## 🚀 Running the Tests

### Prerequisites
```bash
# Install test dependencies
pip install pytest pytest-mock

# Set up environment variables (optional for mocked tests)
export DASHSCOPE_API_KEY="test_key"
```

### Run All Agent Tests
```bash
# From the smartmeeting directory
python tests/test_agent_runner.py
```

### Run Individual Test Files
```bash
# Run specific test file
pytest tests/test_agent_tools.py -v

# Run with coverage
pytest tests/test_agent_tools.py --cov=smartmeeting.agent.tools -v

# Run with detailed output
pytest tests/test_agent_tools.py -v -s
```

### Run Specific Test Classes
```bash
# Run specific test class
pytest tests/test_agent_tools.py::TestAgentTools -v

# Run specific test method
pytest tests/test_agent_tools.py::TestAgentTools::test_recommend_available_rooms_basic -v
```

## 🔧 Test Configuration

### Mock Strategy
The tests use extensive mocking to avoid:
- **External API calls** (LLM services)
- **Database operations** (using mock DataManager)
- **Streamlit UI interactions** (mocked responses)
- **File system operations** (in-memory data)

### Test Data
Each test file includes:
- **Mock room data** with various capacities and equipment
- **Mock meeting data** with time conflicts
- **Mock user data** for testing user-specific operations
- **Realistic test scenarios** based on actual use cases

### Environment Variables
Tests handle missing environment variables gracefully:
- **DASHSCOPE_API_KEY** - Mocked for LLM tests
- **Database connections** - Mocked DataManager
- **External services** - All external calls are mocked

## 📊 Test Metrics

### Coverage Goals
- **Unit test coverage**: >90% for all modules
- **Integration test coverage**: All major workflows
- **Error handling coverage**: All exception paths
- **Edge case coverage**: Boundary conditions and invalid inputs

### Performance Targets
- **Individual test execution**: <1 second
- **Full test suite**: <30 seconds
- **Memory usage**: Minimal (mocked external dependencies)

## 🐛 Debugging Tests

### Common Issues
1. **Import errors**: Ensure you're running from the smartmeeting directory
2. **Mock failures**: Check that all external dependencies are properly mocked
3. **Type errors**: Verify that test data matches expected types

### Debug Mode
```bash
# Run with debug output
pytest tests/test_agent_tools.py -v -s --pdb

# Run with detailed logging
pytest tests/test_agent_tools.py -v --log-cli-level=DEBUG
```

### Test Isolation
Each test is designed to be independent:
- **Fresh mocks** for each test method
- **No shared state** between tests
- **Cleanup** of any created resources

## 🔄 Continuous Integration

### GitHub Actions Integration
The tests are designed to run in CI environments:
- **No external dependencies** required
- **Fast execution** for quick feedback
- **Clear error messages** for debugging
- **Comprehensive coverage** reporting

### Pre-commit Hooks
Consider adding these tests to pre-commit hooks:
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: agent-tests
      name: Agent Tests
      entry: python tests/test_agent_runner.py
      language: system
      pass_filenames: false
```

## 📝 Adding New Tests

### Test Naming Convention
- **Test files**: `test_<module_name>.py`
- **Test classes**: `Test<ClassName>`
- **Test methods**: `test_<functionality>_<scenario>`

### Test Structure
```python
def test_functionality_scenario(self):
    """Test description"""
    # Arrange - Setup test data and mocks
    # Act - Execute the function being tested
    # Assert - Verify the results
```

### Mock Guidelines
- **Mock at the lowest level** possible
- **Use realistic test data** that matches production scenarios
- **Test both success and failure** paths
- **Verify mock interactions** when relevant

## 🎯 Test Quality Standards

### Code Quality
- **Clear test names** that describe the scenario
- **Comprehensive docstrings** explaining test purpose
- **Proper setup and teardown** methods
- **Meaningful assertions** with descriptive messages

### Maintainability
- **DRY principle** - avoid code duplication
- **Test data factories** for complex objects
- **Shared fixtures** for common setup
- **Clear separation** of concerns

### Reliability
- **Deterministic tests** - same result every time
- **No external dependencies** - fully mocked
- **Fast execution** - no slow operations
- **Proper cleanup** - no side effects

## 📚 Additional Resources

- **pytest documentation**: https://docs.pytest.org/
- **unittest.mock documentation**: https://docs.python.org/3/library/unittest.mock.html
- **LangGraph testing**: https://langchain-ai.github.io/langgraph/
- **LangChain testing**: https://python.langchain.com/docs/use_cases/testing

## 🤝 Contributing

When adding new agent functionality:
1. **Write tests first** (TDD approach)
2. **Ensure all tests pass** before committing
3. **Update this README** if adding new test categories
4. **Maintain test coverage** above 90%

---

*Last updated: January 2025* 