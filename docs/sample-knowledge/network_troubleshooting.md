# Network Troubleshooting Runbook

## Initial checks
Confirm whether the failure affects one device, one site, or all users. Record the timestamp, connection type, IP address, gateway, and DNS resolver. Test the local loopback, gateway, and a known external IP in that order.

## DNS failures
If an IP address responds but a hostname does not, inspect the configured DNS resolver. Clear the local DNS cache, query the approved resolver directly, and compare the returned record with the service inventory. Do not change DNS globally before confirming scope.

## Escalation
Escalate as high priority when a site is offline. Treat a company-wide outage as critical. Attach command output with secrets removed.