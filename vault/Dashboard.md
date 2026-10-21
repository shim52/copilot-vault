---
type: dashboard
updated: {{TODAY}}
---

> Last refreshed: **{{TODAY}}** (initial — the daily pass refreshes this every run)
> 👥 Team board → [[Team Tasks]]

## 🤝 Today's meetings
*Events on the brief date, time-ordered. Links only — the meeting note holds the agenda.*
-

## ✅ My to-dos & blocked-on-me
*One source `- [ ]` → one line. Each bullet mirrors a single live checkbox and carries its `→ [[source]]` trail.*
-

## 👥 Raise with team
-

## 🧭 Raise with managers
-

## 📡 Org signals to act on
-

## ❓ Open questions (for manager/team)
→ Full list in [[Open Questions]].

---

### 🔄 How this stays current
Maintained by the daily vault pass (and manually on request: "refresh the dashboard"). The layout follows my priority spine — **meeting links → my to-dos → raise-with-people/managers → org signals** first, reference sections next. Every line is a mirror of a `- [ ]` somewhere else in the vault; an item leaves only when I tick its source.

If you install the **Dataview** community plugin, this block gives a fully automatic roll-up of every open checkbox:

<!--
```dataview
TASK
WHERE !completed AND !contains(file.path, "99-Templates") AND file.name != "Dashboard"
GROUP BY file.link
```
-->
