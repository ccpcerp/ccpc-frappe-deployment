# CCPC Internal Root CA — owner-verified backup and certificate checkpoint (2026-11-11)

Scope: Windows administrator signing workstation and Synology backup only. This note records operator-reported verification output, not independent access to private key material, the NAS, or running production.

## Verified in Windows PowerShell (owner output)

- The existing passphrase-encrypted RSA-4096 private signing key at the previously approved non-synced Windows local CA workspace was present. Git for Windows OpenSSL key-integrity check returned `CCPC_CA_ROOT_KEY_INTEGRITY_PASS`. No key re-generation or password change.
- Owner copied the **already encrypted** key `ccpc-root-ca.key.pem` to Synology share `ccpcerp-prod_backups/CCPC-Root-CA-Recovery`. Owner downloaded a NAS copy and compared its SHA-256 against the Windows original: `CCPC_ROOT_CA_NAS_BACKUP_VERIFIED`.
- Created **public** self-signed root certificate `ccpc-root-ca.crt.pem` from the same encrypted key. Subject `C=PH, O=CCPC, CN=CCPC Internal Root CA`; notBefore `Nov 11 06:24:49 2026 GMT`, notAfter `Nov 11 06:24:49 2076 GMT` (owner-approved ~50-year validity).
- Public root certificate SHA-256 fingerprint: `59:BF:C1:48:65:6E:30:59:96:C1:B4:C0:29:2E:7F:5B:AE:A8:E0:92:AE:92:EB:E0:B4:4E:43:25:37:D2:46:81`.
- `CCPC_ROOT_CA_KEY_CERT_MATCH_PASS`: certificate public key and encrypted private key public component matched. OpenSSL `verify -check_ss_sig` returned certificate `OK` and `CCPC_ROOT_CA_SIGNATURE_PASS`.
- Root extensions inspected: critical `basicConstraints=CA:TRUE`; critical `keyUsage=Certificate Sign, CRL Sign`; subjectKeyIdentifier and authorityKeyIdentifier both `0E:4E:F4:CB:87:BA:7A:FA:3F:7D:D8:00:E3:BB:B1:C9:BB:88:EC:F1`; inspection marker `CCPC_ROOT_CA_EXTENSION_INSPECTION_COMPLETE`.
- Owner copied public certificate to the same Synology recovery folder, downloaded it back and compared SHA-256 with Windows original: `CCPC_ROOT_CA_CERTIFICATE_NAS_BACKUP_VERIFIED`.

## Protection and remaining limitations

- **No** Root CA private key, passphrase, decrypted key, recovery archive or secret may be uploaded to GitHub. This documentation contains only nonsecret certificate metadata and PASS markers.
- Owner explicitly declined GitHub storage of the key. Synology backup is a second copy of the *same encrypted PEM*, not a separate passphrase. Offline escrow of the sole Root CA passphrase and independently tested full recovery on a replacement workstation have **not** been verified.
- Public CA trust is **not yet installed** on employee devices; CA certificate verification is not a TLS deployment or validation of full client trust.
- Existing NEW-host server leaf key and matching unsigned CSR `ccpcerp.internal.csr` must be **reused**, never regenerated. Its previously verified public CSR SHA-256 is `6f88c8f0001a3c0db15c59446580b0b7057de5f84e86127587c272bc78545a46`. Sign off-host with SAN `DNS:ccpcerp.internal`, EKU `serverAuth`, CA:FALSE, suitable leaf keyUsage and a much shorter leaf lifetime; inspect CSR and verify identity before signing. Keep CA signing key on Windows; return only leaf certificate/chain to NEW.
- The subsequently owner-reported signed server leaf certificate is recorded in the issuance section below. No Windows/root-trust installation, Caddy activation, LAN443 firewall opening, DNS/cutover, OLD PROD+DEV change, NEW ERPNext DB/container change, or employee rollout was performed in that signing step.

Earlier next action (now completed): inspect verified Windows public CSR and sign the server leaf. Keep PR #28 DRAFT and maintain the separately approved NEW-only pilot boundaries.

## November 11, 2026 — server leaf certificate issued off NEW (owner-reported PASS)

- Windows signer rechecked `ccpcerp.internal.csr`: OpenSSL CSR self-signature `Certificate request self-signature verify OK`; `subject=CN=ccpcerp.internal`; digest and SAN guard `CCPC_SERVER_CSR_READY_FOR_SIGNING`.
- Using the existing encrypted Root CA key on Windows, owner performed a no-overwrite OpenSSL CSR signing operation with SHA-256, random 128-bit serial (positive), short validity `-days 365`, and explicit server leaf extensions. **No new CA key or server private key generated.**
- Public leaf `ccpcerp.internal.crt.pem` successfully passed `openssl verify -purpose sslserver -verify_hostname ccpcerp.internal -CAfile <public-root> <leaf>` with `ccpcerp.internal.crt.pem: OK` and marker `CCPC_HTTPS_SERVER_CERTIFICATE_SIGNED_AND_VERIFIED`.
- Observed leaf identity `subject=CN=ccpcerp.internal`, `issuer=C=PH, O=CCPC, CN=CCPC Internal Root CA`; valid from `Nov 11 07:01:07 2026 GMT` until `Nov 11 07:01:07 2027 GMT` (one-year **leaf**, 50-year root unchanged).
- Observed leaf extensions: critical `basicConstraints CA:FALSE`, critical `keyUsage Digital Signature, Key Encipherment`, EKU `TLS Web Server Authentication`, SAN `DNS:ccpcerp.internal`.
- **Not yet performed:** compare public key in signed leaf vs CSR as a separate read-only check, transfer public signed certificate to NEW, verify signed certificate matches NEW server's original leaf private key in situ, install client CA trust, install/activate live Caddy TLS listener, UFW/LAN443 change, employee login/browser tests, Wi-Fi/external denial acceptance, DNS/old PROD+DEV cutover. The Root CA private key must stay off NEW.

Next controlled step: read-only compare signed leaf public key with the already-verified CSR public key on Windows; then stage **only** the public leaf and root certificates to NEW with a no-overwrite guarded procedure. No deployment or production cutover is implied.
