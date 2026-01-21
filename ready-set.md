# Ready, Set, ExFrame!

**Your Tour of the Expertise Framework**

---

## Welcome to ExFrame!

You're looking at the landing page of ExFrame - a domain-agnostic AI-powered knowledge management system. This isn't just another chatbot. ExFrame uses **pure semantic search** to find patterns based on *meaning*, not keywords.

Let's take a quick tour of what you're seeing and what you can do right away.

---

## The Landing Page

### Header

At the top, you'll see:
- **ExFrame logo** with the tagline "Expertise Framework"
- **Universe selector** - Shows your current knowledge universe (default: "default")
- **Domain selector** - This is the main switch! Pick what expertise you need
- **Pattern count** - Shows how many patterns are loaded in the current domain

### Domain Selector - The Heart of ExFrame

The domain dropdown is your primary tool. Each domain is a self-contained universe of expertise:

| Domain | Expertise | Patterns |
|--------|-----------|----------|
| **cooking** | Culinary arts, recipes, techniques | 32 |
| **first_aid** | Emergency medical response | 3 |
| **python** | Python programming features | 6 |
| **llm_consciousness** | LLM failure modes, monitoring | 12 |
| **binary_symmetry** | Binary transformations, algorithms | 20 |
| **poetry_domain** | Poetic forms, literary analysis | 13 |
| **diy** | Building, flooring, tools | 10 |
| **exframe_methods** | Methodology, design patterns | 26 |

### Navigation Tabs

The main tabs you see are:

- **Query** - Ask questions and get answers (this is the main event!)
- **Patterns** - Browse all patterns in the current domain
- **Traces** - See query history and how responses were generated
- **Domains** - Manage domains (create new ones, update descriptions)
- **Surveyor** - Explore cross-domain relationships
- **Universes** - Switch between knowledge universes
- **Diagnostics** - System health and embedding coverage

---

## What You Can Do Right Now

### 1. Ask a Question (The Simple Path)

1. **Select a domain** from the dropdown
2. **Type your question** in the text box
3. **Press Enter** (or click "Submit Query")
4. **Get an answer!**

That's it. ExFrame will:
- Search for semantically similar patterns
- Return the most relevant knowledge
- Show you which patterns matched
- Display confidence scores

### 2. Enable Trace (See How It Works)

Check the **"Enable Trace"** box before submitting. You'll see:
- Query processing time
- Which patterns were matched
- Semantic similarity scores
- Specialist used
- Processing method

### 3. Browse Patterns

Click the **Patterns** tab to see all expertise in the current domain. Each pattern shows:
- Name and description
- Pattern type (how_to, procedure, knowledge, etc.)
- Health status (green = good)
- Times accessed
- Creation date

---

## The Simple Query/Response Cycle

Let's walk through a typical interaction:

### Example 1: In-Domain Query

**You:** Select domain "cooking" and ask:
> "How do I cook chicken breast?"

**ExFrame:**
1. Converts your query to a 384-dimensional semantic embedding
2. Searches all cooking patterns for similar meanings
3. Finds relevant patterns (e.g., "Chicken Temperature Guide", "Cooking Methods")
4. Returns a comprehensive answer
5. Shows: "Specialist: cooking", "Confidence: 85%"

**Response:** A detailed answer with:
- Safe internal temperatures
- Cooking methods comparison
- Common mistakes to avoid

### Example 2: The "Extend with AI" Feature

**You:** Ask something obscure:
> "What's the best way to cook a pineapple upside down cake on a campfire?"

**ExFrame:**
1. Searches for patterns... finds few/weak matches
2. Shows: **"3 patterns found"** with **"Confidence: 35%"**
3. Displays a purple button: **"Extend Search with AI"**

**You:** Click "Extend Search with AI"

**ExFrame:**
1. Calls the LLM to search external sources
2. Generates a comprehensive answer from web research
3. Shows: **"AI-Generated"** badge
4. Displays: **"Accept as New Pattern"** button

**Now you choose:**
- **Click "Accept"** → Save this as a new pattern (permanently expands the domain!)
- **Do nothing** → Answer is discarded after you navigate away

---

## AI Extension: With vs Without Storing Expertise

The "Extend with AI" feature gives you a choice:

### Without Storing (One-Shot)
- Get an answer from external sources
- Use it once
- Navigate away → knowledge is gone
- Good for: research, one-off questions, testing

