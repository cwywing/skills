# TestFlight and access — team invites, internal groups, delivery

Read this file before Phase 3 (TestFlight & access). Most "TestFlight 邀请收
不到" incidents are not a TestFlight failure — they are a missing prerequisite
two steps upstream. Diagnose the chain before touching anything.

## The dependency chain (internal testing)

Internal testing requires **team membership first**. The chain, in order:

1. ASC team invitation to the person's email (`asc users invite --email ...
   --roles DEVELOPER --visible-app <APP_ID>` or `--all-apps`).
2. The invitee accepts via the email link (email comes from Apple; invite has a
   short expiry — days, not weeks).
3. Add the accepted user to the app's internal beta group
   (`asc testflight testers add --app <APP_ID> --email ... --group <GROUP_ID>`);
   Apple then emails the TestFlight invitation.
4. The invitee accepts in the TestFlight app and installs.

A stuck invitee is almost always at step 2. Check the actual state at each hop
instead of guessing which hop failed:

```bash
asc users list --output json          # accepted members — is the email here?
asc users invites list --output json  # pending invitations + expiry dates
asc testflight testers list --app <APP_ID> --output json
```

If the email is in neither `users` nor `invites`, the invitation never existed
or was revoked — re-invite. If it is in `invites` with an expiry days away, the
email went to spam (consumer mail providers, notably 163/QQ, aggressively
filter Apple mail): revoke + re-invite to generate a fresh email with a fresh
expiry, and have the person check the junk folder and the provider's
block/whitelist settings. If a second email also vanishes, re-invite to an
inbox on a different provider — do not keep re-sending into the same filter.

External testing (a beta group not tied to team membership) avoids step 1–2 but
puts the first build through Beta App Review; for an app about to submit for
production review anyway, internal is the faster path. Public links exist only
for external groups — useful for real-user betas without collecting Apple IDs,
and each build under a public link must clear Beta App Review before testers
see it. Before submission day, walk the attached build once through the
internal group (the same binary a reviewer will get); a build that never
reached TestFlight has untested install compliance.

## Known failure modes (each happened; each has one fix)

| Symptom | Cause | Fix |
|---|---|---|
| `asc testflight testers add` fails "Tester(s) cannot be assigned" | Invitee has not accepted the team invitation yet | Wait for acceptance; verify in `asc users list`, then retry once |
| Re-invite fails "email already being used" right after a revoke | ASC backend eventual consistency (~1 min) | Sleep 60s, retry the identical command once |
| Invitee "never got any email" but is in `invites` | Apple mail filtered to spam, or invite already expired | Revoke + re-invite (fresh email + expiry); check junk; consider provider whitelist |
| Tester in group, build processed, still no install | Build lacks encryption compliance (Pending Compliance) | See build-and-upload.md error map |
| Group has testers but no builds offered | Group lacks build access | Prefer internal groups with access-to-all-builds; verify via `asc testflight groups list` |

## Review-contact phone fills TWO forms

The App Review contact phone (review details) and the Beta App Review contact
are the same human data entered twice: create review details once
(`asc review details-create`), and set the beta-review side with
`asc testflight review edit` — collect the phone once from the human and fill
both, instead of discovering the second form on submit day.

## Operational rules

- IDs (`GROUP_ID`, invite IDs, tester IDs) come only from command output in
  this conversation — the group id in `asc testflight groups list`, not from
  memory of the web UI.
- Adding a tester or re-inviting a user is lower-risk (single record, easily
  reversed): confirm intent once, act. **Revoking** an invitation or deleting a
  user is higher-risk — restate in human terms who loses access and what
  expires before acting, since the pending email may be sitting unread in spam
  and deletion removes that option.
- After any access change, tell the human exactly which email to look for and
  from whom — "check spam for the Apple team invitation" is the message; the
  mechanics of how you verified it are backstage.
- When a build goes out and testers report nothing, `asc testflight
  notifications send --build-id <BUILD_ID>` re-notifies the group before anyone
  assumes delivery failed.
