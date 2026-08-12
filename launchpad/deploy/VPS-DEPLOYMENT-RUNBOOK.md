# Launchpad Buzz VPS deployment runbook

## Audience and authority

This runbook is for human operators and automation agents from any provider.
The same commands and safety boundaries apply regardless of who performs the
deployment.

The supported entry point is:

```text
launchpad/deploy/run.sh
```

It validates Launchpad image policy and delegates orchestration to
`deploy/compose/run.sh`. Do not execute, copy, or repair deployment material
under `launchpad/deploy/archived/`; it is a record of a failed method.

Agents must also obey the repository instructions in `launchpad/AGENTS.md` and
`launchpad/deploy/AGENTS.md`. An agent must not start, stop, upgrade, or roll
back a production VPS unless the human request explicitly authorizes that
state change.

## Required inputs

Before changing a VPS, identify all of the following:

- the exact approved 40-character Git commit from the `launchpad` branch;
- a successful `Docker image` workflow run for that commit;
- the corresponding `ghcr.io/launchpad-26/buzz` full-SHA tag or, preferably,
  manifest digest;
- the VPS public domain and DNS record if Caddy will provide HTTPS;
- the relay owner public key;
- stable relay, database, Redis, S3, and git-hook secrets; and
- a rollback image plus compatible pre-change data backups for an upgrade.

Stop if the approved commit, successful workflow run, image identity, package
access, production secrets, backup state, or migration compatibility is
unknown. Do not substitute `:launchpad`, `:latest`, `:main`, or any
`ghcr.io/block/buzz` image.

Never paste `deploy/compose/.env`, tokens, private keys, or secret-bearing
command output into an issue, pull request, chat, agent log, or terminal capture.

## VPS prerequisites

Use a supported Ubuntu VPS with:

- SSH and `sudo` access;
- Docker Engine;
- Docker Compose V2 version 2.24.4 or newer;
- Git;
- outbound HTTPS access to GitHub and GHCR; and
- ports 80 and 443 allowed when using the Caddy TLS configuration.

Install Docker Engine and the Compose plugin through Docker's supported Ubuntu
installation method. The project does not maintain a separate Docker installer.
Confirm the installed tools before continuing:

```bash
docker --version
docker compose version
git --version
```

If `ghcr.io/launchpad-26/buzz` is private, authenticate Docker to GHCR using a
least-privileged credential with package-read access. Supply the credential
through a secure interactive or secret-management channel; do not place it in
the repository or this runbook.

## Fresh VPS deployment

### 1. Check out the canonical deployment files

Run as the intended non-root deployment user:

```bash
git clone --branch launchpad --single-branch https://github.com/launchpad-26/buzz.git
cd buzz
git status --short --branch
```

The checked-out repository supplies the deployment files. It does not cause the
VPS to build the relay image.

### 2. Select and verify an exact source commit

Set `SOURCE_COMMIT` to the approved, full 40-character commit from the
successful workflow run, then confirm that the commit exists in the checkout:

```bash
SOURCE_COMMIT='<APPROVED_FULL_40_CHARACTER_GIT_COMMIT>'
git show --no-patch --format='commit=%H subject=%s' "$SOURCE_COMMIT"
IMAGE_TAG="ghcr.io/launchpad-26/buzz:sha-${SOURCE_COMMIT}"
printf 'candidate_image=%s\n' "$IMAGE_TAG"
```

`<APPROVED_FULL_40_CHARACTER_GIT_COMMIT>` is an instruction marker, not a real
value. Do not continue until it has been replaced and the output shows the same
commit that the operator approved.

If GitHub CLI is available, confirm the workflow conclusion without exposing
credentials:

```bash
gh run list \
  --repo launchpad-26/buzz \
  --workflow docker.yml \
  --commit "$SOURCE_COMMIT" \
  --json databaseId,status,conclusion,headSha,url
```

Continue only when the relevant non-PR publication run completed successfully.
A pull-request build does not publish an image.

### 3. Pull the full-SHA tag and resolve its digest