### With Storing (Growing the Domain)
- Click "Accept as New Pattern"
- ExFrame saves the answer as a new pattern
- **Auto-generates semantic embedding** → immediately searchable
- Future queries benefit from this new knowledge
- Good for: reusable expertise, building up domains

---

## Humorous Off-Domain Queries (The "Domain Specialist" Effect)

One of the funniest things about ExFrame is asking questions *outside* a domain's expertise. The system will try its best with the patterns it has, often with hilarious results.

### In the "first_aid" Domain, Ask:

> "How do I bake a chocolate cake?"

**Possible Answer:**
> "While I don't have specific information about baking chocolate cakes, I can tell you that **burns are a common kitchen injury**. If you burn yourself while baking: **1. Cool the burn under running water for 20 minutes. 2. Cover with a sterile dressing. 3. Take pain relief if needed.** Please seek medical attention if the burn is severe or covers a large area."

> "What's the meaning of life?"

**Possible Answer:**
> "Life is a condition that distinguishes organisms from inorganic matter. **If life stops, see the 'Death' pattern for information on termination of life functions.** Remember: if someone is unconscious, check their ABCs (Airway, Breathing, Circulation) and call emergency services immediately."

> "How do I fix a leaky faucet?"

**Possible Answer:**
> "I don't have specific information about plumbing repairs. However, **water damage can lead to mold growth and respiratory issues.** If you have a leak: **1. Turn off the water supply. 2. Contain the water with buckets or towels. 3. Ensure electrical safety if water is near outlets.** Consider consulting a professional plumber."

### In the "cooking" Domain, Ask:

> "My code has a bug, what do I do?"

**Possible Answer:**
> "Debugging code is similar to troubleshooting a recipe that won't work! **Here's a cooking-inspired approach:**

> **1. Check your ingredients** - Verify all your variables and inputs are correct
> **2. Follow the recipe** - Step through your code line by line
> **3. Taste test** - Use print statements or a debugger to inspect values
> **4. Adjust seasoning** - Make small changes and test each one

> **Remember:** Just as you can't unbake a cake, sometimes you need to start fresh with a clean function!"

### In the "python" Domain, Ask:

> "How do I comfort a sad friend?"

**Possible Answer:**
> "While I don't have a pattern for emotional support, I can offer a **Python-inspired approach:**

> ```python
> def comfort_friend(friend):
>     if friend.is_sad():
>         return listen(friend) + validate(feelings) + support()
>
> # Key functions:
> # - listen(): Active listening without judgment
> # - validate(): Acknowledge their feelings are real
> # - support(): Offer help and presence
> ```

> **Note:** This is metaphorical code. For actual emotional support, consider professional counseling resources."

---

## Getting Started - Your First 5 Minutes

1. **Open ExFrame** at http://localhost:3000

2. **Pick a domain** you're curious about (try "cooking" or "python")

3. **Ask a simple question:**
   - Cooking: "How do I know when chicken is done?"
   - Python: "What's a list comprehension?"
   - First Aid: "What do I do for a small cut?"

4. **Look at the response:**
   - Check the confidence score
   - Note which patterns were used
   - Try enabling trace to see the internals

5. **Experiment with off-domain questions:**
   - Ask cooking domain about coding
   - Ask first aid about philosophy
   - See how the domain specialist stays in character!

---

## Tips and Tricks

| Tip | Description |
|-----|-------------|
| **Start with example queries** | Click in the query box for domain-specific examples |
| **Check the Patterns tab** | See what expertise is available before asking |
| **Enable Trace** | Understand how ExFrame finds answers |
| **Use "Extend with AI"** | When confidence is low, get external knowledge |
| **Accept good patterns** | Build up domains for future use |
| **Browse Traces** | See your query history and what worked |

---

## Next Steps

Once you've tried the basics:

1. **Create a new domain** - Use the Domains tab to add your own expertise area
2. **Add patterns manually** - Use the Patterns tab → "Create Pattern" button
3. **Explore Surveyor** - See how patterns relate across domains
4. **Check Diagnostics** - View system health and embedding coverage

---

## The Philosophy

ExFrame isn't just a Q&A system. It's a **knowledge capture and reuse framework**. Every time you accept an AI-generated pattern, you're:
- Capturing expertise permanently
- Making it available to all future queries
- Building an ai persona that emerges from the pattern store
- Building a corpus that improves with use
- Creating a domain-specific knowledge base

The goal is simple: **Never solve the same problem twice.**

---

**Ready? Set? Query!**

---

*Having fun? Share your funniest off-domain query results!*

I recommend using claude code with this app to really take it for a ride.  