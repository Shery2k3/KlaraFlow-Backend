## Merge optional and required docs models into one
### Research about denormalization with JSONB for fields inside docs template
## Collapse to_do_items and onboarding_tasks into a single template_tasks (blueprint) and session_tasks (instance)
## Refactor to feature based scaling
## Fix the request model in /invite employee API
# Match and sync the update and use upserts for template / settings update, i.e. only send "updated data" from FE and upsert that in BE or send whole from FE and parse and look for changes in BE
## Reference User tables' FK id inside Onboarding_Sessions instead of creating one there
## Use employment lifecycle state in Users table with enums: ("Invited", "Onboarded", "Terminated", "Resigned", "Inactive (catch all)" )
## Use system access flags (purely technical): "in_enabled", "can_login"

# Make the vars name in Onboarding Module consistent