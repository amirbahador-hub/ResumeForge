---
description: Interactively edit the master profile YAML.
---

You are running the `/update-profile` command for ResumeForge.

The master profile lives at `profile/profile.yaml`. It is the only source of truth for every tailored resume. Help the user edit it without losing structure.

## Flow

1. **Read** `profile/profile.yaml`.
2. **Ask** what the user wants to do. Offer these options if $ARGUMENTS doesn't already say:
   - Add a new role (experience)
   - Edit an existing role
   - Add/remove a skill
   - Add a project
   - Update contact info
   - Add a one-off achievement, talk, certification, or extra
   - Free-form ("I want to change X")
3. **Probe for the details** specific to the chosen path. For a new role, you need: company, title, dates, location, context, and 4–8 highlight bullets. For a new project: name, description, stack, optional URL. For a new skill: which category it belongs in.
4. **Show the proposed diff** (just the changed YAML section, not the whole file). Ask for confirmation.
5. **Apply** the change with the Edit tool. Preserve indentation and the comment header at the top of the file.
6. **Validate** by re-reading the file. If YAML is broken, fix it before reporting done.
7. **Confirm** with a one-line summary of what changed.

## Rules
- Don't invent details. If the user is vague ("I led a project"), ask for the specifics that would survive an interview.
- Don't reorder unrelated sections. Edits should be local.
- Don't strip the comment header at the top of `profile.yaml`.
- If the user wants to remove something, double-check before deleting. Truthful removals are fine; accidental ones aren't.
- Bullets in `experience[].highlights` should be the same shape as existing entries (objects with `area` and `detail`, or just `detail`).

$ARGUMENTS
