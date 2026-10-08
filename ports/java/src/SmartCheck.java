import java.nio.file.*;
import java.util.*;
import java.util.regex.*;

/*
 * SmartCheck - native Java port.
 * Faithfully reproduces the Python reference (sf_smartcheck.core.check): identical
 * rule IDs, confidences, span strings, ordering and citation-coverage logic.
 * Verified against ports/conformance/expected.json. JDK-only (no dependencies).
 *
 *   javac SmartCheck.java
 *   java  SmartCheck [vectors.json]     # batch -> {"results":[...]}
 *   java  SmartCheck --answer "text" [--sources "text"]
 */
public class SmartCheck {

    static final Pattern NUM = Pattern.compile(
        "\\b\\d{3,}\\b|\\b\\d+(?:\\.\\d+)?\\s?%|\\b\\d+(?:\\.\\d+)?\\s*(?:hundred|thousand|million|billion|trillion)\\b",
        Pattern.CASE_INSENSITIVE);
    static final Pattern CONTRA = Pattern.compile(
        "\\balways\\b.*\\bnever\\b|\\bnever\\b.*\\balways\\b", Pattern.CASE_INSENSITIVE);
    static final Pattern HEDGE = Pattern.compile(
        "\\b(?:as of my knowledge|i think|maybe|probably)\\b", Pattern.CASE_INSENSITIVE);
    static final Pattern DIGIT = Pattern.compile("\\d");

    record Issue(String type, double confidence, String span) {}
    record Verdict(boolean passed, List<Issue> issues, double citationCoverage) {}

    static Verdict check(String answer, String sources) {
        List<Issue> issues = new ArrayList<>();
        boolean hasSources = sources != null && !sources.isEmpty();
        if (NUM.matcher(answer).find() && !hasSources)
            issues.add(new Issue("CHECK-UNSOURCED-NUMBER", 0.6, "numeric claim with no source"));
        if (CONTRA.matcher(answer).find())
            issues.add(new Issue("CHECK-CONTRADICTION", 0.7, "internal contradiction"));
        if (HEDGE.matcher(answer).find())
            issues.add(new Issue("CHECK-HEDGED", 0.5, "hedged/uncertain claim stated as fact"));
        if (answer.contains("[contains seeded error]"))
            issues.add(new Issue("CHECK-SEEDED", 0.9, "known seeded error (demo)"));
        double coverage = hasSources ? 1.0 : (DIGIT.matcher(answer).find() ? 0.0 : 0.5);
        return new Verdict(issues.isEmpty(), issues, coverage);
    }

    // ---------- JSON output ----------
    static String esc(String s) {
        StringBuilder b = new StringBuilder();
        for (char c : s.toCharArray()) {
            switch (c) {
                case '"' -> b.append("\\\"");
                case '\\' -> b.append("\\\\");
                case '\n' -> b.append("\\n");
                case '\r' -> b.append("\\r");
                case '\t' -> b.append("\\t");
                default -> b.append(c);
            }
        }
        return b.toString();
    }

    static String verdictJson(String name, Verdict v) {
        StringBuilder b = new StringBuilder("{");
        if (name != null) b.append("\"name\":\"").append(esc(name)).append("\",");
        b.append("\"passed\":").append(v.passed()).append(",\"issues\":[");
        for (int i = 0; i < v.issues().size(); i++) {
            Issue is = v.issues().get(i);
            if (i > 0) b.append(",");
            b.append("{\"type\":\"").append(esc(is.type())).append("\",\"confidence\":")
             .append(is.confidence()).append(",\"span\":\"").append(esc(is.span())).append("\"}");
        }
        b.append("],\"citation_coverage\":").append(v.citationCoverage()).append("}");
        return b.toString();
    }

    public static void main(String[] args) throws Exception {
        if (args.length >= 1 && args[0].equals("--answer")) {
            String ans = args.length >= 2 ? args[1] : "";
            String src = "";
            for (int i = 0; i < args.length - 1; i++) if (args[i].equals("--sources")) src = args[i + 1];
            System.out.println(verdictJson(null, check(ans, src)));
            return;
        }
        String vpath = args.length >= 1 ? args[0]
            : Paths.get(System.getProperty("user.dir"), "..", "conformance", "vectors.json").toString();
        String raw = Files.readString(Paths.get(vpath));
        Json j = new Json(raw);
        Map<String, Object> root = j.parseObject();
        Object pv = root.get("policy_version");
        @SuppressWarnings("unchecked")
        List<Object> cases = (List<Object>) root.get("cases");
        StringBuilder out = new StringBuilder("{\"policy_version\":");
        out.append(pv == null ? "null" : "\"" + esc((String) pv) + "\"").append(",\"results\":[");
        for (int i = 0; i < cases.size(); i++) {
            @SuppressWarnings("unchecked")
            Map<String, Object> c = (Map<String, Object>) cases.get(i);
            String ans = (String) c.getOrDefault("answer", "");
            String src = (String) c.getOrDefault("sources", "");
            if (i > 0) out.append(",");
            out.append(verdictJson((String) c.get("name"), check(ans, src)));
        }
        out.append("]}");
        System.out.println(out);
    }

    // ---------- minimal JSON parser (objects/arrays/strings/numbers/bools/null) ----------
    static class Json {
        final String s; int i;
        Json(String s) { this.s = s; }
        void ws() { while (i < s.length() && Character.isWhitespace(s.charAt(i))) i++; }
        Map<String, Object> parseObject() { ws(); return (Map<String, Object>) value(); }
        Object value() {
            ws(); char c = s.charAt(i);
            return switch (c) {
                case '{' -> obj();
                case '[' -> arr();
                case '"' -> str();
                case 't', 'f' -> bool();
                case 'n' -> nul();
                default -> num();
            };
        }
        Map<String, Object> obj() {
            Map<String, Object> m = new LinkedHashMap<>(); i++; ws();
            if (s.charAt(i) == '}') { i++; return m; }
            while (true) {
                ws(); String k = str(); ws(); i++; /* colon */
                m.put(k, value()); ws();
                if (s.charAt(i) == ',') { i++; continue; }
                i++; break; /* } */
            }
            return m;
        }
        List<Object> arr() {
            List<Object> a = new ArrayList<>(); i++; ws();
            if (s.charAt(i) == ']') { i++; return a; }
            while (true) {
                a.add(value()); ws();
                if (s.charAt(i) == ',') { i++; continue; }
                i++; break; /* ] */
            }
            return a;
        }
        String str() {
            StringBuilder b = new StringBuilder(); i++; /* opening quote */
            while (true) {
                char c = s.charAt(i++);
                if (c == '"') break;
                if (c == '\\') {
                    char e = s.charAt(i++);
                    switch (e) {
                        case '"' -> b.append('"');
                        case '\\' -> b.append('\\');
                        case '/' -> b.append('/');
                        case 'n' -> b.append('\n');
                        case 'r' -> b.append('\r');
                        case 't' -> b.append('\t');
                        case 'b' -> b.append('\b');
                        case 'f' -> b.append('\f');
                        case 'u' -> { b.append((char) Integer.parseInt(s.substring(i, i + 4), 16)); i += 4; }
                        default -> b.append(e);
                    }
                } else b.append(c);
            }
            return b.toString();
        }
        Object bool() { if (s.startsWith("true", i)) { i += 4; return Boolean.TRUE; } i += 5; return Boolean.FALSE; }
        Object nul() { i += 4; return null; }
        Object num() {
            int st = i;
            while (i < s.length() && "+-.eE0123456789".indexOf(s.charAt(i)) >= 0) i++;
            return Double.parseDouble(s.substring(st, i));
        }
    }
}
