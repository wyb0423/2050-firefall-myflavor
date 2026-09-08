"""Read-only source/probe checks; this does not emulate the Victoria 3 engine.

python3 tests/check_north_america_preflight.py --game-root GAME \
    --firefall-root FIREFALL --techres-root TECHRES
"""

import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "tests/probes/north_america"
TOKEN = re.compile(r'\s+|#[^\n]*|"(?:\\.|[^"\\])*"|[{}=]|[^\s{}=#"]+')
EXPECTED_TAGS = {
    "ZZZCONNECTICUT", "ZZZDELAWARECITY", "ZZZFLORIDACITY", "ZZZGEORGIA",
    "ZZZIDAHOWOOD", "ZZZILLINOISCITY", "ZZZILLINOISWOOD", "ZZZIOWAFARM",
    "ZZZNEWHAMPSHIREWOOD", "ZZZNEWMEXICOFARM", "ZZZNEWYORKFARM",
    "ZZZOREGONMINE", "ZZZSOUTHCAROLINAMINE", "ZZZWISCONSINMINE",
    "ZZZWYOMINGMINE",
}


def parse(text):
    """Nested token lists for data blocks, preserving duplicate assignments."""
    result = []
    stack = [result]
    pos = 0
    for match in TOKEN.finditer(text.lstrip("\ufeff")):
        assert match.start() == pos, f"Invalid token at {pos}"
        pos = match.end()
        token = match[0]
        if token.isspace() or token.startswith("#"):
            continue
        if token == "{":
            block = []
            stack[-1].append(block)
            stack.append(block)
        elif token == "}":
            assert len(stack) > 1, "Unexpected closing brace"
            stack.pop()
        else:
            stack[-1].append(token)
    assert pos == len(text.lstrip("\ufeff")), "Unparsed trailing text"
    assert len(stack) == 1, "Unclosed block"
    return result


def fields(block, name):
    return [block[i + 2] for i in range(len(block) - 2)
            if block[i] == name and block[i + 1] == "="]


def one(block, name):
    values = fields(block, name)
    assert len(values) == 1, f"Expected exactly one {name}, got {len(values)}"
    return values[0]


def definitions(path, *, allow_duplicates=False):
    block = parse(path.read_text(encoding="utf-8-sig"))
    result = {}
    for i in range(len(block) - 2):
        if isinstance(block[i], str) and block[i + 1] == "=" and isinstance(block[i + 2], list):
            key = block[i]
            assert allow_duplicates or key not in result, f"Duplicate definition {key} in {path.name}"
            result[key] = block[i + 2]
    return result


def check_design_references(roots):
    """Check source declarations, not a simulation of engine database merging."""
    spec = (ROOT / "docs/superpowers/specs/2026-09-08-north-america-usa-flavor-design.md").read_text()
    industry = spec.split("#### 6.3.1", 1)[1].split("### 6.4", 1)[0]
    research = spec.split("#### 6.5.1", 1)[1].split("### 6.6", 1)[0]
    required = {
        "buildings": set(re.findall(r"\bbuilding_[a-z0-9_]+\b", industry + research)) | {"building_university"},
        "production_methods": set(re.findall(r"\bpm_[a-z0-9_]+\b", research)),
        "production_method_groups": set(re.findall(r"\bpmg_[a-z0-9_]+\b", research)),
        "technology/technologies": {
            "bessemer_process", "mechanical_tools", "atmospheric_engine",
            "semiconductor", "integrated_circuits", "computer",
            "automated_industrial_robots", "parallel_computing_architecture",
            "wireless_broadband_networks",
        },
        "modifier_type_definitions": {
            "building_group_bg_infrastructure_throughput_add",
            "building_university_throughput_add", "building_goods_input_mult",
            "country_expenses_add", "state_education_access_add",
            "building_group_bg_manufacturing_throughput_add",
        },
    }
    runtime = "\n".join(path.read_text() for path in (ROOT / "common").glob("*/ffpa_north_american*.txt"))
    required["buildings"].update(re.findall(r"(?:is_building_type|can_construct_building|has_building)\s*=\s*(building_[a-z0-9_]+)", runtime))
    modifiers = (ROOT / "common/static_modifiers/ffpa_north_american_modifiers.txt").read_text()
    required["modifier_type_definitions"].update(re.findall(r"^\s*((?:building|state|country)_[a-z0-9_]+)\s*=", modifiers, re.M))
    # An INJECT by itself is not evidence that its target exists.
    for category, keys in required.items():
        declared = set()
        for root in roots:
            for path in sorted((root / "common" / category).glob("*.txt")):
                # Upstream contains duplicate declarations unrelated to our
                # whitelist. This pass checks existence only; probe checks
                # above remain strict about duplicate definitions.
                for name in definitions(path, allow_duplicates=True):
                    operation, separator, key = name.partition(":")
                    if not separator:
                        declared.add(name)
                    elif operation == "REPLACE_OR_CREATE":
                        declared.add(key)
        missing = keys - declared
        assert not missing, f"Undeclared {category} design references: {sorted(missing)}"
        print(f"PASS: {len(keys)} {category} design/runtime references have source declarations.")


