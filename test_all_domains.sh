#!/bin/bash
# Test all domains with Wiseman endpoint

echo "Testing Wiseman endpoint for all domains..."
echo "=========================================="

domains="cooking diy gardening poetry_domain first_aid python llm_consciousness binary_symmetry psycho exframe"

for domain in $domains; do
  echo ""
  echo "Testing: $domain"

  # Get a sample query based on domain
  case $domain in
    cooking)
      query="How do I bake chicken breast?"
      ;;
    diy)
      query="How do I build a simple shelf?"
      ;;
    gardening)
      query="When should I plant tomatoes?"
      ;;
    poetry_domain)
      query="Write a haiku about nature"
      ;;
    first_aid)
      query="What should I do for a minor burn?"
      ;;
    python)
      query="How do I read a file in Python?"
      ;;
    llm_consciousness)
      query="What is machine learning?"
      ;;
    binary_symmetry)
      query="What is the XOR operation?"
      ;;
    psycho)
      query="What is cognitive behavioral therapy?"
      ;;
    exframe)
      query="What is ExFrame?"
      ;;
    *)
      query="Tell me about this domain"
      ;;
  esac

  # Test the domain
  response=$(curl -s -X POST http://localhost:3000/api/query/wiseman \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$query\", \"domain\": \"$domain\"}")

  # Check if response is valid JSON
  if echo "$response" | python3 -m json.tool >/dev/null 2>&1; then
    # Extract key fields
    answer=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('response', 'NO RESPONSE')[:100])")
    sources=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('sources_used', []))")
    status="✅ OK"
  else
    answer="ERROR: Invalid JSON"
    sources="[]"
    status="❌ FAILED"
  fi

  echo "  Status: $status"
  echo "  Sources: $sources"
  echo "  Answer: $answer..."
  echo "  ---"
done

echo ""
echo "=========================================="
echo "Testing complete!"
