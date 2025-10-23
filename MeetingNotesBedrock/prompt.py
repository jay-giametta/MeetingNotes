PROMPT_TEMPLATE = """Do not include information outside of what I asked for. Do not add meta-commentary like "These are concise notes about your meeting."

You are creating meeting notes for {role} and their team members. These conversations are typically with {typical_participants}. Build your results consistently so you can rebuild very similar results on future iterations.

## {date} in MM/DD/YYYY - {context}
Include the actual date from the transcript if mentioned.

### Attendees
CRITICAL: ONLY list people who actually SPOKE during the meeting. Verify each person contributed to the discussion. Do not include people mentioned in passing, on distribution lists, referenced but not present, or mentioned as "not here today." When in doubt, exclude rather than include.

### Notes
**CRITICAL GROUPING PRINCIPLE:** Before writing, mentally map all related information to primary topic areas. A topic should contain ALL relevant information about that subject, even if discussed at different times in the meeting. Consolidate rather than fragment.

**Topic Selection Strategy:**
- Identify 5-8 major themes that capture the meeting's substance
- Each topic should represent a complete area of discussion (e.g., "Database Infrastructure & Storage" not separate "Database" and "Storage" sections)
- Group by business/technical domain, not by when things were mentioned
- Combine related technical components (compute + storage for same tier)
- Merge planning and current-state for same subject area

**Topic Consolidation Examples:**
- Combine "Current Environment" + "Environment Strategy" + "Environment Details" → "Environment Architecture & Consolidation"
- Combine "Database Sizing" + "Storage Planning" + "Storage Growth" → "Database & Storage Infrastructure"
- Combine "Server Types" + "Instance Selection" + "Sizing" → "Compute Infrastructure Planning"

Organize entries by main topic categories. Format the category names as bold Markdown text. Under each bold category, use regular (non-bold) markdown list items starting with a hyphen.

**CRITICAL - Use TAB characters for sub-bullet indentation:**
- Level 1: Start with `- ` (hyphen + space, no indentation)
- Level 2: Start with ONE TAB CHARACTER then `- ` (one tab, then hyphen + space)
- Level 3: Start with TWO TAB CHARACTERS then `- ` (two tabs, then hyphen + space)

You MUST use actual TAB characters (the \t escape character, not spaces) for indentation. This is critical for proper formatting.

**WITHIN EACH TOPIC, USE THIS STRUCTURE:**
1. Current state / baseline information first
2. Constraints, requirements, or decisions next
3. Planning considerations and options
4. Open questions or items needing investigation last

This creates a logical flow within each consolidated topic area.

**WHEN TO USE SUB-BULLETS (you should have many sub-bullets):**
Create sub-bullets when information:
- Provides specific details, examples, or clarification about the parent bullet
- Shows components, steps, or parts of a larger item
- Lists multiple related specifics under a general statement
- Explains implications, reasons, or context for the parent point
- Shows timeline phases or conditional scenarios

Each bullet must:
- Be 15 words or less
- Provide only useful details AWS needs to remember for each line-item (not just summarized info) - these are for historical reference
- Be very relevant with enough context so the reader understands why you included it
- Provide sufficient context for future reference
- Answer: What changed? What was decided? What impacts the project?
- Pass the test: "Would this matter to a team manager reviewing this 6 months from now?"
- Focus on information that impacts {focus_areas}
- Prioritize: {priorities}

**PHRASING PRECISION - CRITICAL:**
- Use cautious language when details are incomplete or tentative
- Distinguish clearly between: decisions made vs. options discussed, requirements vs. preferences, commitments vs. possibilities
- Use qualifiers appropriately: "considering", "exploring", "may", "potential", "discussed", "mentioned", "interested in"
- Reserve definitive language ("will", "requires", "decided") only for explicit commitments
- When specifics are missing (timelines, quantities, exact requirements), acknowledge the gap: "timeline TBD", "scope to be defined", "pending approval"
- Avoid overstating certainty - if something was "mentioned briefly" don't frame it as a "key requirement"
- Default to understating rather than overstating when ambiguous

Exclude:
- Routine process discussions, basic explanations, obvious details
- Meeting logistics, basic definitions, status updates without implications
- Vague/ambiguous information or filler content - the reader should never wonder why you are including the information
- AWS advice or suggestions unless confirmed as actual requirements by the other party

Maintain consistent terminology. Mark uncertain or ambiguous information with [?]. Identify connections to previous discussions when evident. Use context to understand the conversation correctly despite potential transcription errors - only include information you're highly confident in. Keep only information that influences decisions, reveals requirements, or shows progress/blockers.

### Way Ahead
CRITICAL: Only include actual next steps/action items mentioned that affect {action_items_scope}. Do not make up any next steps - use only steps verbally agreed to in the meeting. Do not include non-tactical/vague entries. Include specific owners and deadlines if mentioned. Remove this section if no next steps or way ahead are discussed.

**For action items, clearly distinguish:**
- Confirmed commitments: "{example_commitment}"
- Tentative plans: "{example_tentative}"
- Conditional actions: "{example_conditional}"

---
FINAL CLEANUP:
- Remove additional information that doesn't fit in Attendees, Notes, or Way Ahead sections
- Remove duplicate speaker names (double check for similar names/titles)
- Remove additional information on how well you answered or if you did
- Remove section headers and placeholders if there is no actual content
- Remove non-meeting content or meta-information from your results
- Remove vague speaker descriptions like "Speaker 0"
- Remove template text like "MEETING_TYPE", "ORGANIZATION_1", etc.
- IMPORTANT FINAL REVIEW: Remove any notes that are just "what happened" vs "what matters"
- FINAL PHRASING CHECK: Verify no statements are more definitive than the source material warrants
- VERIFY SUB-BULLETS: Confirm you created sub-bullets using actual TAB characters (the \t character, not spaces) for indentation to show relationships between general points and their specific details
- VERIFY GROUPING: Confirm you consolidated related information into comprehensive topic sections rather than fragmenting and/or being redundant across multiple categories

Meeting Notes to analyze:
{transcript}
"""