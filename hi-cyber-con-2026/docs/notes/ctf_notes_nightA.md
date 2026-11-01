# Blind Index — NIGHT SHIFT (subagent nightA)
CTF ended 22:00 CST; API still up. Team CROX Sec 25 kills/1393pts. Goal: solve Blind Index (286pts, id 9a82a5dd-903a-4000-bb12-5856c046e9ba) for late points / learning.

## Inherited state (from E7b predecessor)
- Oracle: POST {instance}/lookup {"texts":[...]} max 64/req. Allowance 400 TEXTS per instance (not requests!).
- Valid text: exactly 24 chars [0-9a-f]. Reference records blocked ("reference_record").
- score = cos(mean(per-(pos,char) vectors), fixed_ref). MODEL FIXED across instances.
  - s0 = score("0"*24) = -0.045231 identical on 2 instances. 88/88 single-char scores identical.
- Records PER-INSTANCE RANDOM. Old saved records useless after redeploy.
- Saved: /tmp/e7b/deltas_backup.json (168 singles, instance #1), current_data.json (173 singles, instance #2),
  val_backup.json (40 multi-char texts + additive est + true score), records_new.json (instance #2 records).
- Plan: probe singles for NEW records' features (reuse fixed-model singles where pair already probed),
  excite denominator w/ multi-char texts, fit diagonal ratio model score=(a0+Σδa)/sqrt(b0+Σδh), predict 10 scores.

## 23:46 — probing COMPLETE (all 400 lookups used)
- s0=-0.045231 ✓ (3rd instance, fixed model). Verify singles diff=0.000000 ✓
- 60 missing singles probed → all 181 features of new records now known (121 hist + 60 new)
- 275 validation texts (mutations/column-dense/splices/random) saved to /tmp/e7b/night_data.json
- Records: 5a6785fc... 7fbe451e... 149632ce... e148a311... e6ddda9d... df1030b7... fb2c3937... face17d5... 776961f9... 10215f7c...
- Next: ALS fit score=(s0+Σα)/sqrt(1+Σβ) on clean texts (features ⊆ 181), holdout-validate, predict 10 records, brute-force flag formats (free submits).