def main():
    # Exercise the structural reader against the cases needed by the source audit.
    sample = parse('tag-with-dash = { text = "{#}" # ignored }\n x = { a b } x = { c } }')
    assert len(fields(one(sample, "tag-with-dash"), "x")) == 2
    for invalid in ('x = {', 'x = }', 'x = "unterminated'):
        try:
            parse(invalid)
        except AssertionError:
            pass
        else:
            raise AssertionError(f"Accepted malformed source: {invalid}")

    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("game-root", "firefall-root", "techres-root"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    for path, expected in ((args.firefall_root, "alter_time_2050_fire_falls"),
                           (args.techres_root, "tech.res")):
        meta = json.loads((path / ".metadata/metadata.json").read_text())
        assert meta["id"] == expected, f"Wrong upstream: {path}"

    countries = definitions(args.firefall_root / "common/country_definitions/tff_countries.txt")
    formables = definitions(args.firefall_root / "common/country_formation/tff_major_formables.txt")
    states = one(formables["USA"], "states")
    assert len(states) == len(set(states)) == 50
    assert one(formables["USA"], "required_states_fraction") == "0.7"
    assert "STATE_PUERTO_RICO" in states
    assert not {"STATE_ALASKA", "STATE_HAWAII"}.intersection(states)
    mainland = set(states) - {"STATE_PUERTO_RICO"}
    history = one(parse((args.firefall_root / "common/history/states/00_states.txt").read_text()), "STATES")
    holders = set()
    for state in mainland:
        for part in fields(one(history, "s:" + state), "create_state"):
            holders.add(one(part, "country").removeprefix("c:"))
    eligible = {tag for tag in holders if one(countries[tag], "country_type") != "decentralized"}
    assert eligible == EXPECTED_TAGS, f"Cohort drift: {eligible ^ EXPECTED_TAGS}"

    illinois = one(history, "s:STATE_ILLINOIS")
    source = [part for part in fields(illinois, "create_state")
              if one(part, "country") == "c:ZZZILLINOISWOOD"]
    assert len(source) == 1
    provinces = one(source[0], "owned_provinces")
    assert set(provinces) == {"xAD5337", "x2FBF72", "x34036E", "x50C040", "x543986"}

    native = (args.game_root / "common/scripted_effects/00_chris_scripted_effects.txt").read_text()
    assert "set_owner_of_provinces" in native and "p:$PROVINCE$.state.state_region" in native
    probe_effects = definitions(PROBE / "common/scripted_effects/ffpa_na_probe.txt")
    assert set(probe_effects) == {f"ffpa_na_probe_{step}_v1" for step in ("setup", "partial", "merge", "report")}
    for path in (PROBE / "common").rglob("*.txt"):
        definitions(path)
    effects_text = (PROBE / "common/scripted_effects/ffpa_na_probe.txt").read_text()
    assert all(f"p:{province}.state.owner" in effects_text for province in provinces)
    assert "set_owner_of_provinces" not in (PROBE / "common/on_actions/ffpa_na_probe.txt").read_text()
    assert not (PROBE / "common/decisions").exists(), "Probe must not add a normal-game entry point"
    json.loads((PROBE / ".metadata/metadata.json").read_text())
    localizations = []
    for language in ("english", "simp_chinese"):
        path = PROBE / f"localization/{language}/ffpa_na_probe_l_{language}.yml"
        data = path.read_bytes()
        assert data.startswith(b"\xef\xbb\xbf")
        text = data.decode("utf-8-sig")
        assert text.startswith(f"l_{language}:\n")
        localizations.append(set(re.findall(r'^ ([\w.-]+):', text, re.M)))
    assert localizations[0] == localizations[1] == {"ffpa_na_probe_engineering_v1", "ffpa_na_probe_engineering_v1_desc"}
    check_design_references((args.game_root, args.techres_root, args.firefall_root, ROOT))
    print("PASS: 50 formation regions, 49 mainland regions, 15 eligible starting tags.")
    print("PASS: five probe provinces, native transfer precedent, probe structure and localization.")
    print("NOT TESTED: final engine database merging, engine parsing, split/merge inheritance, save reload, AI choice and gameplay balance.")


if __name__ == "__main__":
    main()
