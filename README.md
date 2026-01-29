# XML Test Viewer

A lightweight Windows desktop app to view JUnit XML test reports with tree structure and quick copy for AI debugging.

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

## Features

- 📁 Tree view with collapsible test suites
- ✅❌ Visual pass/fail status labels
- 📋 One-click copy failures as YAML (AI-friendly format)
- 🎨 Modern dark theme UI

## Quick Start

```bash
python main.py
# or with file
python main.py path/to/results.xml
```

## Build Executable

```bash
build.bat
# Output: dist/XMLTestViewer.exe
```

## Copy Output Format

```yaml
failures:
  - name: "testMethod()"
    classname: "org.example.TestClass"
    failure:
      type: "AssertionFailedError"
      message: "expected <true> but was <false>"
      stacktrace: |
        at org.junit.jupiter.api...
```

## License

MIT
