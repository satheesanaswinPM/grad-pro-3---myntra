PROJECT: Myntra Wishlist-to-Purchase AI Discovery Engine

ROLE
Act as a Senior Product Manager + AI/Data Product Engineer working with the Growth Team at Myntra.

CONTEXT
Myntra users frequently add fashion products to their wishlist, signaling explicit interest, but many wishlisted products are never purchased within 30 days.

BUSINESS GOAL
Increase the percentage of users who purchase at least one item from their wishlist within 30 days of adding it.

CONSTRAINT
We CANNOT use monetary incentives such as discounts, coupons, cashback, price reductions, or promotional offers as the primary solution.

IMPORTANT
The underlying user problem is UNKNOWN.

Do not assume that price, sizing, reviews, discounts, or any other commonly suggested reason is the problem.

Your job is to DISCOVER the problem from the scraped user feedback.

DATA
I already have scraped real-world user feedback data.

Use the existing scraped dataset as the primary source of truth.

The dataset may contain feedback from sources such as:
- App Store reviews
- Google Play reviews
- Reddit
- YouTube
- Social media
- Fashion/shopping communities
- Product reviews
- Product Q&A
- Other publicly available discussions

FIRST STEP — INSPECT THE DATA

Before building the analysis pipeline:

1. Inspect all available files and folders.
2. Identify file formats and schemas.
3. Identify available fields such as:
   - review/comment text
   - source
   - date
   - rating
   - product/category
   - username/user ID if available
   - URL
   - metadata
4. Determine the total number of records.
5. Check for duplicates.
6. Check for missing values.
7. Identify language distribution.
8. Identify source distribution.
9. Understand whether the dataset contains Myntra-specific feedback, broader online-fashion-shopping feedback, or both.
10. Create a data-quality report before analysis.

Do NOT overwrite the original scraped data.

CORE RESEARCH QUESTION

Why do users wishlist fashion products but fail to purchase them within 30 days?

The engine should investigate the entire journey:

DISCOVERY → PRODUCT CONSIDERATION → WISHLIST → EVALUATION → PURCHASE / ABANDONMENT

KEY QUESTIONS TO ANSWER

1. WISHLIST INTENT

Why do users add products to wishlists?

Classify intent into evidence-based categories such as:
- Strong purchase intent
- Future purchase
- Bookmarking
- Comparison
- Price watching
- Occasion-based purchase
- Uncertain intent
- Inspiration
- Other emerging intents

Do not force feedback into predefined categories if the data suggests different behaviors.

2. PURCHASE BARRIERS

Identify what prevents users from purchasing after wishlisting.

Investigate, but do not assume:
- Fit uncertainty
- Size uncertainty
- Product quality concerns
- Fabric/material uncertainty
- Styling uncertainty
- Occasion uncertainty
- Reviews/social proof
- Return/exchange concerns
- Delivery concerns
- Availability
- Price/value perception
- Comparing alternatives
- Decision fatigue
- Lack of urgency
- Changing preferences
- Trust
- Need for external validation
- Other emerging barriers

3. POST-WISHLIST UNCERTAINTY

What questions remain unanswered after a user decides they like a product?

For example:
- Will this fit me?
- How will this look on someone like me?
- Is the quality worth it?
- How does the actual product compare with the images?
- What should I pair it with?
- Is this appropriate for my occasion?
- Is there a better alternative?

Again, these are hypotheses to investigate, NOT predetermined conclusions.

4. EXTERNAL RESEARCH

Identify whether users leave Myntra or other shopping platforms to seek information elsewhere.

Look for references to:
- Google
- Reddit
- YouTube
- Instagram
- Other shopping platforms
- Influencers
- Fashion communities
- Friends/family/social validation

Determine WHY they seek external information.

5. COMPARISON BEHAVIOR

Understand how users compare shortlisted products.

Identify:
- What attributes they compare
- Which alternatives they consider
- What information influences the final decision
- Why one product wins over another

6. USER SEGMENTS

Identify meaningful behavioral segments from the data.

Possible examples:
- High-intent shoppers
- Browsers/bookmarkers
- Comparison shoppers
- Fit-conscious shoppers
- Occasion-driven shoppers
- Social-validation seekers
- Quality-conscious shoppers
- Trend/inspiration seekers

Do NOT create arbitrary segments.

Segments must be supported by recurring behavioral patterns in the data.

7. CATEGORY DIFFERENCES

Where the data allows, compare barriers across fashion categories such as:
- Clothing
- Footwear
- Accessories
- Beauty
- Ethnic wear
- Western wear
- Sportswear
- Other available categories

Identify whether wishlist behavior and purchase barriers differ by category.

AI ANALYSIS PIPELINE

Build an end-to-end pipeline:

