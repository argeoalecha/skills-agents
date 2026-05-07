#!/bin/bash
# Pre-deployment validation checklist for TripIntell features

set -e

echo "🚀 Pre-Deployment Validation Checklist"
echo "======================================="

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

# 1. Environment variables
echo -e "\n${YELLOW}1. Checking required environment variables...${NC}"
REQUIRED_VARS=(
    "NEXT_PUBLIC_SUPABASE_URL"
    "NEXT_PUBLIC_SUPABASE_ANON_KEY"
    "SUPABASE_SERVICE_ROLE_KEY"
    "ANTHROPIC_API_KEY"
    "NEXT_PUBLIC_GOOGLE_MAPS_API_KEY"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}  ✗ Missing: $var${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}  ✓ Found: $var${NC}"
    fi
done

# 2. Build check
echo -e "\n${YELLOW}2. Validating production build...${NC}"
if pnpm build; then
    echo -e "${GREEN}✓ Production build successful${NC}"
else
    echo -e "${RED}✗ Production build failed${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 3. Check for console.log statements
echo -e "\n${YELLOW}3. Scanning for debug statements...${NC}"
if grep -r "console\.log" src/ --exclude-dir=node_modules --exclude-dir=.next | grep -v "// DEBUG:"; then
    echo -e "${YELLOW}⚠️  Found console.log statements (consider removing for production)${NC}"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✓ No debug console.log statements found${NC}"
fi

# 4. Check for TODO comments in critical files
echo -e "\n${YELLOW}4. Checking for unresolved TODOs...${NC}"
TODO_COUNT=$(grep -r "TODO\|FIXME" src/ --exclude-dir=node_modules --exclude-dir=.next | wc -l | tr -d ' ')
if [ "$TODO_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $TODO_COUNT TODO/FIXME comments${NC}"
    echo -e "   Review if any are blocking issues"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✓ No TODO/FIXME comments found${NC}"
fi

# 5. Check for hardcoded API keys or secrets
echo -e "\n${YELLOW}5. Scanning for potential secrets...${NC}"
SECRETS_FOUND=0
if grep -r "sk-\|pk_\|AKIA" src/ --exclude-dir=node_modules --exclude-dir=.next 2>/dev/null; then
    echo -e "${RED}✗ Potential secrets found in source code!${NC}"
    ERRORS=$((ERRORS + 1))
    SECRETS_FOUND=1
fi

if [ $SECRETS_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ No obvious secrets detected${NC}"
fi

# 6. Check git status
echo -e "\n${YELLOW}6. Checking git status...${NC}"
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  Uncommitted changes detected${NC}"
    git status --short
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✓ Working directory clean${NC}"
fi

# 7. Check if on main branch
echo -e "\n${YELLOW}7. Checking git branch...${NC}"
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${YELLOW}⚠️  Not on main branch (current: $CURRENT_BRANCH)${NC}"
    echo -e "   Consider merging to main before deploying"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✓ On main branch${NC}"
fi

# 8. Check package.json version
echo -e "\n${YELLOW}8. Checking package version...${NC}"
if [ -f "package.json" ]; then
    VERSION=$(grep -o '"version": "[^"]*' package.json | cut -d'"' -f4)
    echo -e "${GREEN}✓ Current version: $VERSION${NC}"
else
    echo -e "${RED}✗ package.json not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Final summary
echo -e "\n======================================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Ready for deployment.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  $WARNINGS warning(s) - review before deploying${NC}"
    exit 0
else
    echo -e "${RED}❌ $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo -e "${RED}Fix errors before deploying!${NC}"
    exit 1
fi
