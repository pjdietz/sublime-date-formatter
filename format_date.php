<?php

$source = $argv[1];

switch (strtolower($source)) {
    case 'now':
        $source = time();
        break;
    case 'today':
        $source = strtotime('today midnight');
        break;
    default:
        $source = strtotime($argv[1]);
}

for ($i = 2; $i < $argc; $i++) {
    print date($argv[$i], $source) . "\n";
}
