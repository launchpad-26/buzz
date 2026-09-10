# Plan — issue #908: `governance/compatibility-policy.md`

**Issue:** launchpad-26/buzz#908 (parent PRD #619)
**Target:** `launchpad/docs/corpus/governance/compatibility-policy.md`
**Node:** id `governance-compatibility-policy`, type `governance`, status `draft`,
origin `launchpad`
**Shape:** policy node, modelled on `launchpad/docs/corpus/templates/policy.md`
(RFC 2119 MUST/SHOULD framing, derived authority, six required sections)
**Revision:** `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`

## Framing

The issue asks for a policy node about compatibility. The evidence gathering
established that **no repository-wide compatibility policy exists**. This node
therefore records the guarantees that *do* exist, surface by surface, with their
real enforcement, and names the surfaces with no rule as gaps — it does not
invent policy. Its MUST/SHOULD sections bind how a *future change* to a
compatibility surface is described and evidenced, which is authority the corpus
already holds; they do not legislate product behaviour.

Sibling boundary: #911 `governance/deprecation-policy.md` covers how a thing is
removed. This node covers what is guaranteed while it exists.

## Step 1 — Ground truth per surface (DONE during evidence gathering)

Establish, by opening the file in each case, what is guaranteed on: event kinds,
the NIP/wire surface, the relay HTTP surface, the `buzz-cli` output and exit
contract, Rust crate versions, desktop/mobile app versions, and DB migrations.

**Done-when:** every surface has either a cited rule or a recorded absence.

**Result — two briefed claims falsified, both by direct inspection:**

- "All crates share one `0.1.0` from `[workspace.package]`" is **false**.
  `crates/buzz-relay/Cargo.toml:7` sets `version = "0.2.1"` literally, and
  `buzz-persona`, `sprig` and `examples/countdown-bot` each hardcode `0.1.0`
  rather than inheriting it.
- "Only `git-sign-nostr` sets `publish = false`" is **false**.
  `examples/countdown-bot/Cargo.toml` sets it too.

**Result — one briefed claim confirmed:** no test asserts the `buzz-cli`
exit-code mapping, and its four prose copies disagree about code 1.

## Step 2 — Verify every enforcement claim before writing it

For each guarantee found in step 1, open the test, config or workflow that is
supposed to enforce it. Never restate a document's claim that a rule is enforced.

**Done-when:** each row of the enforcement table says what was opened, and the
"documented but unenforced" cases are separated from the mechanically enforced
ones.

## Step 3 — Confirm relationship targets on the merge target

`git show origin/launchpad:<path>` for every node id to be referenced.

**Done-when:** each declared `relationships[].target` was printed from
`origin/launchpad`, not from this worktree.

## Step 4 — Draft the node

Front matter against `node.schema.json`; first FACT records the revision as a
commit citation. Body follows the policy template's six required sections in
order, one level-1 `#` heading first after front matter, under 1000 lines.

**Done-when:** `python3 launchpad/project-intelligence/corpus/validate.py`
reports PASS.

## Step 5 — Gate and commit

Run the corpus unit tests bare and unpiped as the sole command in their own
invocation; confirm `OK`. Then `git add` the document and this plan and
`git commit -s`. No push, no PR.

**Done-when:** one commit exists on `task/908-governance-compatibility-policy`
containing exactly these two files.
