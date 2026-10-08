<?php
/*
 * SmartCheck - native PHP port.
 * Faithfully reproduces the Python reference (sf_smartcheck.core.check): identical
 * rule IDs, confidences, span strings, ordering and citation-coverage logic.
 * Verified against ports/conformance/expected.json. No dependencies.
 *
 *   php smartcheck.php [vectors.json]                 # batch -> {"results":[...]}
 *   php smartcheck.php --answer "text" --sources "s"  # single verdict
 */

const NUM    = '/\b\d{3,}\b|\b\d+(?:\.\d+)?\s?%|\b\d+(?:\.\d+)?\s*(?:hundred|thousand|million|billion|trillion)\b/i';
const CONTRA = '/\balways\b.*\bnever\b|\bnever\b.*\balways\b/i';
const HEDGE  = '/\b(?:as of my knowledge|i think|maybe|probably)\b/i';

function check(string $answer, string $sources = ''): array {
    $issues = [];
    $hasSrc = $sources !== '';
    if (preg_match(NUM, $answer) && !$hasSrc)
        $issues[] = ['type' => 'CHECK-UNSOURCED-NUMBER', 'confidence' => 0.6, 'span' => 'numeric claim with no source'];
    if (preg_match(CONTRA, $answer))
        $issues[] = ['type' => 'CHECK-CONTRADICTION', 'confidence' => 0.7, 'span' => 'internal contradiction'];
    if (preg_match(HEDGE, $answer))
        $issues[] = ['type' => 'CHECK-HEDGED', 'confidence' => 0.5, 'span' => 'hedged/uncertain claim stated as fact'];
    if (strpos($answer, '[contains seeded error]') !== false)
        $issues[] = ['type' => 'CHECK-SEEDED', 'confidence' => 0.9, 'span' => 'known seeded error (demo)'];
    $coverage = $hasSrc ? 1.0 : (preg_match('/\d/', $answer) ? 0.0 : 0.5);
    return ['passed' => count($issues) === 0, 'issues' => $issues, 'citation_coverage' => $coverage];
}

$argv1 = $argv[1] ?? null;
if ($argv1 === '--answer') {
    $ans = $argv[2] ?? '';
    $src = '';
    for ($i = 1; $i < count($argv) - 1; $i++) if ($argv[$i] === '--sources') $src = $argv[$i + 1];
    echo json_encode(check($ans, $src)), "\n";
    exit(0);
}
$vpath = $argv1 ?? __DIR__ . '/../conformance/vectors.json';
$v = json_decode(file_get_contents($vpath), true);
$results = [];
foreach ($v['cases'] as $c) {
    $r = check($c['answer'] ?? '', $c['sources'] ?? '');
    $results[] = array_merge(['name' => $c['name']], $r);
}
echo json_encode(['policy_version' => $v['policy_version'] ?? null, 'results' => $results],
                 JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES), "\n";
