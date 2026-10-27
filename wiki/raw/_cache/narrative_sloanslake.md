---
type: cached-ai-output
title: "Cached report narrative — Sloan's Lake Dental"
format: json-in-markdown
---

# Cached report narrative — Sloan's Lake Dental

> Cached LLM output (generated in the build session, then checked by narrative.find_violations). Set ANTHROPIC_API_KEY to regenerate live.

Pipeline code reads the JSON block below. Edit values here and re-run the pipeline; keep it valid JSON.

```json
{
  "why_it_matters": "{business_name} runs on its patient records and its schedule, and both live on computers and email. If either is locked or stolen, the office stops and patients have to be told.",
  "scenarios": [
    {
      "key": "ransomware",
      "title": "Locked out of the schedule",
      "story": "On a Monday morning, the front desk can't open the schedule. A message on the screen says the files are locked until a ransom is paid. Patients are turned away while experts work out what was taken and how to get the system back."
    },
    {
      "key": "bec",
      "title": "The fake lab invoice",
      "story": "An email that looks exactly like it came from the dental lab says their bank changed and asks you to pay the new account. Everything looks right. The money goes to a criminal, and the real lab is still waiting to be paid."
    },
    {
      "key": "breach",
      "title": "The breach letter",
      "story": "Someone gets into an email account and copies patient files. The practice has to send letters to patients, offer them credit monitoring, answer their calls, and explain what happened to a health-privacy regulator."
    }
  ],
  "exposure_explainer": "Every email login is a door a criminal can try. {business_name} has about {email_accounts} of them. Your email already runs through an encrypted service and only approved servers may send as you, which is good. But your domain has no DMARC policy, so other mail systems aren't told to reject email pretending to be you, and you never hear about it. That doesn't mean you've been hacked; it means you'd be easier to impersonate than you need to be.",
  "next_steps": "Thanks for walking through your setup with us; most of the questions insurers ask are already answered. We'll close the few items still marked to confirm, then the insurance company confirms the final price and you sign.",
  "agent_pitch": "Dr. {owner_last}, while we're renewing your other policies, I want to show you one thing most dental offices your size are adding. You hold patient health records for thousands of families, and your whole day runs on online booking, your charting system and a handful of email logins. The most common problems we see are a ransomware lockout and a fake invoice from someone pretending to be your implant lab. Cyber insurance pays for the experts, the patient letters, the lost income, and the lawsuits if that happens. I have estimates from three insurance companies. I'd recommend the option most dental offices choose, and here's what it costs per month. We already covered most of the application on our call, so once you pick an option there are only a few loose ends.",
  "objection_tailoring": {
    "too_small": "Most cyber claims come from practices like yours, not big hospitals. The attacks are automated and look for weak email setups, and {business_name} hasn't yet told the world's mail systems to reject email pretending to be it.",
    "it_handles_it": "Your IT company makes an attack less likely. This pays for what happens if one gets through anyway: the forensics, the patient letters, the lost days, and any lawsuits. Your IT contract doesn't cover those.",
    "too_expensive": "Put the monthly cost next to what one closed day costs a practice with {dentists} dentists seeing patients. The recommended option is the one most dental offices choose.",
    "never_hacked": "Many offices find out from a patient or their bank, not from their own systems. And if you've ever caught a fake invoice before money went out, that's worth mentioning on the application; insurers see it as a sign your process works.",
    "bop_covers": "Most business and malpractice policies either exclude cyber or include only a small add-on. If you have a specific endorsement in mind, I'll have our cyber specialist compare it line by line."
  },
  "_note": "Cached LLM output, regenerated after intake was added. Checked by narrative.find_violations."
}
```
