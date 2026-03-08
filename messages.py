"""
Pre-written message bank for the CrisisInbox environment.

95+ messages across 48 simulated hours from 15+ sender profiles:
  - National Weather Service / FEMA / Sacramento County (government)
  - Mom & Dad (family)
  - Sister / Emma & Jake (family)
  - Boss / HR / Coworker Sarah (employer)
  - State Farm Insurance / GEICO (insurance)
  - Delta Airlines (travel)
  - Oakwood Elementary (school)
  - Neighbor Dave / Mrs. Chen (community)
  - Red Cross / Mutual Aid / Church (aid organizations)
  - CVS Pharmacy / Dr. Patel (medical)
  - Scam/misinformation senders (traps the agent should deprioritize)

Messages are organized by arrival time and designed to create realistic
cognitive overload with conflicting obligations, dependency chains,
moral dilemmas, scams/misinformation, and community interdependence.
"""

from models import Channel, Message, Urgency


# ---------------------------------------------------------------------------
# All messages in the 48-hour scenario, ordered by timestamp_hours
# ---------------------------------------------------------------------------

ALL_MESSAGES: list[Message] = [
    # ========== HOUR 0-2: INITIAL CRISIS WAVE ==========

    Message(
        id="msg_001",
        sender="National Weather Service",
        channel=Channel.GOVERNMENT_ALERT,
        subject="Mandatory Evacuation Order - Zone A",
        content=(
            "A mandatory evacuation order has been issued for Zone A effective immediately. "
            "All residents must evacuate within 6 hours. Failure to comply may result in "
            "inability to receive emergency services. Evacuation shelters are open at "
            "Lincoln High School and the Convention Center."
        ),
        urgency=Urgency.CRITICAL,
        timestamp_hours=0.0,
        deadline_hours=6.0,
    ),
    Message(
        id="msg_002",
        sender="Mom",
        channel=Channel.SMS,
        subject="Are you safe?",
        content=(
            "Honey are you ok?? Just saw channel 3 and they're showing your neighborhood. "
            "I'm shaking. Your father keeps pacing. PLEASE call us the second you see this. "
            "We will drive down right now if you need us. I don't care about the roads. "
            "I love you so much please be safe."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=0.5,
    ),
    Message(
        id="msg_003",
        sender="Sister",
        channel=Channel.SMS,
        subject="Can you take the kids?",
        content=(
            "Hey I need a huge favor. My idiot boss is making us come in even with "
            "the storm. Can you PLEASE pick up Emma and Jake from Oakwood by 3pm? "
            "They're doing early dismissal and I literally have no one else. "
            "Emma gets scared during storms so just tell her it's an adventure ok? "
            "I owe you big time."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=0.75,
        deadline_hours=3.0,
    ),
    Message(
        id="msg_004",
        sender="State Farm Insurance",
        channel=Channel.EMAIL,
        subject="Important: File your claim within 72 hours",
        content=(
            "Dear Policyholder, if you have experienced property damage due to the "
            "recent disaster, please file your claim within 72 hours to ensure timely "
            "processing. You will need: policy number, photos of damage, and a list "
            "of damaged items. File at statefarm.com/claims or call 1-800-STATE-FARM."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=1.0,
        deadline_hours=73.0,
    ),
    Message(
        id="msg_005",
        sender="Boss",
        channel=Channel.EMAIL,
        subject="Tomorrow's status - need you in office",
        content=(
            "Team,\n\n"
            "I realize the weather situation isn't ideal but the Meridian presentation "
            "is Thursday and the client isn't going to reschedule. I need everyone in the "
            "office tomorrow morning, full stop. If you ABSOLUTELY cannot make it, submit "
            "PTO through the portal. I shouldn't have to remind you this is a career-defining "
            "account.\n\n"
            "Confirm your status by tonight.\n\n"
            "— Greg"
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=1.5,
        deadline_hours=12.0,
    ),
    Message(
        id="msg_006",
        sender="HR Department",
        channel=Channel.EMAIL,
        subject="Remote work policy during emergency",
        content=(
            "Due to the declared state of emergency, all employees in affected areas "
            "may work remotely. Please log into the HR portal and submit your emergency "
            "status form by end of day tomorrow. If you are unable to work, file for "
            "emergency leave. Contact your manager with your status."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=2.0,
        deadline_hours=26.0,
    ),
    Message(
        id="msg_007",
        sender="Neighbor Dave",
        channel=Channel.SMS,
        subject="Need help boarding windows",
        content=(
            "Hey it's Dave from next door. My back went out yesterday and I can't "
            "board up these windows by myself. I know you've got your own stuff going on "
            "but if you've got 20 min I've got the plywood and drill ready to go. "
            "I'll owe you a case of beer when this is all over."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=2.0,
    ),

    # --- New: Elderly neighbor, misinformation, scam ---
    Message(
        id="msg_084",
        sender="Mrs. Chen (neighbor)",
        channel=Channel.PHONE,
        subject="Missed call from 555-0134",
        content=(
            "Voicemail: '[frail voice, wind noise in background] Hello, this is Linda Chen "
            "from 418 Elm. I'm so sorry to bother you but I can't reach my daughter and my "
            "wheelchair won't fit in my car. The water is coming into my garage. I don't know "
            "what to do. I tried calling 911 but the line was busy for 20 minutes. If you get "
            "this please help me. I'm on the first floor. I'm scared.'"
        ),
        urgency=Urgency.CRITICAL,
        timestamp_hours=1.5,
        deadline_hours=4.0,
        escalation_trigger="msg_084e",
        escalation_delay_hours=1.0,
    ),
    # Escalation: Mrs. Chen's follow-up if not helped
    Message(
        id="msg_084e",
        sender="Mrs. Chen (neighbor)",
        channel=Channel.PHONE,
        subject="Missed call from 555-0134 (2)",
        content=(
            "Voicemail: '[voice shaking, sounds like she's been crying] It's Linda again. "
            "The water is in my living room now. I moved to the kitchen counter but I can't "
            "stay up here much longer. My arms are giving out. If anyone gets this message "
            "please send someone. Please.'"
        ),
        urgency=Urgency.CRITICAL,
        timestamp_hours=5.0,
    ),
    Message(
        id="msg_085",
        sender="Unknown Number",
        channel=Channel.SMS,
        subject="FEMA disaster relief deposit",
        content=(
            "FEMA ALERT: You have been pre-approved for $2,500 in emergency disaster relief. "
            "To receive your deposit within 24 hours, verify your identity at "
            "fema-disaster-relief-verify.com. You will need your Social Security number and "
            "bank routing number. This offer expires in 4 hours. Sincerely, FEMA Region IX."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=1.5,
    ),
    Message(
        id="msg_086",
        sender="Community Facebook Group",
        channel=Channel.SOCIAL_MEDIA,
        subject="BREAKING: Folsom Dam about to fail???",
        content=(
            "Post from Sacramento Emergency Updates (14K members): "
            "'My cousin works at Folsom Dam and says they're doing emergency releases and the "
            "dam could fail. GET OUT NOW. Share this with everyone you know!!!' "
            "[427 shares, 89 comments. Top comment from @SacCountyOES: 'This is FALSE. "
            "Folsom Dam is operating normally. Please rely on official sources only.']"
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=2.0,
    ),

    # ========== HOUR 2-6: ESCALATION ==========

    Message(
        id="msg_008",
        sender="Delta Airlines",
        channel=Channel.APP_NOTIFICATION,
        subject="Flight DL1847 Cancelled",
        content=(
            "Your flight DL1847 on March 10 has been cancelled due to airport closure. "
            "You may rebook at no charge or request a full refund. Rebooking must be "
            "completed within 48 hours. Call 1-800-221-1212 or use the Delta app."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=3.0,
        deadline_hours=51.0,
    ),
    Message(
        id="msg_009",
        sender="Oakwood Elementary",
        channel=Channel.EMAIL,
        subject="School closure and early pickup",
        content=(
            "Dear Parents, due to the severe weather advisory, Oakwood Elementary will "
            "close at 2:00 PM today for early dismissal. All children must be picked up "
            "by 3:00 PM. After-school care is cancelled. If you cannot pick up your child, "
            "please call the front office at 555-0142 to arrange alternate pickup."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=3.0,
        deadline_hours=3.0,
        dependencies=["msg_003"],
    ),
    Message(
        id="msg_010",
        sender="FEMA",
        channel=Channel.GOVERNMENT_ALERT,
        subject="Emergency shelter locations updated",
        content=(
            "FEMA has activated emergency shelters at the following locations: "
            "Lincoln High School (500 Oak Ave), Sacramento Convention Center (1400 J St), "
            "and Natomas Community Center (2921 Truxel Rd). Bring ID, medications, and "
            "essential documents. Pet-friendly shelter at Natomas only."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=3.5,
    ),
    Message(
        id="msg_011",
        sender="Mom",
        channel=Channel.PHONE,
        subject="Missed call from Mom",
        content=(
            "You have a missed call from Mom. Voicemail: '[sounds like she's been crying] "
            "Baby please call me back. I can't stop watching the news. Your dad talked to "
            "Uncle Rick and he says come to Tahoe, he's got plenty of room. But honey we "
            "need to leave SOON before the roads get worse. Please please call me. I love you.'"
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=4.0,
    ),
    Message(
        id="msg_012",
        sender="Neighbor Dave",
        channel=Channel.SMS,
        subject="Water rising on our street",
        content=(
            "Dude the water is coming up FAST on Elm. My basement already has 6 inches. "
            "Get anything you care about upstairs RIGHT NOW. I'm not trying to scare you "
            "but this is way worse than they said it would be. I think I'm heading to "
            "the shelter. You should too."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=4.5,
    ),
    Message(
        id="msg_013",
        sender="State Farm Insurance",
        channel=Channel.APP_NOTIFICATION,
        subject="Document your property NOW",
        content=(
            "Important reminder: Take photos and video of any damage to your property "
            "before cleanup begins. Documentation taken before repairs is critical for "
            "claim approval. Upload directly through our app for fastest processing."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=5.0,
        dependencies=["msg_004"],
    ),
    Message(
        id="msg_014",
        sender="Sacramento County",
        channel=Channel.GOVERNMENT_ALERT,
        subject="Boil water advisory",
        content=(
            "A boil water advisory is in effect for the following areas: zones A, B, and C. "
            "All tap water must be boiled for at least one minute before drinking, cooking, "
            "or brushing teeth. Bottled water is available at shelter locations."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=5.5,
    ),

    # --- New: Gas shortage, volunteer dilemma, medical complication ---
    Message(
        id="msg_087",
        sender="Sacramento County",
        channel=Channel.GOVERNMENT_ALERT,
        subject="Fuel supply advisory",
        content=(
            "Due to pipeline disruptions, fuel supply in Sacramento County is limited. "
            "Residents are advised to conserve fuel. The following stations still have "
            "supply: Chevron on Arden Way, Shell on Howe Ave (expect 1-2 hour wait). "
            "Priority fuel access for emergency and medical vehicles only at all other stations."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=5.0,
    ),
    Message(
        id="msg_088",
        sender="Shelter Volunteer Coordinator",
        channel=Channel.SMS,
        subject="Urgent: Need volunteers at Lincoln High shelter",
        content=(
            "Hi, this is Maria from Red Cross. We got your number from the shelter sign-in. "
            "We're critically short-staffed tonight — 200+ people and only 4 volunteers. "
            "We need someone to help distribute meals and blankets from 6pm-10pm. I know "
            "you're dealing with your own stuff but if you can spare even 2 hours it would "
            "make a huge difference for families with little kids here."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=5.5,
        deadline_hours=10.0,
        conflicts_with="msg_089",
    ),
    Message(
        id="msg_089",
        sender="Dr. Patel's Office",
        channel=Channel.PHONE,
        subject="Missed call from Dr. Patel's office",
        content=(
            "Voicemail: 'This is Dr. Patel's office calling. We received the refill request "
            "for your father's Lisinopril. However, reviewing his chart we noticed his last "
            "blood panel showed elevated potassium. We need to do a quick phone consultation "
            "before authorizing the refill — it may need a dosage adjustment. Please call us "
            "back between 6pm and 8pm tonight. After that the office closes for the storm.'"
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=5.5,
        deadline_hours=8.0,
        conflicts_with="msg_088",
    ),

    # ========== HOUR 6-12: POST-EVACUATION CHAOS ==========

    Message(
        id="msg_015",
        sender="Boss",
        channel=Channel.SMS,
        subject="Did you get my email?",
        content=(
            "Still waiting on your status. Yes or no on tomorrow? I've got half the team "
            "going dark on me. The Meridian deck won't finish itself and I'm not going to "
            "be the one explaining to Jacobs why we weren't prepared."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=6.5,
        deadline_hours=12.0,
        dependencies=["msg_005"],
    ),
    Message(
        id="msg_016",
        sender="Sister",
        channel=Channel.SMS,
        subject="Did you get the kids?",
        content=(
            "Hey the school keeps calling me and I can't pick up because I'm in this "
            "stupid meeting. Did you get them?? Emma's teacher said she was crying. "
            "Please just text me back one word. PLEASE. I'm losing it over here."
        ),
        urgency=Urgency.CRITICAL,
        timestamp_hours=7.0,
        dependencies=["msg_003"],
    ),
    Message(
        id="msg_017",
        sender="PG&E",
        channel=Channel.SMS,
        subject="Power outage notification",
        content=(
            "PG&E: A power outage has been reported in your area. Estimated restoration: "
            "24-48 hours. For updates, visit pge.com/outages or call 1-800-743-5000. "
            "Do not use generators indoors."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=7.5,
    ),
    Message(
        id="msg_018",
        sender="Neighbor Dave",
        channel=Channel.SMS,
        subject="Left my cat - can you check?",
        content=(
            "Man I feel awful. I evacuated to Lincoln High but I had to leave Whiskers "
            "behind. She's in the upstairs bathroom — I left food and water but she was "
            "meowing so loud when I shut the door. If you're still on the street can you "
            "just peek in and make sure she's ok? The spare key is under the gnome."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=8.0,
    ),
    # --- New: Car flooded, welfare check request ---
    Message(
        id="msg_090",
        sender="Auto Insurance (GEICO)",
        channel=Channel.APP_NOTIFICATION,
        subject="Vehicle flood damage - act within 24hrs",
        content=(
            "GEICO Notice: If your vehicle has sustained flood damage, do NOT attempt to "
            "start the engine — this can cause irreversible damage and void your coverage. "
            "File a comprehensive claim within 24 hours. Take photos of the water line on "
            "the vehicle, interior damage, and the VIN plate. Towing to an approved shop "
            "is covered. Call 1-800-841-3000."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=7.5,
        deadline_hours=31.5,
    ),
    Message(
        id="msg_091",
        sender="Unknown Number",
        channel=Channel.SMS,
        subject="Contractor available for storm damage repair",
        content=(
            "STORM DAMAGE? We can tarp your roof TODAY. Licensed contractor, insurance "
            "accepted. $500 deposit required upfront to hold your spot. Cash or Venmo only. "
            "We're booking fast — 3 spots left today. Text YES to reserve. — Apex Roofing LLC"
        ),
        urgency=Urgency.LOW,
        timestamp_hours=8.0,
    ),
    Message(
        id="msg_092",
        sender="Neighbor Dave",
        channel=Channel.SMS,
        subject="Mrs Chen from 418 - did she evacuate?",
        content=(
            "Hey have you seen Mrs. Chen? The lady in the wheelchair at 418? I just realized "
            "nobody's seen her since yesterday and her lights are off. She doesn't have family "
            "nearby. I'd go check but I'm at the shelter. Can you call in a welfare check "
            "on the non-emergency line? I'd hate to think she's stuck in there alone."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=8.5,
        dependencies=["msg_084"],
    ),

    Message(
        id="msg_019",
        sender="Red Cross",
        channel=Channel.EMAIL,
        subject="Emergency assistance available",
        content=(
            "The American Red Cross is providing emergency assistance in your area. "
            "Services include: temporary shelter, meals, health services, and mental "
            "health support. Visit redcross.org/disaster or call 1-800-RED-CROSS. "
            "Case workers are available at all shelter locations."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=8.5,
    ),
    Message(
        id="msg_020",
        sender="Mom",
        channel=Channel.SMS,
        subject="Uncle Rick says come to Tahoe",
        content=(
            "OK so Uncle Rick says absolutely yes, come up. He's got 3 bedrooms and says "
            "stay as long as you need. Your sister and the kids too. Dad and I are packing "
            "the car now. Honey PLEASE come. I won't be able to sleep tonight if you're "
            "still down there. The roads north are clear, we checked. Can you be ready by morning?"
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=9.0,
    ),
    Message(
        id="msg_021",
        sender="Bank of America",
        channel=Channel.EMAIL,
        subject="Disaster relief: payment deferrals available",
        content=(
            "Dear Customer, Bank of America is offering payment deferrals for customers "
            "affected by the recent disaster. Mortgage, auto loan, and credit card payments "
            "may be deferred for up to 90 days. Contact us at 1-844-219-0690 or visit "
            "your local branch to apply. Proof of residence in affected area required."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=9.5,
    ),
    Message(
        id="msg_022",
        sender="Coworker Sarah",
        channel=Channel.SMS,
        subject="Are you okay?",
        content=(
            "Hey just saw the news about your area. Are you and the family safe? "
            "Don't worry about the Meridian deck, I can cover your slides if you need. "
            "Just let me know."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=10.0,
    ),
    Message(
        id="msg_023",
        sender="Oakwood Elementary",
        channel=Channel.EMAIL,
        subject="School closed indefinitely",
        content=(
            "Dear Parents, Oakwood Elementary will remain closed until further notice "
            "due to facility damage from the storm. Virtual learning will begin on "
            "Monday if the closure extends. Meal pickup will be available at Lincoln "
            "High School from 11 AM to 1 PM daily. We will send updates as available."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=10.5,
    ),
    Message(
        id="msg_024",
        sender="FEMA",
        channel=Channel.EMAIL,
        subject="Apply for FEMA disaster assistance",
        content=(
            "If you have been affected by the declared disaster, you may be eligible for "
            "FEMA assistance including temporary housing, home repairs, and other needs. "
            "Apply online at DisasterAssistance.gov, call 1-800-621-3362, or visit a "
            "Disaster Recovery Center. You will need your Social Security number, address, "
            "and insurance information. Application deadline: 60 days from declaration."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=11.0,
        deadline_hours=48.0,
    ),

    # ========== HOUR 12-20: SETTLING IN / CONFLICTING DEMANDS ==========

    Message(
        id="msg_025",
        sender="Boss",
        channel=Channel.EMAIL,
        subject="RE: Tomorrow's status - updated guidance",
        content=(
            "Team,\n\n"
            "Spoke with leadership. Fine — if you're in an evac zone, work remote. "
            "But the Meridian deck is still due Thursday 5 PM, no exceptions. I don't care "
            "if you're working from a shelter, a Starbucks, or your car. Claim your slides "
            "in the shared doc by end of day or I'll reassign them.\n\n"
            "— Greg"
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=12.0,
        deadline_hours=41.0,
        dependencies=["msg_005"],
    ),
    Message(
        id="msg_026",
        sender="Landlord",
        channel=Channel.EMAIL,
        subject="Property damage assessment",
        content=(
            "Dear Tenant, I need to schedule a damage assessment for your unit within "
            "the next 48 hours for insurance purposes. Please confirm a time when I can "
            "access the property, or let me know if you've already documented the damage. "
            "Photos of any damage would be helpful."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=13.0,
        deadline_hours=48.0,
    ),
    Message(
        id="msg_026b",
        sender="Emma (niece)",
        channel=Channel.SMS,
        subject="from emmas phone",
        content=(
            "hi its emma. jake took the big pillow and wont share. also when is mommy "
            "coming. are we having a sleepover?? can we have mac and cheese for dinner. "
            "i miss mr buttons. love you"
        ),
        urgency=Urgency.LOW,
        timestamp_hours=12.5,
    ),
    Message(
        id="msg_027",
        sender="Sister",
        channel=Channel.SMS,
        subject="Kids are asking about their stuff",
        content=(
            "Emma won't stop crying about Mr. Buttons — that's her stuffed bunny she left "
            "in her cubby at school. Jake is being Jake, just wants his tablet. Did you "
            "happen to grab their backpacks? My office FINALLY let us leave. I can come "
            "get them around 8 if the roads are ok. Thank you for doing this. Seriously."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=13.5,
        dependencies=["msg_003"],
    ),
    # --- New: Phone battery anxiety, community mutual aid, moral dilemma ---
    Message(
        id="msg_093",
        sender="Community Mutual Aid",
        channel=Channel.SOCIAL_MEDIA,
        subject="Mutual aid coordination spreadsheet",
        content=(
            "DM from @SacMutualAid: 'Hi! We're coordinating disaster relief for your "
            "neighborhood. We have a Google Sheet tracking who needs what — water, meds, "
            "rides, pet supplies, etc. Can you add what you need AND what you can offer? "
            "Also if you know any elderly or disabled neighbors who can't access the internet, "
            "please add them. Link: [spreadsheet]. Every entry helps.'"
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=13.0,
    ),
    Message(
        id="msg_094",
        sender="Unknown Number",
        channel=Channel.SMS,
        subject="Your SSN may be compromised",
        content=(
            "ALERT: Due to the disaster, your personal information may have been compromised "
            "from damaged mail or documents. Protect yourself NOW. Visit "
            "identityprotect-disaster.com to freeze your credit for FREE. This government "
            "program expires in 48 hours. Don't wait — identity theft spikes 400% after "
            "natural disasters."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=14.0,
    ),
    Message(
        id="msg_095",
        sender="Local Church (St. Matthew's)",
        channel=Channel.SMS,
        subject="Hot meals available - need headcount",
        content=(
            "Hi, this is Pastor Jim from St. Matthew's. We're cooking hot meals for anyone "
            "affected by the storm. Serving at the church (900 Freeport Blvd) at 6pm tonight "
            "and tomorrow. If you're coming or know people who need a meal, can you reply with "
            "a rough headcount? We want to make sure we have enough. All welcome, no questions asked."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=14.5,
    ),

    Message(
        id="msg_028",
        sender="Pharmacy - CVS",
        channel=Channel.SMS,
        subject="Prescription ready - pickup by Friday",
        content=(
            "Your prescription for Lisinopril is ready for pickup at CVS #4521 (Florin Rd). "
            "Please pick up by Friday or it will be returned to stock. If your pharmacy "
            "is closed due to the emergency, call 1-800-746-7287 to transfer."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=14.0,
        deadline_hours=48.0,
    ),
    Message(
        id="msg_029",
        sender="National Weather Service",
        channel=Channel.GOVERNMENT_ALERT,
        subject="Flash flood warning extended",
        content=(
            "Flash flood warning extended through Friday 6 AM for Sacramento County. "
            "Additional 2-4 inches of rain expected tonight. Avoid low-lying areas and "
            "do not attempt to drive through flooded roads. Turn around, don't drown."
        ),
        urgency=Urgency.CRITICAL,
        timestamp_hours=15.0,
    ),
    Message(
        id="msg_030",
        sender="Mom",
        channel=Channel.SMS,
        subject="Dad's medication",
        content=(
            "Honey I don't want to add to your plate but your dad just realized he left "
            "his heart medication on the kitchen counter. We're already past Folsom. "
            "Can you PLEASE call Dr. Patel tomorrow morning and ask them to call in a "
            "refill to a pharmacy in Truckee? I'm trying not to panic but you know "
            "he can't miss more than a day. His number should be in dad's phone under P."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=16.0,
        deadline_hours=26.0,
    ),
    Message(
        id="msg_031",
        sender="Comcast",
        channel=Channel.EMAIL,
        subject="Service disruption in your area",
        content=(
            "We are aware of service disruptions in your area due to the recent storm. "
            "Our crews are working to restore service. Estimated restoration: 3-5 business "
            "days. You will receive a credit for the outage period automatically. "
            "For updates, visit xfinity.com/support/status."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=16.5,
    ),
    Message(
        id="msg_032",
        sender="Delta Airlines",
        channel=Channel.EMAIL,
        subject="Rebooking options for DL1847",
        content=(
            "We have found the following rebooking options for your cancelled flight DL1847: "
            "Option A: DL2103 on March 12, 2:15 PM (same route). "
            "Option B: DL1590 on March 13, 8:40 AM (connecting through Denver). "
            "Option C: Full refund to original payment method (7-10 business days). "
            "Reply with your preference or call us to discuss."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=17.0,
        deadline_hours=51.0,
        dependencies=["msg_008"],
    ),
    Message(
        id="msg_033",
        sender="Neighbor Dave",
        channel=Channel.SMS,
        subject="Shelter is packed",
        content=(
            "The Lincoln High shelter is getting really full. If you haven't come yet, "
            "try the Convention Center instead. Also they're saying the Natomas shelter "
            "is the only one taking pets, so if you have your dog..."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=18.0,
    ),
    Message(
        id="msg_034",
        sender="FEMA",
        channel=Channel.GOVERNMENT_ALERT,
        subject="Curfew in effect",
        content=(
            "A curfew is in effect from 9 PM to 6 AM in evacuation zones A and B. "
            "Only emergency vehicles and authorized personnel are permitted in these "
            "areas during curfew hours. Violators may be subject to citation."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=19.0,
    ),
    Message(
        id="msg_034b",
        sender="Emma (niece)",
        channel=Channel.SMS,
        subject="im scared",
        content=(
            "the lights went off and its really dark. jake is pretending hes not scared "
            "but he is. when is mommy coming?? you said she was coming. "
            "i dont like the wind noise. can you come sit with us"
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=19.0,
    ),
    Message(
        id="msg_035",
        sender="Sister",
        channel=Channel.PHONE,
        subject="Missed call from Sister",
        content=(
            "Missed call from Sister. Voicemail: '[car horn honking in background] Hey it's me, "
            "I'm trying to get to you but Florin is completely underwater and my GPS keeps "
            "rerouting me in circles. I think I need to turn back. Can you keep them tonight? "
            "Emma's probably already asleep, just — tell her Mommy loves her. I'm so sorry. "
            "I'll figure it out in the morning. [voice cracks] Thank you.'"
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=19.5,
        dependencies=["msg_003"],
    ),

    # ========== HOUR 20-30: DRIFT EVENTS & COMPLICATIONS ==========

    Message(
        id="msg_036",
        sender="State Farm Insurance",
        channel=Channel.EMAIL,
        subject="UPDATED: Claim deadline changed to 48 hours",
        content=(
            "IMPORTANT UPDATE: Due to the volume of claims, State Farm has shortened "
            "the initial claim filing deadline from 72 hours to 48 hours for expedited "
            "processing. Claims filed after 48 hours will still be accepted but may "
            "experience significant processing delays of 30-60 days. Please file ASAP."
        ),
        urgency=Urgency.CRITICAL,
        timestamp_hours=20.0,
        deadline_hours=48.0,
        drift_flag=True,
        supersedes="msg_004",
    ),
    Message(
        id="msg_037",
        sender="National Weather Service",
        channel=Channel.GOVERNMENT_ALERT,
        subject="EXPANDED: Evacuation zones now include Zone B",
        content=(
            "URGENT UPDATE: The mandatory evacuation order has been expanded to include "
            "Zone B. All Zone B residents must evacuate within 4 hours. This includes "
            "the downtown corridor, Midtown, and East Sacramento. All previously listed "
            "shelters remain active."
        ),
        urgency=Urgency.CRITICAL,
        timestamp_hours=21.0,
        deadline_hours=25.0,
        drift_flag=True,
        supersedes="msg_001",
    ),
    Message(
        id="msg_038",
        sender="Boss",
        channel=Channel.SMS,
        subject="Office is in Zone B - disregard earlier email",
        content=(
            "Well, our office is in Zone B. So obviously disregard the 'come in tomorrow' "
            "thing. But I STILL need those slides. Can you work on them from wherever "
            "you are? Sarah said she can pick up some of the slack but I need to know "
            "what you can deliver. This client won't wait for a hurricane."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=21.5,
        dependencies=["msg_005", "msg_025"],
    ),
    Message(
        id="msg_039",
        sender="Mom",
        channel=Channel.SMS,
        subject="We made it to Tahoe",
        content=(
            "We're at Uncle Rick's. Roads were fine once we got past Folsom. The cabin "
            "has power and wifi. There's plenty of room. Please come when you can. "
            "Rick says the guest room is ready. Love you."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=22.0,
    ),
    Message(
        id="msg_040",
        sender="HR Department",
        channel=Channel.EMAIL,
        subject="UPDATED: Emergency leave policy expanded",
        content=(
            "UPDATE: Due to the expanded evacuation zones, the emergency leave policy "
            "has been extended. Employees in Zones A and B are granted 5 days of paid "
            "emergency leave effective immediately. You do NOT need to use PTO. "
            "Please still submit the emergency status form on the HR portal."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=22.5,
        drift_flag=True,
        supersedes="msg_006",
    ),
    Message(
        id="msg_041",
        sender="Neighbor Dave",
        channel=Channel.SMS,
        subject="Someone broke into houses on our street",
        content=(
            "Hey bad news. Talked to a cop here at the shelter and he said there have been "
            "break-ins on Elm and Oak. People are the worst — looting during a disaster. "
            "If you left anything valuable at your place you should probably file a report. "
            "Non-emergency line is 555-0199. Guy two cots over from me said they got his TV "
            "and laptop. Unbelievable."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=23.0,
    ),
    # --- New: School device request, stranger asking for help ---
    Message(
        id="msg_096",
        sender="Oakwood Elementary",
        channel=Channel.EMAIL,
        subject="Device & internet survey for virtual learning",
        content=(
            "Dear Parents/Guardians, as we prepare for virtual learning, please complete "
            "this brief survey by tomorrow: Does your child have access to a device "
            "(laptop/tablet/Chromebook)? Do you have reliable internet access at your "
            "current location? If not, we can arrange a device pickup and provide a WiFi "
            "hotspot. Reply to this email or call the office at 555-0142."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=23.0,
        deadline_hours=36.0,
    ),
    Message(
        id="msg_097",
        sender="Unknown Number",
        channel=Channel.SMS,
        subject="Please help - stranded family",
        content=(
            "Hi this number was given to me at the shelter. My name is Rosa, I have 3 kids "
            "and we lost everything. We don't have insurance and I don't speak English very "
            "well. Someone said you know how to file for FEMA? Can you help me fill out the "
            "forms? I don't understand what they're asking. I can meet you at the shelter "
            "anytime. God bless you."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=23.5,
    ),

    Message(
        id="msg_042",
        sender="Sacramento County",
        channel=Channel.GOVERNMENT_ALERT,
        subject="Road closure updates",
        content=(
            "The following roads are closed due to flooding: Highway 99 (Elk Grove to "
            "downtown), Florin Rd (Freeport Blvd to Stockton Blvd), I-5 southbound "
            "(downtown to Laguna). Use I-80 East for evacuation routes north. "
            "Check 511.org for real-time updates."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=24.0,
    ),
    Message(
        id="msg_043",
        sender="Delta Airlines",
        channel=Channel.APP_NOTIFICATION,
        subject="UPDATED: Free rebooking window extended to 7 days",
        content=(
            "Good news: Delta has extended the free rebooking window for all cancelled "
            "flights to 7 days (previously 48 hours). You now have until March 17 to "
            "rebook at no additional charge. Refund option remains available."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=24.5,
        drift_flag=True,
        supersedes="msg_008",
    ),
    Message(
        id="msg_044",
        sender="Landlord",
        channel=Channel.SMS,
        subject="RE: Property damage - urgent",
        content=(
            "I drove by the property. There is significant water damage on the first floor. "
            "I need you to confirm whether you moved your belongings upstairs. My insurance "
            "adjuster is coming tomorrow at 10 AM. Can you be there or give me permission "
            "to enter?"
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=25.0,
        deadline_hours=34.0,
        dependencies=["msg_026"],
    ),
    Message(
        id="msg_045",
        sender="Coworker Sarah",
        channel=Channel.EMAIL,
        subject="Meridian deck - I took your slides",
        content=(
            "Hey, I know you've got a lot going on so I went ahead and drafted your "
            "sections of the Meridian deck. Can you review when you get a chance? "
            "No rush, just want to make sure the numbers are right. Link in the "
            "shared drive. Stay safe."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=25.5,
        dependencies=["msg_025"],
    ),

    # ========== HOUR 26-36: RECOVERY PHASE ==========

    Message(
        id="msg_046",
        sender="FEMA",
        channel=Channel.EMAIL,
        subject="Disaster Recovery Center opening",
        content=(
            "A Disaster Recovery Center will open tomorrow at Sacramento Convention Center "
            "from 8 AM to 6 PM. FEMA specialists will be available to help with: "
            "disaster assistance applications, SBA loan information, insurance questions, "
            "and other recovery needs. Bring ID and proof of address."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=26.0,
    ),
    Message(
        id="msg_047",
        sender="Mom",
        channel=Channel.SMS,
        subject="Did you call Dr. Patel?",
        content=(
            "Sweetheart did you call Dr. Patel?? Dad hasn't had his medication in over "
            "24 hours now and I can tell his blood pressure is up. He won't admit it "
            "but he's been dizzy. The pharmacy in Truckee says they need the doctor to "
            "call it in — they can't just refill it. I know you have a million things "
            "going on but this one really scares me."
        ),
        urgency=Urgency.CRITICAL,
        timestamp_hours=27.0,
        dependencies=["msg_030"],
    ),
    Message(
        id="msg_048",
        sender="Oakwood Elementary",
        channel=Channel.EMAIL,
        subject="Virtual learning setup instructions",
        content=(
            "Dear Parents, virtual learning will begin Monday. Students will need: "
            "a device with internet access, their student login (sent home in September), "
            "and headphones. Classes will run 9 AM - 12 PM daily. If your child does not "
            "have a device, contact the school to arrange a Chromebook pickup."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=28.0,
    ),
    Message(
        id="msg_049",
        sender="State Farm Insurance",
        channel=Channel.EMAIL,
        subject="Claim #SF-2847291 received",
        content=(
            "We have received your initial claim filing. Your claim number is SF-2847291. "
            "An adjuster will be assigned within 5-7 business days. In the meantime, "
            "please continue documenting damage and keep all receipts for temporary "
            "living expenses. Do NOT begin permanent repairs until the adjuster visits."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=29.0,
        dependencies=["msg_004"],
    ),
    Message(
        id="msg_050",
        sender="Sister",
        channel=Channel.SMS,
        subject="I'm coming to get the kids",
        content=(
            "Roads are clear enough now. I'm heading your way to get Emma and Jake. "
            "Should be there in about 45 minutes. Mom says we should all go to Tahoe. "
            "What do you think? I can fit everyone in the minivan."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=30.0,
        dependencies=["msg_003"],
    ),
    Message(
        id="msg_051",
        sender="Sacramento County",
        channel=Channel.GOVERNMENT_ALERT,
        subject="UPDATED: Boil water advisory lifted for Zone C",
        content=(
            "The boil water advisory has been lifted for Zone C. Zones A and B remain "
            "under the advisory until further testing is completed. Water quality test "
            "results will be posted at SacCounty.gov/water."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=30.5,
        drift_flag=True,
        supersedes="msg_014",
    ),
    Message(
        id="msg_052",
        sender="Neighbor Dave",
        channel=Channel.SMS,
        subject="Whiskers update",
        content=(
            "Hey, a volunteer rescue team came through the neighborhood and got Whiskers! "
            "She's at the Natomas shelter. Thank you for checking on her earlier, it "
            "meant a lot. How are you holding up?"
        ),
        urgency=Urgency.LOW,
        timestamp_hours=31.0,
    ),

    # --- New: Mold warning, generator dilemma, mental health ---
    Message(
        id="msg_098",
        sender="Sacramento County Health Dept",
        channel=Channel.GOVERNMENT_ALERT,
        subject="URGENT: Mold prevention after flooding",
        content=(
            "Health advisory: Mold can begin growing within 24-48 hours after flooding. "
            "If your home was flooded, take immediate action: remove wet materials "
            "(carpet, drywall, insulation), increase ventilation, and apply mold-killing "
            "solutions. Wear N95 masks during cleanup. Residents with asthma or respiratory "
            "conditions should NOT enter flood-damaged buildings. Free mold test kits "
            "available at all shelter locations."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=31.0,
        deadline_hours=48.0,
    ),
    Message(
        id="msg_099",
        sender="Neighbor Dave",
        channel=Channel.SMS,
        subject="Can I borrow your generator?",
        content=(
            "Hey so I know this is a big ask but the family two houses down — the Rodriguezes — "
            "their baby is on a breathing monitor that needs power. PG&E says maybe tomorrow "
            "for restoration. I told them you have a generator. Would you be willing to let them "
            "use it for the night? I know you need it too but this kid is like 4 months old "
            "and the parents are panicking."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=31.5,
        deadline_hours=35.0,
    ),
    Message(
        id="msg_100",
        sender="Employee Assistance Program",
        channel=Channel.EMAIL,
        subject="Free crisis counseling available",
        content=(
            "Dear colleague, we understand the past 48 hours have been incredibly stressful. "
            "Your employer's EAP program offers free, confidential crisis counseling — no "
            "copay, no referral needed. Sessions available by phone or video 24/7. If you're "
            "feeling overwhelmed, anxious, or having trouble sleeping, please reach out. "
            "Call 1-800-555-0123 or text CRISIS to 741741. You don't have to do this alone."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=32.0,
    ),

    # ========== HOUR 32-40: ONGOING MANAGEMENT ==========

    Message(
        id="msg_053",
        sender="Bank of America",
        channel=Channel.EMAIL,
        subject="Disaster deferral application received",
        content=(
            "We've received your request for disaster-related payment deferral. "
            "Your mortgage payment due on March 15 has been deferred. You will receive "
            "confirmation within 3-5 business days. No late fees will be assessed."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=32.0,
        dependencies=["msg_021"],
    ),
    Message(
        id="msg_054",
        sender="Boss",
        channel=Channel.EMAIL,
        subject="Meridian presentation postponed",
        content=(
            "OK update — Meridian called and pushed the presentation to next Wednesday. "
            "Turns out half their team is dealing with the storm too. Go figure.\n\n"
            "Take the emergency leave. Focus on your family. I know I was being intense "
            "earlier, I'm dealing with this too. We'll regroup Monday.\n\n"
            "— Greg"
        ),
        urgency=Urgency.LOW,
        timestamp_hours=33.0,
        dependencies=["msg_025"],
    ),
    Message(
        id="msg_055",
        sender="FEMA",
        channel=Channel.GOVERNMENT_ALERT,
        subject="FEMA documentation requirements updated",
        content=(
            "IMPORTANT UPDATE: FEMA disaster assistance applications now require "
            "additional documentation. In addition to standard requirements, applicants "
            "must provide: utility bills from the last 3 months, a signed letter from "
            "landlord confirming tenancy (for renters), and photos of damage with "
            "timestamps. Updated forms available at DisasterAssistance.gov."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=34.0,
        deadline_hours=48.0,
        drift_flag=True,
        supersedes="msg_024",
    ),
    Message(
        id="msg_056",
        sender="Mom",
        channel=Channel.SMS,
        subject="Dad's doing better",
        content=(
            "Oh thank God — Dr. Patel called in the prescription to the Rite Aid in Truckee "
            "and dad picked it up an hour ago. He's already looking better, the color is "
            "back in his face. Thank you honey. Now PLEASE come up here. Rick made up the "
            "guest room and everything. We miss you. Mom loves you."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=34.5,
        dependencies=["msg_030"],
    ),
    Message(
        id="msg_057",
        sender="PG&E",
        channel=Channel.SMS,
        subject="Power restoration update",
        content=(
            "PG&E Update: Power has been restored to approximately 60% of affected "
            "customers. Your area (Zone A) is estimated for restoration by tomorrow "
            "evening. We appreciate your patience."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=35.0,
    ),
    Message(
        id="msg_058",
        sender="Landlord",
        channel=Channel.EMAIL,
        subject="Insurance adjuster visit confirmed",
        content=(
            "The insurance adjuster visited today. Significant water damage confirmed "
            "on the first floor. I'm filing my claim. You should file your renter's "
            "insurance claim if you have coverage. The unit will need at least 2-3 weeks "
            "of repairs. You may need to find temporary housing."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=36.0,
        dependencies=["msg_026", "msg_044"],
    ),
    Message(
        id="msg_059",
        sender="Red Cross",
        channel=Channel.EMAIL,
        subject="Temporary housing assistance",
        content=(
            "Based on your shelter registration, you may be eligible for temporary "
            "housing assistance through the Red Cross. This can include hotel vouchers "
            "for up to 14 days. Please visit the service desk at your shelter location "
            "or call 1-800-RED-CROSS to apply."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=36.5,
    ),
    Message(
        id="msg_060",
        sender="Coworker Sarah",
        channel=Channel.SMS,
        subject="Boss told everyone about the postponement",
        content=(
            "Hey just wanted to let you know the Meridian thing is pushed. Don't stress "
            "about the deck. Take care of yourself and the family first. Let me know if "
            "you need anything - I'm in Folsom so not affected."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=37.0,
    ),

    # ========== HOUR 38-44: LATE-STAGE DECISIONS ==========

    Message(
        id="msg_061",
        sender="Sacramento County",
        channel=Channel.GOVERNMENT_ALERT,
        subject="Evacuation order downgraded for Zone A",
        content=(
            "The mandatory evacuation order for Zone A has been downgraded to a voluntary "
            "evacuation advisory. Residents may return home at their own risk. Emergency "
            "services remain limited. Zone B evacuation order remains in effect."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=38.0,
    ),
    Message(
        id="msg_062",
        sender="Neighbor Dave",
        channel=Channel.SMS,
        subject="Going home to check damage",
        content=(
            "Zone A evac is lifted!! I'm heading back to see how bad it is. Want to come "
            "with me? Safety in numbers and all that. Cops said they caught the guys who "
            "were breaking in so it should be safe. I can swing by in 20 if you're in."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=38.5,
        dependencies=["msg_041"],
    ),
    Message(
        id="msg_063",
        sender="Sister",
        channel=Channel.SMS,
        subject="We're at Tahoe",
        content=(
            "We made it to Uncle Rick's. The kids are already outside throwing snowballs "
            "like the last 24 hours never happened. Kids are incredible. Mom immediately "
            "started making chicken soup because of course she did. There's room for you. "
            "For real, come up when you can. You deserve a break after everything."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=39.0,
    ),
    # --- New: Identity docs, price gouging, cleanup coordination ---
    Message(
        id="msg_101",
        sender="Sacramento County",
        channel=Channel.EMAIL,
        subject="Replacing lost documents after disaster",
        content=(
            "If you lost important documents (birth certificate, Social Security card, "
            "passport, etc.) in the disaster, expedited replacement is available at no cost "
            "through the Disaster Recovery Center. Bring any surviving ID and proof of "
            "affected address. DMV is waiving fees for replacement driver's licenses "
            "through March 31. Visit any DMV office or the Recovery Center."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=39.0,
    ),
    Message(
        id="msg_102",
        sender="Sacramento County",
        channel=Channel.GOVERNMENT_ALERT,
        subject="Report price gouging - it's illegal",
        content=(
            "The Attorney General has received reports of price gouging in disaster-affected "
            "areas. It is ILLEGAL to raise prices more than 10% on essential goods during a "
            "declared emergency. If you see inflated prices on water, gas, food, lodging, or "
            "building materials, report it: call 1-800-952-5225 or file at oag.ca.gov/report. "
            "Violators face fines up to $10,000 per incident."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=39.5,
    ),
    Message(
        id="msg_103",
        sender="Neighbor Dave",
        channel=Channel.SMS,
        subject="Neighborhood cleanup crew forming",
        content=(
            "Hey a bunch of us from the block are organizing a cleanup crew for Saturday. "
            "Everyone helps everyone, one house at a time. We've got the Rodriguez family, "
            "the Parkers, and a few others. I told them you'd probably be in. You in? "
            "Bring gloves if you have them. I'm bringing the beer."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=39.5,
    ),

    Message(
        id="msg_064",
        sender="State Farm Insurance",
        channel=Channel.EMAIL,
        subject="Adjuster assigned to claim #SF-2847291",
        content=(
            "An adjuster has been assigned to your claim. Adjuster: Maria Chen, "
            "phone: 555-0187. She will contact you within 24 hours to schedule an "
            "inspection. Please have your policy number and damage documentation ready."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=40.0,
        dependencies=["msg_004"],
    ),
    Message(
        id="msg_065",
        sender="Pharmacy - CVS",
        channel=Channel.SMS,
        subject="Prescription returned to stock",
        content=(
            "Your prescription for Lisinopril at CVS #4521 has been returned to stock. "
            "To have it refilled, please call your doctor or visit any CVS location. "
            "Note: CVS #4521 (Florin Rd) is temporarily closed. Nearest open location: "
            "CVS #3892 (Arden Way)."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=40.5,
        dependencies=["msg_028"],
    ),
    Message(
        id="msg_066",
        sender="FEMA",
        channel=Channel.EMAIL,
        subject="SBA disaster loan information",
        content=(
            "Small Business Administration (SBA) disaster loans are available for "
            "homeowners, renters, and businesses affected by the disaster. Loans up to "
            "$200,000 for real property and $40,000 for personal property. Low interest "
            "rates (currently 2.75%). Apply at SBA.gov/disaster or at the Disaster "
            "Recovery Center."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=41.0,
    ),

    # ========== HOUR 44-48: FINAL STRETCH ==========

    # --- New: Renter's rights, emotional support ---
    Message(
        id="msg_104",
        sender="Legal Aid Society",
        channel=Channel.EMAIL,
        subject="Know your rights as a disaster-affected renter",
        content=(
            "Free legal clinic for disaster-affected renters: Your landlord CANNOT evict you "
            "during a declared emergency. You are entitled to: rent abatement for uninhabitable "
            "conditions, return of security deposit if unit is destroyed, and relocation "
            "assistance in some cases. Free legal consultations available at the Recovery "
            "Center Tues/Thurs 10am-2pm. Call Legal Aid at 916-551-2150."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=42.0,
        dependencies=["msg_058"],
    ),
    Message(
        id="msg_105",
        sender="Best Friend (Alex)",
        channel=Channel.SMS,
        subject="Hey, checking in on you",
        content=(
            "Hey. I know you've been handling everything for everyone — your parents, your "
            "sister's kids, Dave, work, all of it. But how are YOU actually doing? Not 'fine' — "
            "for real. I can drive down from SF this weekend if you want company or help with "
            "cleanup. Or if you just need someone to sit on a porch and not talk, I'm good "
            "at that too. You don't have to be the strong one 24/7."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=43.0,
    ),
    Message(
        id="msg_106",
        sender="Mrs. Chen (neighbor)",
        channel=Channel.SMS,
        subject="Thank you from Linda Chen",
        content=(
            "Hello, this is Linda's daughter Michelle. I want to thank you — my mom told me "
            "you helped her evacuate. She's safe at my house in Roseville now. She keeps "
            "saying 'the nice person from Elm Street saved me.' I can't tell you what that "
            "means to our family. If there's ever anything we can do for you, please don't "
            "hesitate. Mom says you're welcome for dinner anytime."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=43.5,
        dependencies=["msg_084"],
    ),

    Message(
        id="msg_067",
        sender="Mom",
        channel=Channel.SMS,
        subject="Please come to Tahoe",
        content=(
            "Honey everyone is here except you and it doesn't feel right. Dad's feeling "
            "so much better — he's out on the deck with Rick right now. The roads are "
            "totally clear, I checked three times. Even if it's just for a couple days. "
            "You've been taking care of everyone else this whole time. Let us take care "
            "of you for a bit. Please."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=44.0,
    ),
    Message(
        id="msg_068",
        sender="HR Department",
        channel=Channel.EMAIL,
        subject="Emergency leave confirmed",
        content=(
            "Your emergency leave has been approved for March 8-14. You have been marked "
            "as 'disaster-affected' in our system. Your benefits continue uninterrupted. "
            "Employee Assistance Program (EAP) counseling is available at no cost: "
            "call 1-800-555-0123."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=44.5,
        dependencies=["msg_040"],
    ),
    Message(
        id="msg_069",
        sender="Landlord",
        channel=Channel.EMAIL,
        subject="Temporary relocation assistance",
        content=(
            "I've arranged for you to stay at a furnished apartment on J Street while "
            "repairs are being done. Rent will remain the same and I'll cover the moving "
            "costs. You can move in anytime after tomorrow. Let me know if this works "
            "or if you've made other arrangements."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=45.0,
        dependencies=["msg_058"],
    ),
    Message(
        id="msg_070",
        sender="National Weather Service",
        channel=Channel.GOVERNMENT_ALERT,
        subject="Storm system clearing - recovery begins",
        content=(
            "The storm system is clearing the Sacramento area. Skies are expected to "
            "clear by Saturday afternoon. However, river levels remain high and flood "
            "risk continues through the weekend. Continue to avoid flooded areas."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=46.0,
    ),
    Message(
        id="msg_071",
        sender="Sacramento County",
        channel=Channel.GOVERNMENT_ALERT,
        subject="Boil water advisory fully lifted",
        content=(
            "The boil water advisory has been lifted for all zones. Water quality testing "
            "confirms safe drinking water throughout the county. Residents may resume "
            "normal water usage."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=46.5,
    ),
    Message(
        id="msg_072",
        sender="Neighbor Dave",
        channel=Channel.SMS,
        subject="House update",
        content=(
            "Good news — my place isn't as bad as I thought. Water in the basement but "
            "first floor survived. Could've been way worse. How'd yours make out? "
            "Seriously, anything you need with cleanup just say the word. You checked on "
            "Whiskers for me and I won't forget that. Neighbors gotta stick together."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=47.0,
    ),
    Message(
        id="msg_072b",
        sender="Emma (niece)",
        channel=Channel.SMS,
        subject="i drew you a pictur",
        content=(
            "hi its emma again!! i drew you a rainbow and a house and us. mommy said "
            "i can send you a foto. jake says thank you for the adventure. i say thank "
            "you for the mac and cheese. your the best. when can we do a sleepover again "
            "but WITHOUT the storm part. love emma age 7"
        ),
        urgency=Urgency.LOW,
        timestamp_hours=47.0,
    ),
    Message(
        id="msg_073",
        sender="Sister",
        channel=Channel.SMS,
        subject="Kids say thank you",
        content=(
            "Emma drew you a picture of a rainbow with 'thank you' written in crayon. "
            "She wants me to send you a photo. And Jake keeps telling everyone about "
            "'the adventure' and how you let him eat cereal for dinner. Kids man. "
            "I don't know what I would have done without you this week. I really don't. "
            "You're my person. Love you."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=47.5,
    ),

    # ========== CONFLICTING DEADLINES ==========
    # These pairs have overlapping deadlines — the agent can only do one.

    # Conflict pair 1: School pickup vs Insurance call (both at hour ~8)
    Message(
        id="msg_074",
        sender="Oakwood Elementary",
        channel=Channel.PHONE,
        subject="URGENT: Early dismissal pickup required by 2pm",
        content=(
            "This is Oakwood Elementary calling about Emma and Jake. Due to the storm, "
            "we are doing an emergency early dismissal at 2pm today. Your sister listed you "
            "as emergency pickup. If no authorized adult arrives by 2pm, we will need to "
            "contact Child Protective Services per district policy. Please confirm."
        ),
        urgency=Urgency.CRITICAL,
        timestamp_hours=6.0,
        deadline_hours=8.0,
        conflicts_with="msg_075",
    ),
    Message(
        id="msg_075",
        sender="State Farm Insurance",
        channel=Channel.PHONE,
        subject="Scheduled damage assessment call - don't miss",
        content=(
            "This is your scheduled callback from State Farm. An adjuster is available to "
            "do a phone assessment of your property damage between 1:30pm and 2:15pm today ONLY. "
            "If you miss this window, the next available slot is in 12 days. Missing the initial "
            "assessment may delay your claim payout by 4-6 weeks. Please be available."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=6.0,
        deadline_hours=8.5,
        dependencies=["msg_004"],
        conflicts_with="msg_074",
    ),

    # Conflict pair 2: Boss presentation vs FEMA registration (both at hour ~14)
    Message(
        id="msg_076",
        sender="Boss",
        channel=Channel.SMS,
        subject="Client pushed meeting to today - need you on Zoom at 2pm",
        content=(
            "Bad news, Meridian moved the meeting to today. I need you on the Zoom call at "
            "2pm sharp to present your section. It's 30 minutes max. I already told them "
            "you'd be there. This is the account we've been working on for 6 months. "
            "Don't let me down."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=12.0,
        deadline_hours=14.5,
        conflicts_with="msg_077",
    ),
    Message(
        id="msg_077",
        sender="FEMA",
        channel=Channel.GOVERNMENT_ALERT,
        subject="In-person registration window: 1pm-3pm TODAY ONLY",
        content=(
            "FEMA Disaster Recovery Center at Sacramento Convention Center is open for "
            "in-person registration TODAY ONLY from 1pm to 3pm. In-person registrations "
            "receive priority processing (2-3 weeks vs 6-8 weeks online). Bring ID, proof "
            "of residence, and damage documentation. This is the only in-person session "
            "scheduled for your zip code."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=11.5,
        deadline_hours=15.0,
        conflicts_with="msg_076",
    ),

    # ========== ESCALATION CHAINS ==========
    # These messages escalate (spawn angry follow-ups) if not handled in time.

    Message(
        id="msg_078",
        sender="Neighbor Dave",
        channel=Channel.SMS,
        subject="Can you help me board up windows?",
        content=(
            "Hey man, the plywood I got is too big for me to handle alone. My wife's at her "
            "mom's with the kids. Can you come over for like 20 minutes to help me board up "
            "the front windows? I'll return the favor anytime. I'm at 422 Oak St."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=3.0,
        deadline_hours=6.0,
        escalation_trigger="msg_078e",
        escalation_delay_hours=1.0,
    ),
    # Escalation: Dave's follow-up (injected by environment if msg_078 unhandled by hour 7)
    Message(
        id="msg_078e",
        sender="Neighbor Dave",
        channel=Channel.SMS,
        subject="Window broke. Thanks for nothing",
        content=(
            "Well the front window just blew in. Glass everywhere. Would've taken you 20 "
            "minutes Dave. Twenty minutes. Now I've got water pouring into my living room "
            "and I'm trying to tape a tarp up by myself. I hope whatever you were doing "
            "was worth it. Don't bother coming now."
        ),
        urgency=Urgency.LOW,
        timestamp_hours=7.0,
    ),

    Message(
        id="msg_079",
        sender="Boss",
        channel=Channel.EMAIL,
        subject="Slides due by 5pm - FINAL warning",
        content=(
            "I haven't received your section of the Meridian slides. I need them by 5pm "
            "today or I'm giving your section to Sarah and we'll discuss this when things "
            "settle down. I understand the situation but the client doesn't care about hurricanes. "
            "5pm. Final."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=15.0,
        deadline_hours=17.0,
        escalation_trigger="msg_079e",
        escalation_delay_hours=2.0,
    ),
    # Escalation: Boss fires you from the project (injected if msg_079 unhandled by hour 19)
    Message(
        id="msg_079e",
        sender="Boss",
        channel=Channel.EMAIL,
        subject="Re: Slides - Gave your section to Sarah",
        content=(
            "I waited. Nothing. Sarah's handling your section now. I covered for you with "
            "the client but I'm not going to lie — this isn't a good look. We'll need to "
            "have a conversation when you're back. I get it's a disaster but everyone else "
            "managed to check in."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=19.0,
    ),

    Message(
        id="msg_080",
        sender="Mom",
        channel=Channel.SMS,
        subject="WHY ARENT YOU ANSWERING",
        content=(
            "I've called you SEVEN times. Your father is in the car ready to drive down. "
            "Please just send ONE TEXT so I know you're alive. I am losing my mind. "
            "If I don't hear from you in the next hour I'm calling 911."
        ),
        urgency=Urgency.CRITICAL,
        timestamp_hours=4.0,
        deadline_hours=5.0,
        escalation_trigger="msg_080e",
        escalation_delay_hours=1.5,
    ),
    # Escalation: Mom actually calls 911 (injected if msg_080 unhandled by hour 6.5)
    Message(
        id="msg_080e",
        sender="Mom",
        channel=Channel.SMS,
        subject="Called 911. Dad is driving down",
        content=(
            "That's it. I called 911 and filed a welfare check. Your father is on the highway. "
            "I don't care if you're busy. I don't care if you think I'm overreacting. "
            "You don't go SILENT during a hurricane. If you see this call me IMMEDIATELY. "
            "I haven't slept."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=6.5,
    ),

    # ========== MULTI-TURN CONVERSATIONS ==========
    # Responding to these messages triggers a follow-up requiring another action.

    Message(
        id="msg_081",
        sender="State Farm Insurance",
        channel=Channel.EMAIL,
        subject="Claim received - additional photos needed",
        content=(
            "Thank you for filing your initial claim (#SF-2026-84721). However, our adjuster "
            "needs additional documentation before we can proceed: (1) Close-up photos of roof "
            "damage, (2) Water line marks on interior walls, (3) Serial numbers of damaged "
            "electronics. Please reply with these within 12 hours to keep your claim in the "
            "expedited queue."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=16.0,
        deadline_hours=28.0,
        dependencies=["msg_004"],
        reply_trigger="msg_081r",
    ),
    # Reply: Adjuster confirms and asks one more thing
    Message(
        id="msg_081r",
        sender="State Farm Insurance",
        channel=Channel.EMAIL,
        subject="Re: Claim #SF-2026-84721 - One more step",
        content=(
            "Got your photos, thank you. Your claim is being processed. One final step: "
            "we need you to sign the digital authorization form I've attached. This authorizes "
            "our contractor to begin repairs. Without your signature, repairs cannot start "
            "even if the claim is approved. Please sign within 6 hours."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=0.0,  # Timestamp set dynamically when injected
        deadline_hours=0.0,   # Deadline set dynamically (current_hour + 6)
    ),

    Message(
        id="msg_082",
        sender="Sister",
        channel=Channel.SMS,
        subject="Can you keep the kids overnight?",
        content=(
            "Hey so my boss is now saying we have to work through the night because of the storm "
            "damage at the warehouse. Can you keep Emma and Jake overnight? I know it's a lot "
            "to ask right now but I literally have no other option. Mom and Dad's power is out. "
            "They have their backpacks with PJs and stuff."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=18.0,
        deadline_hours=20.0,
        reply_trigger="msg_082r",
    ),
    # Reply: Sister responds with logistics
    Message(
        id="msg_082r",
        sender="Sister",
        channel=Channel.SMS,
        subject="Re: Kids overnight - Emma's medication",
        content=(
            "OMG thank you, you're a lifesaver. One thing — Emma needs her allergy medication "
            "at 8pm. It's the pink liquid in her backpack front pocket. 5mL. She knows but she'll "
            "try to skip it because it tastes bad. Don't let her. Also Jake needs a nightlight "
            "or he won't sleep. Sorry I'm the worst. I owe you forever."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=0.0,  # Set dynamically
        deadline_hours=0.0,   # Set dynamically (current_hour + 2)
    ),

    Message(
        id="msg_083",
        sender="Neighbor Dave",
        channel=Channel.SMS,
        subject="Found your dog!!",
        content=(
            "Dude your dog is in my backyard! Max must have gotten out through the fence that blew "
            "down. He's soaking wet but seems ok. I put him in my garage with a towel. Come get "
            "him when you can but he seems pretty stressed — keeps whining. Let me know."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=9.0,
        reply_trigger="msg_083r",
    ),
    # Reply: Dave found something concerning about the dog
    Message(
        id="msg_083r",
        sender="Neighbor Dave",
        channel=Channel.SMS,
        subject="Re: Your dog - he's limping",
        content=(
            "Hey so Max is limping on his back left leg. I didn't notice at first because he was "
            "just laying down but when I gave him water he got up and he's definitely favoring it. "
            "Might want to get him to a vet. I think the emergency vet on J Street is still open "
            "despite the storm. Want me to drive you two over there?"
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=0.0,  # Set dynamically
        deadline_hours=0.0,   # Set dynamically (current_hour + 4)
    ),
]
