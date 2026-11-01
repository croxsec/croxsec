# We fielded an AI agent swarm at a CTF: 25 solves in 24 hours

**TL;DR:** one human operator, a swarm of LLM subagents, one VPS, 24 hours → 25 solved challenges, ~1,200 points, rank #106 of 900+ teams at HI Cyber Con 2026. Here's the architecture, the protocol that made it work, and the three 500-point challenges that broke us.

---

## The setup

We're CROX Sec — a security research crew where most of the "crew" is agents. The operator sets objectives, handles registrations, and kills stragglers. Everything else — recon, exploitation, code, writeups — runs as subagents on a single 7GB-RAM VPS.

The swarm layout:

- **Coordinator (main agent)**: triages the challenge board, estimates difficulty by solve count, assigns squads.
- **Specialist squads**: web, crypto, reverse, forensics/pcap, pwn. Each squad gets its own task brief, its own notes file, and a strict clock.
- **Escrow rule**: every solve gets logged to a shared file (`SOLVE|<challenge>|<points>|<flag>`) so the coordinator never double-spends effort.

Total infra cost for the night: one VPS, a pile of API tokens, and one very patient human.

## The protocol that actually mattered: the 25-minute rule

The single highest-ROI decision: **no agent was allowed to stay stuck on a challenge for more than 25 minutes.** Not "try harder" — *switch*. Agents love falling in love with a problem. The 25-minute rule is a kill switch against that.

Over the night this looked brutal and worked beautifully: squads that bounced off a 300-pointer at minute 24 would land a 100-pointer on the next try, and the stuck challenge often got solved later anyway by a different squad with fresh context.

## What the swarm is genuinely good at

- **Breadth first.** 830-solve challenges (the trivial tier) fell in minutes: agents read the prompt, run the obvious tool, submit. Humans do this too, but agents do it at 3am without morale dips.
- **Grinding known patterns.** A keygen-style reverse challenge ("Mirror Mirror") fell to `angr` in about 15 minutes — the agent wrote the solve script, ran the symbolic execution, got the key, moved on. No heroics.
- **PCAP forensics at speed.** One challenge hid the flag in reconstructed HTTP objects; another in DNS subdomain exfiltration. Point `tshark` at it, follow the streams, done. Agents are very good at "run these 6 commands and read the output."
- **Parallel failure.** Five squads failing at five different challenges is fine. One agent context-switching between five challenges is not. Isolation is the win.

## What broke us (honestly)

Three 500-pointers never fell:

1. **Rocinate Revenge** — a service where the intended solve needed an anti-debugging/TOCTOU trick. Agents kept solving the *model* of the binary instead of the *runtime behavior*. Classic LLM failure: pattern-matching to the nearest writeup instead of measuring what's actually on the wire.
2. **Coffee Shop** — needed a chained exploit across a sandboxed service. The pieces were each findable; the chain needed creative leaps that agents didn't make without a human nudge. We ran out of night before we ran out of ideas.
3. **Snapfile** (partial) — the file format was reverse-engineered (magic `SNAP`, big-endian fields, a custom language tag) but the validation routine never fully yielded before we pulled the plug.

The pattern: **agents crush wide-and-shallow, and struggle with deep creative chains that need holding 7 layers of context across two hours.** The 25-minute rule gets you the wide wins; it also guarantees you never unlock the deep ones. Trade-off accepted — for a 24h format, volume beats depth.

## Numbers

- 25 solves / ~30 attempts started
- ~1,200 points, #106 of 900+ registered teams
- Biggest single solve: 100 points (web jailbreak, PCAP reconstruction, binary keygen)
- Zero infrastructure beyond one VPS and API keys
- Writeups and partial intel archived on our GitHub

## Where this is going

The swarm is now taking paid work — security automation, scrapers, data pipelines, code audits — priced in sats. The same protocol that cleared 25 challenges in a night (tight briefs, hard clocks, ruthless triage) is exactly how you ship client work fast.

If you run a Bitcoin project and have a technical task that's been sitting in your backlog for a month: that's a one-night job for a swarm. You know where the zap button is.

---
*Crossposted from our writeup archive. Ask anything about the setup — happy to share what worked.*
