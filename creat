
<?php
// VulnCentral - PHP + PostgreSQL

$host = getenv("DB_HOST") ?: "localhost";
$port = getenv("DB_PORT") ?: "5432";
$dbname = getenv("DB_NAME") ?: "vulncentral";
$user = getenv("DB_USER") ?: "postgres";
$password = getenv("DB_PASSWORD") ?: "password";

try {
    $pdo = new PDO(
        "pgsql:host=$host;port=$port;dbname=$dbname",
        $user,
        $password,
        [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
    );
} catch (PDOException $e) {
    http_response_code(500);
    exit("Database connection failed.");
}

$q = trim($_GET["q"] ?? "");
$severity = strtoupper(trim($_GET["severity"] ?? ""));

$allowed = ["", "CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"];

if (!in_array($severity, $allowed, true)) {
    $severity = "";
}

$sql = "
    SELECT cve_id, title, description, severity,
           cvss_score, affected_product, remediation
    FROM vulnerabilities
    WHERE (
        :empty_q = ''
        OR cve_id ILIKE :cve
        OR title ILIKE :title
        OR description ILIKE :description
    )
    AND (:empty_severity = '' OR severity = :severity)
    ORDER BY cvss_score DESC NULLS LAST
";

$stmt = $pdo->prepare($sql);
$keyword = "%$q%";

$stmt->execute([
    "empty_q" => $q,
    "cve" => $keyword,
    "title" => $keyword,
    "description" => $keyword,
    "empty_severity" => $severity,
    "severity" => $severity
]);

$records = $stmt->fetchAll(PDO::FETCH_ASSOC);

$stats = $pdo->query("
    SELECT severity, COUNT(*) AS total
    FROM vulnerabilities
    GROUP BY severity
")->fetchAll(PDO::FETCH_KEY_PAIR);

$total = array_sum($stats);

function h($value) {
    return htmlspecialchars(
        (string)($value ?? ""),
        ENT_QUOTES,
        "UTF-8"
    );
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VulnCentral Security Dashboard</title>

<style>
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #0b1220;
    color: #e5edf8;
}
header {
    padding: 24px;
    background: #111c30;
    border-bottom: 1px solid #253650;
}
h1 { color: #67e8f9; margin: 0 0 8px; }
main { padding: 24px; max-width: 1200px; margin: auto; }
.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 14px;
    margin-bottom: 24px;
}
.card, .panel {
    background: #142137;
    border: 1px solid #293b57;
    border-radius: 12px;
    padding: 18px;
}
.number { font-size: 28px; font-weight: bold; }
.critical { color: #fb7185; }
.high { color: #fb923c; }
.medium { color: #facc15; }
.low { color: #4ade80; }
form { display: flex; gap: 10px; flex-wrap: wrap; }
input, select, button {
    padding: 11px;
    border-radius: 7px;
    border: 1px solid #344761;
}
input, select { background: #0b1220; color: white; }
button {
    background: #0891b2;
    color: white;
    cursor: pointer;
}
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; margin-top: 16px; }
th, td {
    padding: 13px;
    text-align: left;
    border-bottom: 1px solid #293b57;
    vertical-align: top;
}
th { color: #67e8f9; }
a { color: #67e8f9; }
small { color: #a8b7cc; }
</style>
</head>

<body>
<header>
    <h1>🛡️ VulnCentral</h1>
    <div>Centralized Vulnerability Registry</div>
</header>

<main>
    <h2>Security Overview</h2>

    <section class="cards">
        <div class="card">
            <small>Total vulnerabilities</small>
            <div class="number"><?= h($total) ?></div>
        </div>

        <?php foreach (["CRITICAL", "HIGH", "MEDIUM", "LOW"] as $level): ?>
        <div class="card">
            <small><?= h($level) ?> severity</small>
            <div class="number <?= strtolower($level) ?>">
                <?= h($stats[$level] ?? 0) ?>
            </div>
        </div>
        <?php endforeach; ?>
    </section>

    <section class="panel">
        <h2>Search Vulnerabilities</h2>

        <form method="GET">
            <input
                type="search"
                name="q"
                placeholder="Search CVE or keyword"
                value="<?= h($q) ?>"
            >

            <select name="severity">
                <option value="">All severities</option>
                <?php foreach (["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"] as $level): ?>
                <option value="<?= h($level) ?>"
                    <?= $severity === $level ? "selected" : "" ?>>
                    <?= h($level) ?>
                </option>
                <?php endforeach; ?>
            </select>

            <button type="submit">Search</button>
            <a href="index.php">Reset</a>
        </form>

        <div class="table-wrap">
        <table>
            <thead>
                <tr>
                    <th>CVE ID</th>
                    <th>Vulnerability</th>
                    <th>Severity</th>
                    <th>CVSS</th>
                    <th>Affected Product</th>
                    <th>Remediation</th>
                </tr>
            </thead>
            <tbody>
            <?php if (!$records): ?>
                <tr>
                    <td colspan="6">No matching vulnerabilities found.</td>
                </tr>
            <?php else: ?>
                <?php foreach ($records as $row): ?>
                <tr>
                    <td>
                        <a target="_blank" rel="noopener noreferrer"
                           href="https://nvd.nist.gov/vuln/detail/<?= rawurlencode($row["cve_id"]) ?>">
                           <?= h($row["cve_id"]) ?>
                        </a>
                    </td>
                    <td>
                        <strong><?= h($row["title"]) ?></strong><br>
                        <small><?= h($row["description"]) ?></small>
                    </td>
                    <td class="<?= strtolower(h($row["severity"])) ?>">
                        <?= h($row["severity"]) ?>
                    </td>
                    <td><?= h($row["cvss_score"]) ?></td>
                    <td><?= h($row["affected_product"]) ?></td>
                    <td><?= h($row["remediation"]) ?></td>
                </tr>
                <?php endforeach; ?>
            <?php endif; ?>
            </tbody>
        </table>
        </div>

        <p><small>
            Showing <?= count($records) ?> matching records.
            Verify remediation using official vendor advisories.
        </small></p>
    </section>
</main>
</body>
</html>
