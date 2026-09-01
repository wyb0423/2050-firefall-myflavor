# Greek Nationalism Country Identity Repair Design

## 1. Status and scope

This design was approved on 2026-09-01. It repairs the `je_greek_nationalism`
chain for the fixed Victoria 3 1.13.*, Firefall 0.1.1, and Tech & Res 1.6 load
environment used by FFPA.

The change is intentionally limited to the Greek Nationalism entry, its
Eastern Roman proposal, the GRE -> BYZ formation handoff, and the terminal
success/failure event delivery. A repository-wide audit of optional `c:TAG ?=`
identity checks is required separately; it must not be implemented as an
unreviewed mechanical replacement in this change.

## 2. Observed failure

Firefall starts without an active GRE country. The Firefall city-state
`ZZZEASTERNTHRACEWOOD` (Midye Woods / 米迪耶林镇) has both Turkish and Greek
primary cultures and its capital is in `STATE_EASTERN_THRACE`. That state is
part of vanilla `geographic_region_megali_greece`.

The vanilla journal therefore behaves as authored when FFPA is absent:

```text
Greek primary culture
AND capital in geographic_region_megali_greece
-> je_greek_nationalism is available
```

FFPA intentionally narrows the journal to a formed GRE, but currently expresses
that restriction with `c:GRE ?= this`. The optional scope operator does not
provide a strict current-country identity assertion when the specified country
does not exist. Because GRE is initially only a country definition and formable,
the guard can be skipped instead of rejecting Midye Woods and comparable
Firefall countries.

The ambitious completion branch repeats the problem with `c:BYZ ?= this`.
Before BYZ exists, an unrelated country can appear to satisfy the requirement
that it has already become BYZ.

## 3. Desired behavior

The repaired state machine is:

```text
Non-GRE country
  -> journal is hidden and cannot activate

GRE
  -> journal becomes available
  -> greece.1 chooses one of three routes
       -> limited Greek program: remains GRE
       -> Megali Idea: remains GRE
       -> Eastern Roman title: GRE receives ffpa_flavor.8,
          selects the ambitious route, and may form BYZ

GRE, limited/Megali route
  -> success or failure resolves the journal
  -> greece.4 or greece.5 is shown explicitly

BYZ, ambitious route inherited from GRE
  -> active journal survives the tag change
  -> success or failure resolves the journal
  -> greece.4 or greece.5 is shown explicitly

Any other active legacy instance
  -> invalidates without success/failure rewards
  -> temporary journal state is cleaned
```

Only GRE may create a new journal instance. BYZ is not an independent activation
candidate; it may only continue an instance inherited from GRE after the
ambitious route was selected.

## 4. Identity rule

Country identity gates in this chain will use the current country definition:

```text
country_definition = cd:GRE
country_definition = cd:BYZ
```

This form is valid in the current 1.13 country trigger scope and does not depend
on whether a global `c:GRE` or `c:BYZ` country object existed before evaluation.
Optional `?=` scoping remains valid for optional effects and nullable saved
scopes, but it must not be used as the sole exclusive identity assertion for a
Firefall formable tag.

## 5. Journal lifecycle changes

`common/journal_entries/zzzz_ffpa_greek_nationalism_override.txt` remains the
single complete replacement of vanilla `je_greek_nationalism`.

The replacement will make the following lifecycle rules explicit:

1. `is_shown_in_lobby`, `is_shown_when_inactive`, and `possible` require
   `country_definition = cd:GRE`.
2. `transferable = yes` documents that the active instance must survive the
   GRE -> BYZ formation handoff.
3. The active instance is valid only when the current country is either:
   - GRE; or
   - BYZ with `embrace_ambitious_agenda_var`.
4. The limited and Megali completion branches require GRE.
5. The ambitious completion branch requires BYZ.
6. The original failure conditions apply only while the instance is in one of
   the two valid identity states. A legacy instance on another country must be
   invalidated rather than treated as a Greek national failure.
7. `on_complete` calls `greece.4` with `popup = yes`.
8. `on_fail` calls `greece.5` with `popup = yes`.
9. `on_invalid` removes only temporary Greek Nationalism state:
   - `greek_homeland_states_owned_var`;
   - `byzantium_states_owned_var`;
   - `no_megali_idea_var`;
   - `embrace_megali_idea_var`;
   - `embrace_ambitious_agenda_var`;
   - `byzantium_event_fired`.

`ionian_islands_requirement_var` is not removed. Existing saves have no marker
that proves which system created it, and its default value is harmless once the
strict identity gates prevent the wrong country from consuming this chain.

The implementation must not fire `greece.5` from `on_invalid`: Midye Woods did
not fail a Greek national project; it received a journal it was never eligible
to own under FFPA's design.

## 6. Adjacent chain guards

The following connected entry points receive the same strict identity rule:

| File/object | Required identity |
|---|---|
| `events/ffpa_eastern_mediterranean_events.txt` / `ffpa_flavor.8` | GRE |
| `common/decisions/ffpa_eastern_mediterranean_decisions.txt` / `ffpa_request_eastern_roman_title` | GRE |
| `common/country_formation/ffpa_byzantium.txt` / BYZ `potential` and identity tooltip | GRE |
| `events/ffpa_formation_overrides.txt` / `formation.3` | BYZ |

