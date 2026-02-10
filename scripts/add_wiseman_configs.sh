#!/bin/bash
# Add Wiseman config to domain.json files

# Poet config - pure generation, high temperature
add_poet_config() {
  local domain=$1
  local file="/home/peter/development/eeframe/universes/MINE/domains/$domain/domain.json"

  if [ ! -f "$file" ]; then
    echo "Skipping $domain (no domain.json)"
    return
  fi

  # Check if wiseman section already exists
  if grep -q '"wiseman"' "$file"; then
    echo "Skipping $domain (wiseman section exists)"
    return
  fi

  # Add wiseman config before closing brace
  temp_file=$(mktemp)
  awk '
  /}$/ && !added {
    print "  ,\"wiseman\": {"
    print "    \"use_void\": true,"
    print "    \"use_library\": false,"
    print "    \"use_internet\": false,"
    print "    \"temperature\": 0.9,"
    print "    \"show_thinking\": false,"
    print "    \"max_tokens\": 2000"
    print "  }"
    added = 1
  }
  {print}
  ' "$file" > "$temp_file"
  mv "$temp_file" "$file"
  echo "Added poet config to $domain"
}

# Researcher config - internet search, show thinking
add_researcher_config() {
  local domain=$1
  local file="/home/peter/development/eeframe/universes/MINE/domains/$domain/domain.json"

  if [ ! -f "$file" ]; then
    echo "Skipping $domain (no domain.json)"
    return
  fi

  # Check if wiseman section already exists
  if grep -q '"wiseman"' "$file"; then
    echo "Skipping $domain (wiseman section exists)"
    return
  fi

  # Add wiseman config before closing brace
  temp_file=$(mktemp)
  awk '
  /}$/ && !added {
    print "  ,\"wiseman\": {"
    print "    \"use_void\": false,"
    print "    \"use_library\": true,"
    print "    \"use_internet\": false,"
    print "    \"temperature\": 0.5,"
    print "    \"show_thinking\": true,"
    print "    \"max_tokens\": 3000,"
    print "    \"max_documents\": 10"
    print "  }"
    added = 1
  }
  {print}
  ' "$file" > "$temp_file"
  mv "$temp_file" "$file"
  echo "Added researcher config to $domain (library mode, internet TODO)"
}

# Librarian config - library search, show thinking
add_librarian_config() {
  local domain=$1
  local file="/home/peter/development/eeframe/universes/MINE/domains/$domain/domain.json"

  if [ ! -f "$file" ]; then
    echo "Skipping $domain (no domain.json)"
    return
  fi

  # Check if wiseman section already exists
  if grep -q '"wiseman"' "$file"; then
    echo "Skipping $domain (wiseman section exists)"
    return
  fi

  # Add wiseman config before closing brace
  temp_file=$(mktemp)
  awk '
  /}$/ && !added {
    print "  ,\"wiseman\": {"
    print "    \"use_void\": false,"
    print "    \"use_library\": true,"
    print "    \"use_internet\": false,"
    print "    \"temperature\": 0.5,"
    print "    \"show_thinking\": true,"
    print "    \"max_tokens\": 2000,"
    print "    \"max_documents\": 10"
    print "  }"
    added = 1
  }
  {print}
  ' "$file" > "$temp_file"
  mv "$temp_file" "$file"
  echo "Added librarian config to $domain"
}

echo "Adding Wiseman configs to domains..."
echo "======================================"

# Poet domains
echo ""
echo "Poet domains:"
add_poet_config "poetry_domain"

# Researcher domains
echo ""
echo "Researcher domains:"
add_researcher_config "cooking"
add_researcher_config "diy"
add_researcher_config "gardening"
add_researcher_config "first_aid"
add_researcher_config "python"
add_researcher_config "llm_consciousness"
add_researcher_config "binary_symmetry"
add_researcher_config "psycho"

# Librarian domains
echo ""
echo "Librarian domains:"
# exframe already has it

echo ""
echo "======================================"
echo "Done! Check domains for wiseman sections."
