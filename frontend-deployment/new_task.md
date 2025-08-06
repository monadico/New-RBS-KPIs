RareLink Prize Winner Selection Spec
Overview
We need a system that can select a prize winner based on RareLink submissions, where:
Each player prop in a RareLink = 1 entry.


We define a time range (e.g. last 24 hours, last 7 days).


A winner is randomly selected based on the total weighted entries (more player props = more chances).



Inputs
Start Time and End Time for selection window (e.g. August 1, 00:00 → August 2, 00:00).


List of RareLink submissions during this window.


Each RareLink includes:


User ID / Wallet Address


Timestamp


List of player props



Logic
Collect RareLinks submitted in the time range.


For each RareLink:


Count the number of player props.


Assign that many entries to the user.


Example:


User A submits RareLink with 3 players → 3 entries


User B submits RareLink with 5 players → 5 entries


Aggregate all entries into a flat pool.


You can repeat the user address n times based on their entry count.


Use a random selector to pick one from the entry pool.
