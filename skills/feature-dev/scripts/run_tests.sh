#!/bin/bash
# Run comprehensive test suite for TripIntell features

set -e

echo "🧪 Running Feature Development Test Suite..."
echo "=============================================="

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in a Next.js project
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: package.json not found${NC}"
    exit 1
fi

# Type checking
echo -e "\n${YELLOW}1. TypeScript Type Checking...${NC}"
if pnpm type-check; then
    echo -e "${GREEN}✓ Type checking passed${NC}"
else
    echo -e "${RED}✗ Type checking failed${NC}"
    exit 1
fi

# Linting
echo -e "\n${YELLOW}2. Running ESLint...${NC}"
if pnpm lint; then
    echo -e "${GREEN}✓ Linting passed${NC}"
else
    echo -e "${RED}✗ Linting failed${NC}"
    exit 1
fi

# Unit tests
echo -e "\n${YELLOW}3. Running Unit Tests (Vitest)...${NC}"
if pnpm test; then
    echo -e "${GREEN}✓ Unit tests passed${NC}"
else
    echo -e "${RED}✗ Unit tests failed${NC}"
    exit 1
fi

# E2E tests (optional - skip if not configured)
if grep -q "test:e2e" package.json; then
    echo -e "\n${YELLOW}4. Running E2E Tests (Playwright)...${NC}"
    if pnpm test:e2e; then
        echo -e "${GREEN}✓ E2E tests passed${NC}"
    else
        echo -e "${RED}✗ E2E tests failed${NC}"
        exit 1
    fi
else
    echo -e "\n${YELLOW}4. E2E Tests: Skipped (not configured)${NC}"
fi

echo -e "\n${GREEN}=============================================="
echo -e "✅ All tests passed successfully!${NC}"
