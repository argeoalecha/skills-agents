#!/bin/bash
# Validate Supabase database migrations before deployment

set -e

echo "🗄️  Validating Database Migrations..."
echo "======================================"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check for Supabase migrations directory
if [ ! -d "supabase/migrations" ]; then
    echo -e "${YELLOW}⚠️  No migrations directory found (supabase/migrations)${NC}"
    echo "This is OK if no database changes were made."
    exit 0
fi

# Count migrations
MIGRATION_COUNT=$(find supabase/migrations -name "*.sql" | wc -l | tr -d ' ')
echo -e "${YELLOW}Found $MIGRATION_COUNT migration file(s)${NC}\n"

if [ "$MIGRATION_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✓ No new migrations to validate${NC}"
    exit 0
fi

# Check migration naming convention
echo -e "${YELLOW}1. Checking migration naming convention...${NC}"
INVALID_NAMES=0
for file in supabase/migrations/*.sql; do
    filename=$(basename "$file")
    # Should match: YYYYMMDDHHMMSS_description.sql
    if ! echo "$filename" | grep -qE '^[0-9]{14}_[a-z_]+\.sql$'; then
        echo -e "${RED}  ✗ Invalid name: $filename${NC}"
        echo -e "    Expected format: YYYYMMDDHHMMSS_description.sql"
        INVALID_NAMES=1
    fi
done

if [ $INVALID_NAMES -eq 0 ]; then
    echo -e "${GREEN}✓ All migration files follow naming convention${NC}"
else
    echo -e "${RED}✗ Some migrations have invalid names${NC}"
    exit 1
fi

# Check for dangerous operations
echo -e "\n${YELLOW}2. Scanning for dangerous operations...${NC}"
DANGEROUS_OPS=0

for file in supabase/migrations/*.sql; do
    filename=$(basename "$file")

    # Check for DROP commands without IF EXISTS
    if grep -qi "DROP TABLE\|DROP COLUMN" "$file" && ! grep -qi "IF EXISTS" "$file"; then
        echo -e "${RED}  ⚠️  $filename contains DROP without IF EXISTS${NC}"
        DANGEROUS_OPS=1
    fi

    # Check for CASCADE deletions
    if grep -qi "CASCADE" "$file"; then
        echo -e "${YELLOW}  ⚠️  $filename contains CASCADE operation${NC}"
        echo -e "     Review carefully to ensure data safety"
    fi

    # Check for missing RLS policies on new tables
    if grep -qi "CREATE TABLE" "$file" && ! grep -qi "ALTER TABLE.*ENABLE ROW LEVEL SECURITY" "$file"; then
        echo -e "${YELLOW}  ⚠️  $filename creates table without RLS${NC}"
        echo -e "     Consider adding RLS policies for security"
    fi
done

if [ $DANGEROUS_OPS -eq 0 ]; then
    echo -e "${GREEN}✓ No dangerous operations detected${NC}"
else
    echo -e "${YELLOW}⚠️  Review warnings above carefully${NC}"
fi

# Check for transaction safety
echo -e "\n${YELLOW}3. Checking transaction safety...${NC}"
for file in supabase/migrations/*.sql; do
    filename=$(basename "$file")

    # Check if migration uses transactions
    if grep -qi "BEGIN\|START TRANSACTION" "$file"; then
        if ! grep -qi "COMMIT" "$file"; then
            echo -e "${RED}  ✗ $filename: BEGIN without COMMIT${NC}"
            exit 1
        fi
        echo -e "${GREEN}  ✓ $filename uses transactions${NC}"
    fi
done

echo -e "${GREEN}✓ Transaction safety checks passed${NC}"

# Final summary
echo -e "\n${GREEN}======================================"
echo -e "✅ Migration validation complete!${NC}\n"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Review migration files in supabase/migrations/"
echo -e "  2. Test migrations locally: ${YELLOW}pnpm db:migrate${NC}"
echo -e "  3. Verify schema changes: ${YELLOW}pnpm db:types${NC}"