The proposal event may convert `embrace_megali_idea_var` into
`embrace_ambitious_agenda_var`, but only for GRE. The BYZ formation definition
continues to require monarchy and the ambitious route variable. `formation.3`
continues to grant only the existing FFPA Justinianic claim whitelist.

## 7. Old-save behavior

### 7.1 Active invalid instances

An active journal on Midye Woods or any country other than valid GRE/BYZ is
removed through the journal's own `invalid` path. This avoids a global country
scan and respects the Eastern Mediterranean on_action boundary.

Runtime counters and route variables are cleaned. Already granted claims are
not removed because the old implementation did not attach provenance markers;
removing them could destroy a legitimate claim supplied by Firefall, another
event, or a war settlement.

### 7.2 Already completed invalid instances

An already completed invalid instance has no active journal to invalidate. Its
state is inert once the adjacent decision, proposal, and formation guards are
strict. No Greek success event or reward is retroactively granted to the wrong
country.

The old chain has no durable marker that distinguishes “terminal event was
resolved” from “journal set its completion flag but the event was not
presented.” This change therefore does not guess, globally clear completion
flags, or reopen already terminated journals. If a concrete save later needs
that separate recovery, it requires an explicit, player-confirmed migration
rather than a silent heuristic.

### 7.3 Valid GRE and BYZ instances

An active GRE instance remains active. An active BYZ instance remains valid only
when it carries `embrace_ambitious_agenda_var`. Its counters, route variable,
and completion progress are preserved.

## 8. Event delivery

The static chain already contains `on_complete -> greece.4` and
`on_fail -> greece.5`; neither vanilla terminal event has a country trigger.
The repair does not copy those large upstream events.

FFPA will make the two terminal journal events explicit popups:

```text
on_complete -> greece.4, popup = yes
on_fail     -> greece.5, popup = yes
```

This retains the original event effects and minimizes the upstream override
surface. The separate approved historical-text redesign may override their
localization, but it is not part of this logic repair.

## 9. Files in scope

Runtime changes are limited to:

- `common/journal_entries/zzzz_ffpa_greek_nationalism_override.txt`;
- `events/ffpa_eastern_mediterranean_events.txt`, only `ffpa_flavor.8`;
- `common/decisions/ffpa_eastern_mediterranean_decisions.txt`, only the Eastern
  Roman title recovery decision;
- `common/country_formation/ffpa_byzantium.txt`;
- `events/ffpa_formation_overrides.txt`, only the identity trigger.

No metadata, README, country definition, state history, culture, modifier,
reward value, journal threshold, or localization change is required by this
repair.

## 10. Validation matrix

### 10.1 Static validation

- Compare the final `je_greek_nationalism` definition against vanilla 1.13.11,
  Firefall 0.1.1, Tech & Res 1.6, and FFPA in load order.
- Confirm all chain identity checks use `country_definition = cd:GRE/BYZ`.
- Confirm no connected entry point retains a sole `c:GRE ?=` or `c:BYZ ?=`
  exclusive identity guard.
- Confirm the override retains all upstream thresholds, route variables,
  counters, rewards, and outcome descriptions except the already intentional
  plausible-formables difference.
- Check braces, strings, duplicate top-level keys, `git diff --check`, and the
  unchanged metadata JSON.

### 10.2 New-game runtime scenarios

1. Start as `ZZZEASTERNTHRACEWOOD`: the journal and recovery decision are absent.
2. Check another Greek-primary Firefall successor in the Megali region: the
   journal is absent.
3. Form GRE: the journal becomes available and `greece.1` appears.
4. Complete the limited route as GRE: `greece.4` appears once.
5. Complete the Megali route as GRE: `greece.4` appears once.
6. Fail either GRE route: `greece.5` appears once.
7. Select the ambitious route, form BYZ, and verify the journal survives.
8. Complete the ambitious route as BYZ: `greece.4` appears once.
9. Fail the ambitious route as BYZ: `greece.5` appears once.
10. Verify a non-GRE country cannot use the proposal decision or form BYZ through
    this chain.

### 10.3 Old-save runtime scenarios

1. Load a save where Midye Woods has an active journal: it invalidates without
   Greek success/failure rewards and clears temporary state.
2. Load a save with an active GRE journal: it remains active.
3. Load a save with an active ambitious BYZ journal: it remains active.
4. Load a save where a non-GRE predecessor has already terminated the journal:
   no Greek terminal reward is retroactively granted and connected recovery
   entries remain unavailable to that country.
5. Verify claims present before the update and active-instance invalidation
   remain present.

## 11. Broader follow-up

The repository currently contains many `c:GRE ?=`, `c:BYZ ?=`, and `c:TUR ?=`
expressions. Some are correct optional scoping; others appear to be exclusive
identity gates for Firefall formables and may share this defect. A follow-up
audit must classify each occurrence by scope and intent before replacement,
with priority given to on_actions, journal visibility/invalidity, decisions,
and event triggers. This design does not authorize a blind repository-wide
rewrite.
