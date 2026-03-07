"""
Pre-written message bank for the CrisisInbox environment.

70+ messages across 48 simulated hours from 8 sender profiles:
  - National Weather Service / FEMA (government)
  - Mom & Dad (family)
  - Sister (family)
  - Boss / HR (employer)
  - State Farm Insurance (insurance)
  - Delta Airlines (travel)
  - Oakwood Elementary (school)
  - Neighbor Dave (community)

Messages are organized by arrival time and designed to create realistic
cognitive overload with conflicting obligations and dependency chains.
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
]
