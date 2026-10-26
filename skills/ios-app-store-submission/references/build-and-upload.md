# Build, export, and upload — the headless pipeline

Read this file before Phase 2 (build & upload). Every command here mutates real
state on App Store Connect or the local signing environment; the risk tiers and
gates live in SKILL.md. Replace every `<PLACEHOLDER>` from the project fact
sheet (SKILL.md Phase 0) — never invent a value.

## Prerequisites, verified once per machine

- Xcode with the project's SDK; `asc` CLI authenticated (`asc auth doctor`).
  Intermittent 401 storms against ASC usually self-heal within the hour and
  the CLI retries internally — wait rather than churning credentials.
- **If the repo has a release workflow (CI job or script) proven to produce
  uploads, trigger it instead of re-running this pipeline locally** — a
  battle-tested workflow beats a fresh terminal history; fall back to the
  manual steps below when it fails or doesn't exist.
- The Apple Distribution certificate lives in a dedicated keychain on build
  machines (e.g. `~/.appstoreconnect/signing.keychain-db`, first in the search
  list). Codesign and export die with `errSecInternalComponent` if it is locked,
  so unlock it before archiving:

  ```bash
  security unlock-keychain -p "$(tr -d '\n' < <KEYCHAIN_PASS_FILE>)" <KEYCHAIN_PATH>
  security set-key-partition-list -S apple-tool:,apple: -k "$(tr -d '\n' < <KEYCHAIN_PASS_FILE>)" <KEYCHAIN_PATH>
  ```

  `set-key-partition-list` is what lets `xcodebuild` and the export step use the
  key without prompting; skip it and the next CLI invocation re-locks.
- Info.plist declares `ITSAppUsesNonExemptEncryption=false` (or an encryption
  declaration exists) so compliance auto-clears; if not, clear it on ASC or add
  the key — a build without it stalls in "Pending Compliance" and TestFlight
  testers cannot install.

## Step 1 — bump the build number

App Store Connect rejects a re-upload of the same (marketing version, build)
pair, so bump the build number before every archive. XcodeGen projects: bump
`CURRENT_PROJECT_VERSION` in `project.yml`, then `xcodegen generate` (a MUST —
hand-editing the `.xcodeproj` drifts from the spec). Plain `.xcodeproj`
projects: `agvtool new-version -all <N>` from the project root. Commit the bump
with the upload bookkeeping, not silently.

## Step 2 — archive Release

```bash
xcodebuild archive \
  -project <PROJECT>.xcodeproj -scheme <SCHEME> \
  -configuration Release -destination 'generic/platform=iOS' \
  -archivePath .asc/artifacts/<PROJECT>.xcarchive \
  -allowProvisioningUpdates -quiet
```

`generic/platform=iOS` builds the device slice without needing a device attached.
Verify the archive before exporting — exporting a wrong-version archive wastes a
15–45 minute processing cycle:

```bash
/usr/libexec/PlistBuddy -c "Print :CFBundleShortVersionString" -c "Print :CFBundleVersion" \
  .asc/artifacts/<PROJECT>.xcarchive/Products/Applications/<APP>.app/Info.plist
```

## Step 3 — provisioning profile (create once, reuse until expiry)

Xcode automatic export fails on machines with no Apple ID logged into Xcode
("No profiles found") — that is expected, not a bug to work around by logging
in. Create the App Store profile through the API instead:

```bash
asc profiles create --name "<APP> App Store <date>" --profile-type IOS_APP_STORE \
  --bundle <BUNDLE_ID_TEAM_PREFIX> --certificate <DIST_CERT_ID>
asc profiles download --name "<APP> App Store <date>"
# install to ~/Library/MobileDevice/Provisioning Profiles/<UUID>.mobileprovision
# (UUID comes from `security cms -D -i <file>` on the downloaded profile)
```

Check for an existing valid profile first (`asc profiles list`) — recreating per
build is unnecessary churn. The profile referenced in the export options must be
installed under exactly the name the options file names, or export fails.

## Step 4 — export the IPA

Use a manual export options plist (template in `assets/export-options.plist`):
method `app-store-connect`, `signingStyle` manual, the full signing-certificate
name, and a `provisioningProfiles` map naming the installed profile. Then:

```bash
xcodebuild -exportArchive -archivePath .asc/artifacts/<PROJECT>.xcarchive \
  -exportOptionsPlist <EXPORT_OPTIONS>.plist -exportPath .asc/artifacts/ipa-b<N>
```

Export into a fresh per-build directory; keeping build N-1's IPA around costs
nothing and saves a re-export when the upload needs re-checking.

## Step 5 — upload, then poll for VALID

```bash
asc builds upload --app <APP_ID> --ipa .asc/artifacts/ipa-b<N>/<PROJECT>.ipa
```

"Upload committed" means the bytes arrived, nothing more. The build resource
takes minutes to ~45 min to appear and process; poll with a sleep loop:

```bash
asc builds list --app <APP_ID>   # watch for version <N>, processingState VALID
```

Only a VALID build can be attached or distributed. If processing ends in FAILED,
the failure email in ASC names the cause (missing icon, bad launch screen,
entitlement mismatch) — fix that cause; do not re-upload the same bytes hoping
for a different verdict.

## Step 6 — attach to the version

```bash
asc versions attach-build --app <APP_ID> --version "<VERSION_STRING>" --build-number "<N>"
```

Attach is what makes the build the one Apple reviews; a VALID build sitting
unattached is not "ready for submission". Re-run `asc validate` after attaching —
attaching can surface new checks (e.g. encryption declaration).

## Error map — known failures and the one fix each

Read the error, fix the named cause, retry once. Do not vary other parameters to
probe; each upload attempt is a real write on ASC.

| Symptom | Cause | Fix |
|---|---|---|
| `errSecInternalComponent` during codesign/export | Signing keychain locked | Re-run the unlock + partition-list pair from Prerequisites |
| Export: "No profiles for ... found" | No Xcode Apple ID on this machine, or profile not installed | Create via `asc profiles` and install under the exact name in the options plist |
| Upload rejected, error 90476, mentions `UILaunchStoryboardName` | Info.plist references a storyboard the Release archive doesn't package | Declare an empty `UILaunchScreen` dict instead of a storyboard name |
| `asc versions attach-build` matches nothing | Build still processing, or version string mismatch | Poll `asc builds list` first; pass the version string ASC reports (it may differ from the marketing version) |
| Build VALID but testers can't install | Missing encryption compliance | Add `ITSAppUsesNonExemptEncryption=false` or clear the declaration; next build picks it up |
