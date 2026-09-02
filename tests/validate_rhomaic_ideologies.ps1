$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$ideologies = Get-Content -LiteralPath "$root\common\ideologies\ffpa_eastern_mediterranean_ideologies.txt" -Raw
$effects = Get-Content -LiteralPath "$root\common\scripted_effects\ffpa_eastern_mediterranean_effects.txt" -Raw
$liberalism = [regex]::Match($ideologies, '(?s)ideology_ffpa_rhomaic_liberalism = \{.*?(?=ideology_ffpa_rhomaic_civic_universalism = \{)').Value
$universalism = $ideologies.Substring($ideologies.IndexOf('ideology_ffpa_rhomaic_civic_universalism = {'))

if (-not $liberalism -or $liberalism.Contains('lawgroup_citizenship')) { throw 'Rhomaic Liberalism must exist without a citizenship law group.' }
foreach ($group in 'lawgroup_policing', 'lawgroup_internal_security', 'lawgroup_free_speech', 'lawgroup_rights_of_women') {
	if (-not $liberalism.Contains($group)) { throw "Rhomaic Liberalism is missing $group." }
}
if (-not $universalism.Contains('law_multicultural = strongly_approve')) { throw 'Rhomaic Civic Universalism must strongly approve Multiculturalism.' }
foreach ($operation in 'remove_ideology = ideology_liberal', 'remove_ideology = ideology_liberal_modern', 'add_ideology = ideology_ffpa_rhomaic_liberalism', 'set_variable = ffpa_byz_rhomaic_civic_universalism_v2') {
	if ($effects -notmatch "(?m)^\s*$operation\r?$") { throw "Migration is missing: $operation." }
}
foreach ($file in 'english\ffpa_l_english.yml', 'simp_chinese\ffpa_l_simp_chinese.yml') {
	if (-not (Get-Content -LiteralPath "$root\localization\$file" -Raw).Contains('ideology_ffpa_rhomaic_liberalism_desc:')) { throw "$file is missing Rhomaic Liberalism localization." }
}

'Rhomaic ideology validation passed.'
