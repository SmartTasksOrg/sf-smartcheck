// SmartCheck - native Go port.
// Faithfully reproduces the Python reference (sf_smartcheck.core.check): identical
// rule IDs, confidences, span strings, ordering and citation-coverage logic.
// Verified against ports/conformance/expected.json. Standard library only.
//
//   go run main.go [vectors.json]                 # batch -> {"results":[...]}
//   go run main.go --answer "text" --sources "s"  # single verdict
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

var (
	numRe    = regexp.MustCompile(`(?i)\b\d{3,}\b|\b\d+(?:\.\d+)?\s?%|\b\d+(?:\.\d+)?\s*(?:hundred|thousand|million|billion|trillion)\b`)
	contraRe = regexp.MustCompile(`(?i)\balways\b.*\bnever\b|\bnever\b.*\balways\b`)
	hedgeRe  = regexp.MustCompile(`(?i)\b(?:as of my knowledge|i think|maybe|probably)\b`)
	digitRe  = regexp.MustCompile(`\d`)
)

type Issue struct {
	Type       string  `json:"type"`
	Confidence float64 `json:"confidence"`
	Span       string  `json:"span"`
}

type Verdict struct {
	Name             string  `json:"name,omitempty"`
	Passed           bool    `json:"passed"`
	Issues           []Issue `json:"issues"`
	CitationCoverage float64 `json:"citation_coverage"`
}

func check(answer, sources string) Verdict {
	issues := []Issue{}
	hasSrc := sources != ""
	if numRe.MatchString(answer) && !hasSrc {
		issues = append(issues, Issue{"CHECK-UNSOURCED-NUMBER", 0.6, "numeric claim with no source"})
	}
	if contraRe.MatchString(answer) {
		issues = append(issues, Issue{"CHECK-CONTRADICTION", 0.7, "internal contradiction"})
	}
	if hedgeRe.MatchString(answer) {
		issues = append(issues, Issue{"CHECK-HEDGED", 0.5, "hedged/uncertain claim stated as fact"})
	}
	if strings.Contains(answer, "[contains seeded error]") {
		issues = append(issues, Issue{"CHECK-SEEDED", 0.9, "known seeded error (demo)"})
	}
	cov := 0.5
	if hasSrc {
		cov = 1.0
	} else if digitRe.MatchString(answer) {
		cov = 0.0
	}
	return Verdict{Passed: len(issues) == 0, Issues: issues, CitationCoverage: cov}
}

type vectors struct {
	PolicyVersion string `json:"policy_version"`
	Cases         []struct {
		Name    string `json:"name"`
		Answer  string `json:"answer"`
		Sources string `json:"sources"`
	} `json:"cases"`
}

func main() {
	args := os.Args[1:]
	if len(args) >= 1 && args[0] == "--answer" {
		ans, src := "", ""
		if len(args) >= 2 {
			ans = args[1]
		}
		for i := 0; i < len(args)-1; i++ {
			if args[i] == "--sources" {
				src = args[i+1]
			}
		}
		b, _ := json.Marshal(check(ans, src))
		fmt.Println(string(b))
		return
	}
	vpath := filepath.Join("..", "conformance", "vectors.json")
	if len(args) >= 1 {
		vpath = args[0]
	}
	raw, err := os.ReadFile(vpath)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	var v vectors
	if err := json.Unmarshal(raw, &v); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	results := make([]Verdict, 0, len(v.Cases))
	for _, c := range v.Cases {
		r := check(c.Answer, c.Sources)
		r.Name = c.Name
		results = append(results, r)
	}
	out := map[string]interface{}{"policy_version": v.PolicyVersion, "results": results}
	b, _ := json.MarshalIndent(out, "", "  ")
	fmt.Println(string(b))
}