```bash
docker pull "$IMAGE_TAG"
IMAGE_REF=$(docker image inspect \
  --format '{{index .RepoDigests 0}}' \
  "$IMAGE_TAG")
printf 'immutable_image=%s\n' "$IMAGE_REF"
```

The printed value must start with:

```text
ghcr.io/launchpad-26/buzz@sha256:
```

Stop if it points anywhere else. The digest reference is the preferred
production value because it cannot move after publication.

When GitHub CLI supports attestation verification on the host, verify the
artifact before deployment:

```bash
gh attestation verify "oci://${IMAGE_REF}" --owner launchpad-26
```

If attestation verification is unavailable, record that fact for the reviewer;
do not claim provenance verification was performed.

### 4. Create the local production configuration

```bash
cp deploy/compose/.env.example deploy/compose/.env
chmod 600 deploy/compose/.env
${EDITOR:?Set EDITOR to a trusted terminal editor} deploy/compose/.env
```

In the editor:

1. replace every `CHANGE_ME` value;
2. set `BUZZ_IMAGE` to the exact value printed as `immutable_image`;
3. set the public domain and URL values consistently;
4. set `RELAY_OWNER_PUBKEY` to the intended 64-character hex public key;
5. generate and store stable secrets through the operator's approved secret
   process; and
6. decide migration behavior deliberately before the first start.

`BUZZ_AUTO_MIGRATE=true` lets the relay apply embedded migrations on startup.
For an established production database, migration and backup compatibility must
be reviewed before an image change. Do not rotate stable secrets during a
restart or upgrade.

The `.env` file is ignored by Git. Confirm only its permissions and ignore
status; do not print its contents:

```bash
stat -c '%a %n' deploy/compose/.env
git check-ignore deploy/compose/.env
```

### 5. Validate without starting services

```bash
./launchpad/deploy/run.sh check
./launchpad/deploy/run.sh backup-hint
```

The guard prints the selected public image reference and Compose version. It
must report that the deployment configuration is valid. It must not print
secrets.

### 6. Start the stack

For a public VPS where Caddy terminates HTTPS:

```bash
export BUZZ_COMPOSE_TLS=true
./launchpad/deploy/run.sh start
./launchpad/deploy/run.sh status
```

For an intentionally non-TLS development environment, omit the exported TLS
switch. Do not use the non-TLS form for a public production relay without a
separate, reviewed TLS terminator.

`start` runs `docker compose up -d --wait`. It does not run an explicit pull.
Compose may fetch an absent image, but it may reuse an image already present on
the VPS. Pulling and resolving the immutable image in step 3 removes that
ambiguity for the first deployment.

### 7. Verify health and running identity

Read the public domain without displaying the rest of `.env`, then check the
relay and inspect the running image:

<!-- markdownlint-disable MD013 -->

```bash
BUZZ_DOMAIN=$(sed -n 's/^BUZZ_DOMAIN=//p' deploy/compose/.env)
curl --fail --silent --show-error "https://${BUZZ_DOMAIN}/_liveness"

container_id=$(docker compose \
  --env-file deploy/compose/.env \
  -f deploy/compose/compose.yml \
  ps -q relay)

docker inspect \
  --format 'configured={{.Config.Image}} image_id={{.Image}}' \
  "$container_id"

image_id=$(docker inspect --format '{{.Image}}' "$container_id")
docker image inspect \
  --format 'repo_digests={{json .RepoDigests}} revision={{index .Config.Labels "org.opencontainers.image.revision"}} source={{index .Config.Labels "org.opencontainers.image.source"}}' \
  "$image_id"
```

<!-- markdownlint-enable MD013 -->

Confirm all four facts:

1. `configured=` equals the reviewed `BUZZ_IMAGE` digest;
2. `repo_digests` includes the same Launchpad digest;
3. `revision=` equals `SOURCE_COMMIT`; and
4. `source=` is `https://github.com/launchpad-26/buzz`.

If any value differs, stop and investigate before declaring the deployment
successful.

## Command behavior

All supported operations should go through `launchpad/deploy/run.sh` so image
policy is checked first.

