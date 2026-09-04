# Volumetric DDoS Detection 

AI-based detection module for volumetric/protocol DDoS attacks (SYN floods, with UDP reflection/amplification in progress), built as one branch of a larger unidirectional (read-only) network threat-detection pipeline.
This repo is scoped specifically to **volumetric and protocol DDoS attacks** (threat class **a** in the problem statement: SYN floods, UDP reflection/amplification, spoofed-source floods) - one of six threat-detection branches in a larger unidirectional (read-only) network threat-detection pipeline being built by the team. It does not cover C2 beaconing, DGA/DNS tunnelling, encrypted-malware detection, recon/port-scanning, or exfiltration - those are separate branches owned by other team members.

**Problem Statement:**  AI-Based Detection of Cyber Threats in Unidirectional IP Traffic
**Organization:** National Technical Research Organisation (NTRO)

## Context

This module assumes the "data diode" constraint from the problem statement: the detection system can only passively observe traffic (packet captures / flow records) and can never send probes, complete handshakes, or push mitigation actions back across the ingest path. Detection has to work purely from what crosses the wire.

## What's implemented so far - Branch A: Volumetric DDoS

- **Traffic generation & capture (Docker):** a 3-container lab (`victim`, `attacker`, `monitor`) simulating a passive monitoring setup. `monitor` shares `victim`'s network namespace and captures traffic via `tcpdump`, mirroring the read-only diode model - it observes everything to/from the victim but never talks back.
- **Feature extraction (`extract_features.py`, `windowed_features.py`):** reads pcaps with `scapy`, classifies TCP packets by flag combination (SYN-only, SYN-ACK, ACK, FIN, RST), and computes windowed features (1-second buckets) - packet rate and a SYN-only-to-completed-session ratio, which is the core signal for SYN flood detection.
- **Detection engine (`cusum_detector.py`):** a CUSUM (cumulative sum) change-point detector that learns a short baseline from early traffic, then flags sustained deviations above it. This is the "hot path" from the design - cheap, streaming-friendly, needs no training data.

### Results

Using a simulated benign baseline (15 HTTP requests over 15s) followed by a short unthrottled SYN flood (`hping3 -S --flood`):

| Metric | Benign | Flood |
|---|---|---|
| SYN-only : ACK ratio | ~0.1 | 5,000–15,000+ |
| CUSUM value | 0 (flat) | crosses alert threshold within 1 window (~1 sec) |

**Detection latency:** ~1 second from attack onset - maps to the problem statement's "bounded latency, streaming not batch" requirement.

**Note on the environment:** since the Docker attacker isn't spoofing its source IP, every SYN-ACK reply is auto-RST'd by the attacker's own kernel (it never issued a real `connect()`), so the SYN:SYN-ACK ratio alone doesn't distinguish flood from benign here - the separating signal is the SYN-only vs. completed-session (ACK/FIN) ratio and raw packet rate. Real-world spoofed attacks would show this at the SYN:SYN-ACK level directly (see planned TTL-deviation feature below).

## Repo structure
## Running the lab

\`\`\`bash
docker compose up -d --build
\`\`\`

Capture benign baseline:
\`\`\`bash
docker exec -it monitor tcpdump -i eth0 -w /captures/benign.pcap
# in a second terminal:
docker exec -it attacker sh -c 'for i in $(seq 1 15); do curl -s -o /dev/null http://victim; sleep 1; done'
\`\`\`

Capture flood traffic (keep it short - a few seconds of --flood generates a lot of packets):
\`\`\`bash
docker exec -it monitor tcpdump -i eth0 -w /captures/syn_flood.pcap
# in a second terminal:
docker exec -it attacker hping3 -S --flood -p 80 victim
\`\`\`

Run detection:
\`\`\`bash
python cusum_detector.py
\`\`\`

## Design notes

Full architecture notes (windowing scheme, shared feature layer, per-branch feature lists, fusion plan) are in the team's ideation doc - this repo implements the SYN-flood hot-path slice of that design end-to-end as a working proof of concept.

## Status / Next steps

- [x] SYN flood detection - feature extraction + CUSUM, demonstrated on real captured traffic
- [ ] UDP reflection/amplification detection (Branch B)
- [ ] TTL-baseline deviation feature (requires spoofed-source traffic to demonstrate meaningfully)
- [ ] Fusion layer (logistic regression / XGBoost) - deferred until multiple branches exist to fuse
- [ ] Standardized alert schema output