RAW DATA
↓
Data Cleaning & Normalization
↓
Deduplication
↓
Language Detection
↓
Relevant Feedback Filtering
↓
Intent Detection
↓
Problem/Barrier Extraction
↓
Need & Uncertainty Extraction
↓
Behavior/Context Extraction
↓
User Segment Identification
↓
Theme Clustering
↓
Evidence Aggregation
↓
Quantification
↓
Opportunity Scoring
↓
Prioritized Opportunity Areas

IMPORTANT:
The engine must go beyond:
- Sentiment analysis
- Keyword counting
- Simple topic extraction
- Generic review summarization

Every insight should connect:

USER EVIDENCE
→ BEHAVIOR
→ PROBLEM
→ NEED
→ PURCHASE BARRIER
→ POTENTIAL BUSINESS IMPACT

EVIDENCE SYSTEM

Every generated insight should retain traceability to the underlying feedback.

For each insight store:

- Insight ID
- Problem statement
- User need
- Barrier
- Intent
- Segment
- Category
- Source
- Evidence text/snippet
- Record ID
- Date
- Frequency
- Percentage of relevant feedback
- Confidence score
- AI interpretation
- Hypothesis vs observed evidence

Do not present AI-generated assumptions as facts.

QUANTIFICATION

For every major barrier/theme, calculate where possible:

- Number of mentions
- Percentage of relevant feedback
- Number of unique records
- Source distribution
- Category distribution
- Segment distribution
- Co-occurring barriers
- Trend over time

Make it clear when a number is based on:
- All scraped data
- Relevant data
- A specific source
- A specific segment

OPPORTUNITY PRIORITIZATION

Create a transparent opportunity-scoring framework.

Suggested dimensions:

1. Frequency
2. Severity
3. Relationship to purchase hesitation
4. Number of users/segments affected
5. Evidence confidence

Create an Opportunity Score that ranks the identified problems.

Do not artificially assign high scores.

If the available data cannot establish a relationship with actual purchase behavior, clearly label it as a hypothesis rather than claiming causality.

OUTPUT

Build an interactive Product Discovery Dashboard / Research Console.

The dashboard should contain:

1. EXECUTIVE SUMMARY
- Dataset size
- Sources
- Key findings
- Top opportunity areas

2. WISHLIST INTENT
- Why users wishlist
- Intent distribution
- Intent by source/category

3. PURCHASE BARRIERS
- Ranked barriers
- Frequency
- Severity
- Evidence
- Source distribution

4. USER SEGMENTS
- Segment definitions
- Segment size
- Key behaviors
- Dominant barriers
- Needs

5. UNCERTAINTY MAP
Show what users still need to know after wishlisting.

6. CUSTOMER JOURNEY
Visualize:
Discovery → Consideration → Wishlist → Evaluation → Purchase/Abandonment

7. COMPARISON BEHAVIOR
- What users compare
- Why they compare
- Decision criteria

8. EXTERNAL RESEARCH
Show what information users seek outside Myntra.

9. CATEGORY ANALYSIS
Compare barriers and behaviors across categories.

10. OPPORTUNITY MATRIX
Plot opportunities based on:
- Frequency
- Severity/impact
- Evidence confidence

11. EVIDENCE EXPLORER
Allow the PM to click an insight and see the actual supporting user feedback.

12. RESEARCH HYPOTHESES
Convert the strongest opportunities into testable hypotheses for primary user research.

DESIGN PRINCIPLE

The dashboard should feel like a PRODUCT DISCOVERY / RESEARCH INTELLIGENCE TOOL, not a generic analytics dashboard.

Prioritize:
- Clear insights
- Evidence traceability
- Useful visualizations
- Easy comparison
- Decision-making

Avoid unnecessary charts.

FINAL QUESTION THE SYSTEM MUST HELP ANSWER

"Who adds products to their wishlist, why do they do it, what prevents them from purchasing, what information are they missing, which barriers matter most, and which opportunity should the Myntra Growth Team investigate first to improve 30-day wishlist-to-purchase conversion?"

TECHNICAL REQUIREMENTS

- Use the existing scraped data.
- Preserve the raw dataset.
- Create processed/analysis datasets separately.
- Make the pipeline reproducible.
- Keep API keys/secrets in environment variables.
- Handle large datasets efficiently.
- Cache expensive AI operations where possible.
- Avoid repeatedly sending identical feedback to an LLM.
- Log AI processing failures.
- Allow the dataset to be refreshed/reprocessed later.
- Make the analysis modular so new data sources can be added.
- Clearly separate data processing, AI analysis, scoring, and dashboard layers.

DO NOT BUILD THE FINAL PRODUCT SOLUTION YET.

The purpose of Part 1 is DISCOVERY.

First identify and prioritize the underlying user problems using evidence from the scraped data.

Only after the strongest opportunity areas are established should the project move toward solution ideation, validation, and experimentation.