<!-- markdownlint-disable MD013 -->

| Command | Canonical behavior | Pulls images? |
|---|---|---|
| `check` | Renders and validates the Compose configuration. | No. |
| `start` | Runs `compose up -d --wait`. | No explicit pull; Compose may fetch a missing image. |
| `pull` | Runs `compose pull`. | Yes, for configured service images. |
| `upgrade` | Runs `compose pull`, then `compose up -d --wait`, then prints backup reminders. | Yes, for all configured service images, not only the relay. |
| `restart` | Runs `compose up -d --wait --force-recreate relay`. | No. |
| `stop` | Runs `compose down` without `--volumes`. | No; named volumes remain. |
| `status` | Runs `compose ps`. | No. |
| `logs [service]` | Follows logs; defaults to `relay`. | No. |

<!-- markdownlint-enable MD013 -->

Because `upgrade` pulls all configured service images, review the whole Compose
configuration and backups before production upgrades. A relay digest pin does
not make the other service tags immutable.

## Intentional upgrade

1. Approve a new full source commit and confirm its non-PR Docker workflow run
   succeeded.
2. Pull its full-SHA tag, resolve the manifest digest, and verify provenance as
   in fresh-deployment steps 2 and 3.
3. Record the currently running `BUZZ_IMAGE`, Git revision, and image digest.
4. Run the backup checklist and create coordinated Postgres, MinIO/media, and
   git-data backups from the same maintenance window.
5. Review database migrations between the running and target commits.
6. Edit only `BUZZ_IMAGE` in the local `.env` unless the release explicitly
   requires another reviewed configuration change.
7. Validate, upgrade, and inspect the result:

```bash
export BUZZ_COMPOSE_TLS=true
./launchpad/deploy/run.sh check
./launchpad/deploy/run.sh backup-hint
./launchpad/deploy/run.sh upgrade
./launchpad/deploy/run.sh status
```

Repeat the health and identity checks from fresh-deployment step 7. Do not use
`restart` as an upgrade command: it does not pull the target image.

## Rollback

An image rollback is appropriate only when the previous relay version can use
the current database and stored data. If the upgrade applied an incompatible
migration, restore the matching pre-upgrade database, object/media, and git-data
backups as a coordinated recovery instead of rolling back only the container.

For an image-compatible rollback:

1. confirm the previous Launchpad digest and its source commit from the recorded
   pre-upgrade state;
2. ensure that exact digest is still pullable;
3. replace only `BUZZ_IMAGE` in `deploy/compose/.env` with the previous digest;
4. run:

```bash
export BUZZ_COMPOSE_TLS=true
./launchpad/deploy/run.sh check
./launchpad/deploy/run.sh upgrade
./launchpad/deploy/run.sh status
```

1. repeat the health and running-identity checks; and
2. record why the rollback occurred and which immutable digest is now running.

Do not roll back to a moving tag. Do not restore only one member of a
Postgres/object/git backup set when those components must represent the same
maintenance window.

## Development-only floating image override

The guard rejects moving tags. If a development or test environment
intentionally needs one, the operator may run:

```bash
BUZZ_ALLOW_FLOATING_IMAGE=true ./launchpad/deploy/run.sh check
```

Set the override on the actual operation as well. This is not a production
procedure. The override never permits `ghcr.io/block/buzz` or a non-Launchpad
namespace.

## Failure response

- Missing or duplicate `BUZZ_IMAGE`: correct the local `.env`; do not bypass
  the guard.
- Block or non-Launchpad image: stop and resolve the correct Launchpad workflow
  artifact.
- Floating image rejection: select a digest or full commit tag; do not set the
  override for production.
- GHCR pull or attestation failure: confirm workflow success, package access,
  and authentication without exposing credentials.
- Compose version rejection: install a supported Compose V2 release; do not
  remove the minimum-version check.
- Health or identity mismatch: preserve logs and inspection output that contain
  no secrets, stop further rollout, and escalate to the human operator.

The deployment is complete only when the configured digest, running digest,
OCI revision label, approved Git commit, workflow run, and Launchpad source URL
all agree.
