<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# Communication

與使用者互動時一律使用繁體中文回覆，無論使用者使用何種語言。
完成每一項工作以系統鈴聲提醒。
如果遇到執行中斷，兩分鐘後重新嘗試。如果五次失敗發生系統鈴聲來提醒
每完成一項工作則發出系統鈴聲提醒
每一個修改請先提供計劃，確認後才開始修改
每一個修改完成後，請先進行測試，如果發現問題則再次修改。直到系統能穩定執行

# Execution Strategy

預設 approval_policy = never，所有指令免逐次核准。
開發新函數前請先檢查 @func.md 看是否有類似的功能！如果有試著直接調用。如果無法使用達到設計目標才開發新的功能。
建立新的函數後，都添加函數子程序的名稱與功能進 @func.md 中
每次修改完畢後都必須進行功能測試，測試有錯誤則繼續修改直到系統能穩定執行才能終止
全功能測試則需要完整的測試所有功能，包含按鈕，資料輸入，資料輸出，畫面上文字的完整性與正確性。所有表單的內容都是正確無誤。

# Execution Environment (for future collaboration)

sandbox_mode: danger-full-access
approval_policy: never, 所有指令免逐次審核
network_access: full accessed

# Build, Lint, Test Commands

This project uses OpenSpec for spec-driven development. Currently, no build/test/lint configuration is set up.

Update this section with actual commands when code is added:
```bash
# Build
npm run build  # or python -m build, or cargo build, etc.

# Lint
npm run lint   # or ruff check ., or pylint, etc.

# Format
npm run format # or black ., or prettier --write .

# Tests
npm test               # Run all tests
npm test path/to/test  # Run single test file
pytest tests/test_x.py  # Python: run single test file
pytest tests/test_x.py::test_func  # Python: run single test function
```

# Code Style Guidelines

## Imports
- Import standard library first, then third-party, then local modules
- Use absolute imports when available
- Avoid wildcard imports

## Formatting
- Use [formatter] with [config]
- Max line length: [N] characters
- Indent with [spaces/tabs]
- Trailing commas for multi-line structures

## Types
- Use strict type checking
- Explicit return types on functions
- Avoid `any`/`unknown` types
- Interface types for public APIs

## Naming Conventions
- Variables: camelCase
- Constants: UPPER_SNAKE_CASE
- Functions: camelCase
- Classes: PascalCase
- Files: kebab-case
- Directories: kebab-case

## Error Handling
- Handle expected errors gracefully
- Use typed custom errors
- Always preserve error context
- Never silently swallow errors

## Architecture
- Keep components small and focused
- Prefer composition over inheritance
- Use dependency injection
- Separate concerns (data, view, logic)

## Documentation
- Document public APIs with docstrings
- Add comments for non-obvious logic
- Update README for breaking changes
- Keep inline comments minimal

# OpenSpec Workflow

Before implementing features:
1. Check `openspec spec list --long` for existing specs
2. Create change proposal for new features or breaking changes
3. Validate with `openspec validate [change-id] --strict`
4. Implement after proposal approval
5. Archive with `openspec archive <change-id>` after deployment

See `openspec/AGENTS.md` for detailed OpenSpec instructions.
