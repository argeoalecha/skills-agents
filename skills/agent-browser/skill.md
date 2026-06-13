---
name: agent-browser
description: Browser automation CLI for AI agents. Use when the user needs to interact with websites, including navigating pages, filling forms, clicking buttons, taking screenshots, extracting data, testing web apps, or automating any browser task. Triggers include requests to "open a website", "fill out a form", "click a button", "take a screenshot", "scrape data from a page", "test this web app", "login to a site", "automate browser actions", or any task requiring programmatic web interaction.
allowed-tools: Bash(npx agent-browser:*), Bash(agent-browser:*)
---

# Browser Automation with agent-browser

## Core Workflow

Every browser automation follows this pattern:

1. **Navigate**: `agent-browser open <url>`
2. **Snapshot**: `agent-browser snapshot -i` (get element refs like `@e1`, `@e2`)
3. **Interact**: Use refs to click, fill, select
4. **Re-snapshot**: After navigation or DOM changes, get fresh refs

```bash
agent-browser open https://example.com/form
agent-browser snapshot -i
# Output shows:  @e1 input[type=email], @e2 input[type=password], @e3 button[type=submit]
agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "mypassword"
agent-browser click @e3
agent-browser snapshot -i   # re-snapshot after page changes
```

---

## Commands Reference

### Navigation
```bash
agent-browser open <url>        # Navigate to URL
agent-browser back              # Go back in history
agent-browser forward           # Go forward in history
agent-browser reload            # Reload current page
```

### Snapshots
```bash
agent-browser snapshot -i       # Interactive snapshot — assigns @e1, @e2... refs to all visible elements
agent-browser snapshot          # Non-interactive snapshot — page text + structure, no refs
```

`snapshot -i` output format:
```
@e1  input[name="email"]  placeholder="Email address"
@e2  input[name="password"]  placeholder="Password"
@e3  button[type="submit"]  text="Sign in"
@e4  a[href="/signup"]  text="Create account"
```

Always re-snapshot after:
- Page navigation
- Modal/dialog opens or closes
- Dynamic content loads (React state update, AJAX response)

### Interaction
```bash
agent-browser click @e3                     # Click element by ref
agent-browser fill @e1 "text to type"       # Clear and type into input
agent-browser select @e5 "Option Value"     # Select dropdown option by visible text
agent-browser check @e6                     # Check a checkbox
agent-browser uncheck @e6                   # Uncheck a checkbox
```

### Screenshots
```bash
agent-browser screenshot                              # Screenshot to ~/.agent-browser/tmp/ (default)
agent-browser screenshot ./path/to/file.png           # Screenshot to a specific file
agent-browser screenshot --full ./path/to/file.png    # Full-page screenshot to a specific file
agent-browser screenshot --screenshot-dir ./dir/      # Override output directory for this call
```

Set `AGENT_BROWSER_SCREENSHOT_DIR=./dir/` in the environment to route all screenshots to a fixed directory without repeating the flag on every call.

### Waiting
```bash
agent-browser wait --text "Success"         # Wait for text to appear
agent-browser wait --selector ".modal"      # Wait for element selector
agent-browser wait --url "/dashboard"       # Wait for URL change
agent-browser wait --ms 2000               # Wait fixed milliseconds
```

### Scrolling
```bash
agent-browser scroll down 500              # Scroll down 500px
agent-browser scroll up 500               # Scroll up
agent-browser scroll bottom               # Scroll to page bottom
agent-browser scroll top                  # Scroll to top
```

### Data Extraction
```bash
agent-browser snapshot                    # Get page text — pipe output for parsing
agent-browser snapshot -i                 # Get structured element data with refs
```

---

## Common Patterns

### Login flow
```bash
agent-browser open https://app.example.com/login
agent-browser snapshot -i
agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --url "/dashboard"
agent-browser snapshot -i
```

### Form submission with validation check
```bash
agent-browser open https://example.com/contact
agent-browser snapshot -i
agent-browser fill @e1 "John Doe"
agent-browser fill @e2 "invalid-email"   # intentionally bad
agent-browser click @e5                  # submit
agent-browser snapshot                   # check for validation error
# look for error text in output
agent-browser fill @e2 "john@doe.com"    # fix email
agent-browser click @e5
agent-browser wait --text "Thank you"
```

### Scraping data
```bash
agent-browser open https://example.com/products
agent-browser scroll bottom             # load all items
agent-browser snapshot                  # capture full page text
# Parse snapshot output for product names, prices, etc.
```

### Multi-step navigation
```bash
agent-browser open https://app.example.com
agent-browser snapshot -i
agent-browser click @e4               # click nav item
agent-browser wait --url "/settings"
agent-browser snapshot -i
agent-browser fill @e2 "new value"
agent-browser click @e8               # save button
agent-browser wait --text "Saved"
agent-browser screenshot              # confirm success
```

---

## Rules

- Always call `snapshot -i` before interacting with a new page or after navigation
- After any click that might trigger navigation, call `wait` then `snapshot -i`
- Element refs (`@e1`, `@e2`) are only valid for the current snapshot — re-snapshot after DOM changes
- If an element isn't found in snapshot output, scroll down and re-snapshot
- Take screenshots after completing key steps to confirm success
- When testing, take a screenshot of both success and error states

---

## Error Handling

| Issue | Fix |
|---|---|
| Element ref not found in snapshot | Scroll to that section and re-snapshot |
| Click not responding | Check if element is inside a shadow DOM; try scrolling to it first |
| Navigation didn't happen | Use `wait --url` or `wait --text` instead of assuming immediate redirect |
| Form submission silently fails | Check snapshot after submit for error messages |
| Page loading slowly | Use `wait --text` for a landmark string rather than `wait --ms` |
