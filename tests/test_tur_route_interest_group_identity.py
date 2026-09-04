from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    traits = (ROOT / "common/interest_group_traits/ffpa_eastern_mediterranean_interest_group_traits.txt").read_text()
    effects = (ROOT / "common/scripted_effects/ffpa_turkish_flavor_effects.txt").read_text()
    events = (ROOT / "events/ffpa_turkish_flavor_events.txt").read_text()

    for name, text in (("traits", traits), ("effects", effects), ("events", events)):
        assert text.count("{") == text.count("}"), f"unbalanced braces: {name}"

    trait_specs = {
        "ig_trait_ffpa_tur_guardianship_intervention": ("max_approval = unhappy", "country_law_enactment_speed_mult = -0.10"),
        "ig_trait_ffpa_tur_civilian_command": ("min_approval = happy", "unit_defense_mult = 0.05"),
        "ig_trait_ffpa_tur_republican_public_instruction": ("min_approval = loyal", "state_education_access_add = 0.05"),
        "ig_trait_ffpa_tur_contractual_obstruction": ("max_approval = unhappy", "state_capitalists_investment_pool_efficiency_mult = -0.05"),
        "ig_trait_ffpa_tur_reconstruction_contracts": ("min_approval = happy", "state_construction_mult = 0.05"),
        "ig_trait_ffpa_tur_national_technical_service": ("min_approval = loyal", "country_production_tech_research_speed_mult = 0.05"),
    }
    for trait_id, required in trait_specs.items():
        assert traits.count(f"{trait_id} = {{") == 1, trait_id
        for fragment in required:
            assert fragment in traits, f"{trait_id}: {fragment}"

    required_effect_fragments = (
        "ffpa_apply_tur_route_interest_group_identity_v1 = {",
        "ffpa_tur_has_republican_state_project_v1 = yes",
        "has_variable = ffpa_tur_republic_settlement_choice_v1",
        "ffpa_tur_republic_interest_group_identity_v1",
        "ffpa_tur_has_directorate_state_project_v1 = yes",
        "has_variable = ffpa_tur_directorate_settlement_choice_v1",
        "ffpa_tur_directorate_interest_group_identity_v1",
    )
    for fragment in required_effect_fragments:
        assert fragment in effects, fragment
    assert events.count("after = { ffpa_apply_tur_route_interest_group_identity_v1 = yes }") == 2

    localization_keys = (
        "ffpa_ig_tur_republican_general_staff",
        "ffpa_ig_tur_ankara_civic_society",
        "ffpa_ig_tur_national_reconstruction_combines",
        "ffpa_ig_tur_national_technical_service_corps",
        *(key for trait_id in trait_specs for key in (trait_id, f"{trait_id}_desc")),
    )
    localization_sets = []
    for path in (
        ROOT / "localization/english/ffpa_turkish_flavor_l_english.yml",
        ROOT / "localization/simp_chinese/ffpa_turkish_flavor_l_simp_chinese.yml",
    ):
        text = path.read_text(encoding="utf-8-sig")
        localization_sets.append({line.split(":", 1)[0].strip() for line in text.splitlines()[1:] if line.startswith(" ") and ":" in line})
        for key in localization_keys:
            assert text.count(f"\n {key}:") == 1, f"{path.name}: {key}"
    assert localization_sets[0] == localization_sets[1], "English and Chinese localization key sets differ"

    print("TUR route interest-group identity checks passed")


if __name__ == "__main__":
    main()
