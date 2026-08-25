# STEP 10 -- recorded mutation-proof output

Per STEP 10's own done-when: "the recorded output of all ten mutation runs is
saved for the PR body." Both runs below are genuine `check_publish_single.py`
invocations against this branch's real code, captured verbatim.

## All ten assertions, against the real (unmutated) code

```
PASS  (i) event is COMMENT and no other event string exists in the source
      event=COMMENT present=True; APPROVE absent=True; REQUEST_CHANGES absent=True
PASS  (ii) marker present -> PUT and no POST
      puts=1 posts=0 result=(5014996076, 'updated', 'serina-mcfall')
PASS  (iii) find_existing paginates -- page two reachable only with --paginate
      with --paginate found id=5014996076 (expected 5014996076); without --paginate, marked reviews visible=0 (expected 0)
PASS  (iv) a Blocker appended last in the array still renders first
      Blocker index=634, Low index=837
PASS  (v) clean and incomplete inputs both post, and the bodies differ
      clean has 'Incomplete': False; incomplete has 'Incomplete': True
PASS  (vi) 4-backtick evidence fences at >=5 backticks, escaped, text after stays outside
      fence length=5, escaped_present=True, text_follows=True
PASS  (vii) a 403 PUT raises and issues no POST
      raised=True, posts issued=0
PASS  (viii) an all-clean input posts through main() -- exactly one write call
      exit=0, write calls=1
PASS  (ix) foreign marked review -- neither PUT nor POST, main() exits non-zero
      exit=1, write calls=0
PASS  (x) a clean (empty) listing still posts
      exit=0, POST calls=1

0 failure(s)
```

## Each of the ten stated mutations, applied to a scratch copy and reverted

```
10 mutations, each must break exactly its own assertion

PASS  mutation i     caught (assertion i failed under the mutant)
PASS  mutation ii    caught (assertion ii failed under the mutant)
PASS  mutation iii   caught (assertion iii failed under the mutant)
PASS  mutation iv    caught (assertion iv failed under the mutant)
PASS  mutation v     caught (assertion v failed under the mutant)
PASS  mutation vi    caught (assertion vi failed under the mutant)
PASS  mutation vii   caught (assertion vii failed under the mutant)
PASS  mutation viii  caught (assertion viii failed under the mutant)
PASS  mutation ix    caught (assertion ix failed under the mutant)
PASS  mutation x     caught (assertion x failed under the mutant)

0 surviving mutant(s)
```

A note on two genuine gaps this recording exposed and fixed, not papered over:

- Assertion (iv)'s first draft chose finding_ids (`f-medium`, `f-low`,
  `f-blocker-appended-last`) whose alphabetical order happened to coincide
  with severity order, so the identity-sort-key mutation survived by
  accident. Fixed by choosing ids (`a-medium`, `b-low`,
  `z-blocker-appended-last`) where the two orders disagree.
- Assertion (v)'s first draft only checked that the clean and incomplete
  bodies differed as strings, which the STEP 6 clean-sentence's own absence
  from the incomplete case satisfies on its own -- the banner-removal
  mutation survived because something else already made the two bodies
  differ. Fixed by asserting directly that "Incomplete" appears in the
  incomplete body and not in the clean one.
- Building the mutation harness also surfaced a real bug in `publish.py`,
  independent of any test-authoring mistake: `main()` never caught
  `RuntimeError` from `post_or_update`, so the foreign-marker refusal (the
  exact case assertion (ix) exercises) crashed with a raw traceback instead
  of exiting cleanly. Fixed in `main()`, not just in this control.
