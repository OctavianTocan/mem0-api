## Coding Guidelines
When writing code, follow these principles to ensure clarity, maintainability, and quality:

### Single Responsibility Per Function
- Functions should only do one thing.
- They should do it well.
- And they should do it only.
- If you can describe the function with "and," it likely needs splitting.
- If you can extract functionality from within the function without restating its purpose, it likely needs splitting.
- If you have multiple sections within a function, that's a symptom of the curse of the function with more than one purpose. It needs splitting.
- Functions should be small—ideally no more than 20 lines
- If a function does only those steps that are one level below the stated name

### Only One Level Of Abstraction Per-function
- Make sure that all statements within a function are at the same level of abstraction. Mixing levels of abstraction within a function is always confusing.
- Reading code should feel like reading well-written prose

### Keep Function Bodies Short
- Aim for readable, scannable function bodies
- Long bodies indicate mixed responsibilities
- Delegate to helpers rather than implementing everything inline.
- Short functions are easier to understand, test, and maintain.
- Blocks within a function, `if` statements, `else` statements, `while` statements, and so on should be one line each. And that line should probably be a function call.
- The indent level of a function should not be greater than one or two. Functions should never be large enough to hold nested structures.
- Functions should hardly ever be longer than 20 lines. Aim for 5-10 lines where possible

### Separate Concerns into Layers
- Lookup/Search: Finding or locating entities
- Extraction: Processing and transforming data
- Persistence: Saving, I/O, and side effects
- Orchestration: Coordinating multiple helpers
- Each layer should be independently understandable

### Isolate Side Effects
- Group side-effecting operations (I/O, editor access, notifications, logging)
- Keep pure functions separate from those with side effects
- Make side effects explicit and localized
- Easier to reason about and test when separated
- Command-Query Separation principle
- Avoid functions that modify state AND return a value

### Minimize Parameter Complexity
- Avoid out-parameters and reference returns when possible
- Prefer returning structured results over modifying caller state
- Clear input/output contracts improve readability
- 0 is ideal, 1 is good, 2 is acceptable, 3 is the maximum
- Don't use flag/boolean arguments
- If several arguments are cohesive, wrap them into an object/class

### Reuse Existing Abstractions
- Leverage proven utilities rather than reimplementing logic
- Build new helpers on top of existing ones
- Reduces bugs and maintenance burden
- Creates consistency across codebase

### Use Appropriate Visibility
- Default to private/internal scope
- Make public only when truly needed for reuse
- Reduces coupling and surface area
- Clarifies intended usage patterns

### Maintain Backward Compatibility
- Don't break existing APIs unnecessarily
- Create new focused methods alongside existing ones
- Allows gradual migration and reduces impact
- Preserves existing client code

### Use Clear, Consistent Naming
- Names should indicate purpose and scope
- Follow patterns (e.g., `Get*`, `Find*`, `Save*`, `On*`)
- Avoid ambiguous or overly generic names
- Good names reduce need for comments

### Design for Testability
- Small, focused functions are easier to test independently
- Separate concerns enable unit testing of each layer
- Reduce mocking complexity by limiting dependencies
- Testable code is usually better designed code

### Make Dependencies Explicit
- Function signatures should show what the function needs
- Avoid hidden dependencies or global state access
- Clear dependencies make code flow easier to follow
- Easier to refactor and reason about interactions

### Prefer Composition Over Monolithic Implementation
- Build complex behavior from simple, composable pieces
- Each piece should be independently valuable
- Enables reuse and flexibility
- Reduces cognitive load when reading code

### Stay Up-to-Date and Verify SDKs and APIs
- Make 100% sure you're using the latest version of any SDK
- Triple-check the documentation for all APIs before writing anything
- Prevents integration issues and ensures compatibility
- Easier to refactor and reason about interactions

### The Stepdown Rule
- Arrange functions so each is followed by calls at the next abstraction level, enabling top‑down reading.
- Write code like sequential "TO" paragraphs: each describes the current level and references the next level down.
- Readers should descend one abstraction level at a time as they read down the function list.
- Each function naturally leads to more detailed implementations below it, creating a narrative flow from high-level intent to low-level details.
