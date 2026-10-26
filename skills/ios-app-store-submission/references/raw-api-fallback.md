# Raw API fallback — when the asc CLI can't reach

Prefer the asc CLI; drop to the raw REST API when an operation is outside the
CLI's coverage or its error message misleads. The executor is
`scripts/asc_api.py` (zero-config beyond credentials; JWT header carries ONLY
alg/kid — adding `typ` returns 401). It exists because `curl` to
api.appstoreconnect.apple.com intermittently blackholes behind some proxies,
while python urllib + ES256 is stable; it also retries 409/429/5xx with
backoff, which the raw path otherwise lacks.

```
python3 scripts/asc_api.py GET "/v1/apps?filter[bundleId]=<BUNDLE_ID>&fields[apps]=name"
python3 scripts/asc_api.py PATCH "/v1/.../<ID>" body.json      # body file, or "-" for stdin
```

Credentials come from `ASC_KEY_ID` / `ASC_ISSUER_ID` / `ASC_KEY_PATH`, or any
`~/.appstoreconnect/*.env` exporting them. **The raw API has no asc validation
layer and its errors are more cryptic** — before any write here, re-read the
bright lines in SKILL.md: IDs from results only, one fix then one retry, no
field-probing (a 409 is not an invitation to vary the body).

Endpoint traps below each cost a real debugging round; check the list before
writing, not after.

## Read-only starters

```
GET /v1/apps?filter[bundleId]=<BUNDLE>                        # app record → numeric app id
GET /v1/apps/{id}/appStoreVersions                            # versions → versionId
GET /v1/builds?filter[app]={id}&sort=-uploadedDate&limit=5    # builds + processingState
GET /v1/appCategories?limit=200                               # category id IS the enum: TRAVEL/UTILITIES…
```

Two identity systems coexist: the numeric app id (APIs) and the 10-digit
Apple ID (team/account views) are different numbers — never substitute one for
the other. Version resource relationship names are whatever
`GET /v1/appStoreVersions/{id}` returns: pricing hangs off `apps` as
`appPriceSchedule`, availability as `appAvailabilityV2` (older
`availableTerritories` paths are gone).

## appInfo localizations (name / subtitle / privacy URL)

```
PATCH /v1/appInfoLocalizations/{locId}          # edit an existing locale
POST  /v1/appInfoLocalizations                  # create: attributes{locale,name,subtitle,privacyPolicyUrl} + relationships.appInfo
```

- `POST /v1/appInfos/{id}/appInfoLocalizations` is **405** — the collection is
  top-level only.
- PATCH attributes must **not include `locale`** (409).
- Creating an appInfoLocalization **auto-creates** the matching version
  localization; a second POST fails DUPLICATE — list first, then PATCH.

## Version localizations (description / keywords / promo text / supportUrl)

```
GET   /v1/appStoreVersions/{vid}/appStoreVersionLocalizations   # list → per-locale ids
PATCH /v1/appStoreVersionLocalizations/{locId}                 # no locale in attributes
POST  /v1/appStoreVersionLocalizations                         # only if the locale truly missing
```

## Age rating — one call, all fields, two types

`PATCH /v1/ageRatingDeclarations/{appInfoId}` must carry **every required
field at once**; partial PATCHes fail missing-required. Boolean fields
(advertising, gambling, messagingAndChat, userGeneratedContent, …) and
NONE-enum fields (alcoholOrTobacco, violenceRealistic, horrorOrFearThemes, …)
mix in one body. `GET` on this resource is 403 (update-only) — success is the
PATCH 200 itself. A utility app answering no/NONE across the board computes 4+;
1:1 customer support chat does not count as UGC/messaging.

## Attach build — to-one relationships take an OBJECT

```
PATCH /v1/appStoreVersions/{vid}/relationships/build
{"data": {"type": "builds", "id": "<buildId>"}}     # object! an array → "expects data as an object"
```

Poll `processingState == VALID` before attaching; buildId comes from the
builds list result (in current API it often equals the upload's Delivery UUID).

## Direct screenshot upload (asc unavailable)

Three steps: reserve → chunked PUT → commit.

1. `POST /v1/appScreenshotSets` — attributes{screenshotDisplayType} +
   relationships.appStoreVersionLocalization.
2. `POST /v1/appScreenshots` — attributes{fileName,fileSize} +
   relationships.**appScreenshotSet** (singular; plural → unknown-relationship).
   The response carries `uploadOperations[]` (url/offset/length/method): PUT
   the binary chunks at their offsets, no auth header on those PUTs.
3. `PATCH /v1/appScreenshots/{id}` — attributes{uploaded:true,
   sourceFileChecksum:<MD5>}.

PNGs must have no alpha channel. For capture/retouch/sizing before this point,
read `references/screenshots-capture.md`.
