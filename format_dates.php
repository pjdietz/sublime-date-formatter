<?php

$format = $argv[1];

for ($i = 2; $i < $argc; $i++) {

    $source = $argv[$i];
    switch (strtolower($source)) {
        case 'now':
            $source = time();
            break;
        case 'today':
            $source = strtotime('today midnight');
            break;
        default:
            $source = strtotime($source);
    }

    print date($format, $source) . "\n";
}
