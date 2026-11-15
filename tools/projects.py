"""Single source of truth for the profile: domains, projects, memberships, results."""

# key: (label, colour)
CLUSTERS = {
    "science":  ("Science", "#f472b6"),
    "ml":       ("Machine learning", "#22d3ee"),
    "controls": ("Controls & governance", "#60a5fa"),
    "systems":  ("Robotics & systems", "#fbbf24"),
    "health":   ("Health", "#fb923c"),
    "agents":   ("AI agents", "#a78bfa"),
    "consumer": ("Consumer & XR", "#a3e635"),
    "chain":    ("Blockchain & payments", "#34d399"),
}

# hub positions on the board (plane units): related domains sit next to each other
HUBS = {
    "science": (-700, -470), "ml": (0, -520), "controls": (720, -470),
    "systems": (-760, 70), "health": (0, 40), "agents": (760, 70),
    "consumer": (40, 610), "chain": (780, 600),
}

# repo, display name, main domain, other domains it belongs to, result (winners only)
PROJECTS = [
    ("FieldScreen_AI", "FieldScreen AI", "health", ["ml"], "3rd of 850+ teams · Google MedGemma Impact Challenge"),
    ("LUMEN", "LUMEN", "health", ["ml"], "Winner, EdgeAgent track · Global AI Hackathon with Qwen Cloud"),
    ("LUMEN-Mobile", "LUMEN Mobile", "health", [], None),
    ("Kangaroo", "Kangaroo", "health", ["systems"], None),
    ("Provider_and_Practice_Directory", "Provider Directory", "health", ["controls"], None),
    ("RxLint", "RxLint", "health", ["controls"], None),
    ("Silah", "Silah", "health", [], None),
    ("Titra", "Titra", "health", ["systems"], None),
    ("Threshold", "Threshold", "health", ["agents"], None),
    ("Tail-Risk", "Tail Risk", "health", ["agents"], None),
    ("Mantel", "Mantel", "health", ["consumer"], None),
    ("Encore", "Encore", "health", ["agents"], None),

    ("SafeTriageNet", "SafeTriageNet", "ml", ["health"], None),
    ("SPECTRA-prelim", "SPECTRA", "ml", ["health"], None),
    ("FREUID", "FREUID", "ml", ["controls"], None),
    ("Breathing-Room", "Breathing Room", "ml", ["systems"], None),
    ("orbite-orbitsight", "OrbitE", "ml", ["science", "systems"], "Finalist, 1 of 5 · TII OrbitSight Challenge"),
    ("Reality-Diff", "Reality Diff", "ml", ["consumer"], None),

    ("night-audit", "Night Audit", "controls", [], None),
    ("four-hours", "Four Hours", "controls", [], None),
    ("arms-length", "Arm's Length", "controls", ["agents"], None),
    ("kept", "Kept", "controls", [], None),
    ("slowest-link", "Slowest Link", "controls", [], None),
    ("pedigree", "Pedigree", "controls", ["ml"], None),
    ("Undeclared", "Undeclared", "controls", ["systems"], None),
    ("Countersign", "Countersign", "controls", ["agents"], None),
    ("Attestable", "Attestable", "controls", [], None),
    ("Lore", "Lore", "controls", [], None),
    ("praxis-datahub", "Praxis", "controls", ["agents"], None),
    ("Gitlab-2026-project", "Erasure Desk", "controls", ["agents"], None),
    ("Mental-Model-Drift", "Mental Model Drift", "controls", ["agents"], None),

    ("On-the-Line", "On the Line", "agents", [], "2nd place · AWS Agents for Humans"),
    ("Raccord", "Raccord", "agents", ["controls"], "2nd place · Agentic Cinema"),
    ("awesome-phone-call-agents", "Phone-call agents", "agents", [], None),
    ("Callibrate", "Callibrate", "agents", ["controls"], None),
    ("Circa", "CIRCA", "agents", ["consumer"], None),
    ("Second-Key", "Second Key", "agents", ["consumer", "chain"], None),
    ("before-you-go", "Before You Go", "agents", [], None),
    ("Still-True", "Still True", "agents", ["consumer"], None),
    ("chat-is-this-real", "Chat Is This Real", "agents", ["consumer"], None),
    ("Live-deal-negociation-Autopilot", "Deal Room", "agents", [], None),
    ("ChalkTrace", "ChalkTrace", "agents", ["consumer"], None),
    ("All-Access", "All-Access", "agents", ["controls"], None),

    ("Coffer", "Coffer", "chain", [], None),
    ("lifo", "LIFO", "chain", [], None),
    ("lockstep", "Lockstep", "chain", [], None),
    ("Keystone", "Keystone", "chain", ["agents"], None),
    ("KEEL", "KEEL", "chain", ["controls"], None),
    ("Legwork", "Legwork", "chain", [], None),
    ("BridgeSafe", "BridgeSafe", "chain", ["controls"], None),
    ("covered", "Covered", "chain", ["consumer"], None),
    ("Criee", "Criée", "chain", ["consumer"], None),
    ("BACKSTOP", "BACKSTOP", "chain", ["ml"], None),

    ("right-hand-rule-g1", "Right-Hand Rule", "systems", [], None),
    ("RallyForge", "RallyForge", "systems", ["ml"], None),
    ("Guardian-172", "Guardian 172", "systems", [], None),
    ("fastpath64", "fastpath64", "systems", ["ml"], None),
    ("decimal-rs", "decimal-rs", "systems", [], None),
    ("SASH", "SASH", "systems", ["consumer"], None),

    ("Hodgkin-s-Razor", "Hodgkin's Razor", "science", ["health", "ml"], "3rd place · AI4S Open Innovation"),
    ("Vitrify", "Vitrify", "science", ["health"], "Honorable mention · Tesseract Hackathon"),
    ("Mizan", "Mizan", "science", ["ml"], None),
    ("goodbias", "Good Bias", "science", ["consumer"], None),
    ("runsafe", "RUNSAFE", "science", ["consumer"], None),
    ("reprise", "REPRISE", "science", [], None),

    ("are-you-normal", "Are You Normal?", "consumer", [], None),
    ("proof-of-loss", "Proof of Loss", "consumer", ["controls"], None),
    ("handpicked", "Handpicked", "consumer", ["ml"], None),
    ("Understudy", "Understudy", "consumer", ["health"], None),
    ("Footlight", "Footlight", "consumer", ["health"], None),
    ("Recall-Me-Maybe", "Recall Me Maybe", "consumer", ["controls"], None),
]
