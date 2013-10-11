<?php

/**
 * Read the command line for a string date followed by any number of format
 * string. Parse the string date to a timestamp, then output that timestamp
 * formatted with each format string on a separat line.
 */

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
