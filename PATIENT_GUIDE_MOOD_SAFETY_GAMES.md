# 🎯 MEMORA Patient Dashboard - How to Use Mood & Safety Features

**Updated:** September 25, 2026  
**Version:** 2.0 - With Button Acknowledgment Feedback

---

## 📝 Mood Tracking - Step by Step

### How It Works:

```
1. PATIENT OPENS MOOD PAGE
   └→ Sees 5 big mood buttons in a row
      • 😊 Very Happy
      • 🙂 Happy
      • 😐 Okay
      • 😟 Sad
      • 😔 Very Sad

2. PATIENT CLICKS ON MOOD
   └→ Button immediately shows selection
      • Button border turns GREEN ✅
      • Button background turns light green
      • Button grows slightly (1.1x size)
   └→ Note section appears below
      "Add a note (optional)"
   └→ Save/Clear buttons appear

3. PATIENT ADDS NOTE (OPTIONAL)
   └→ Can type up to 500 characters
   └→ Example: "Great day! Got a good night's sleep"

4. PATIENT CLICKS "💾 SAVE MOOD"
   └→ IMMEDIATE FEEDBACK:
      • Button text changes to "⏳ Saving..."
      • Button becomes DISABLED (grayed out)
      • Cannot click again (prevents double-save)
   └→ Application sends mood to server
   └→ Server saves mood to database

5. SUCCESS! CONFIRMATION APPEARS
   └→ Green success alert displays:
      "✓ Your mood has been saved 2:15 PM"
      (with exact timestamp)
   └→ Mood buttons hide
   └→ "Today" section shows:
      "😐 Okay
       Great day! Got a good night's sleep
       Today at 2:15 PM"

6. HISTORY UPDATES
   └→ Mood appears in "Your Mood This Week" section
   └→ Can see last 14 days of moods
```

### Important Features:
- ✅ **Can only save mood once per day** (each new save updates today)
- ✅ **Notes are optional** (can save mood without note)
- ✅ **Timestamp shows when saved**
- ✅ **Mood appears in caregiver dashboard** (caregiver can monitor)
- ✅ **14-day history** (see trends over time)

---

## 🆘 Safety - Emergency Alert System

### How It Works:

```
1. PATIENT OPENS SAFETY PAGE
   └→ Sees safety status card
      Status: 🛡️ "SAFE" or ⚠️ "ALERT ACTIVE"
   └→ Large red emergency button
      "🆘 EMERGENCY"
   └→ Hint text: "Tap if you need immediate help"

2. PATIENT NEEDS HELP - CLICKS EMERGENCY BUTTON
   └→ Browser shows confirmation dialog:
      "Are you sure you need help?"
   └→ Two choices:
      ☑️ OK (Send emergency alert)
      ☐ Cancel (Don't send, go back)

3A. IF PATIENT CLICKS "CANCEL"
   └→ Nothing happens
   └→ Button stays normal
   └→ No alert sent

3B. IF PATIENT CLICKS "OK"
   └→ IMMEDIATE FEEDBACK:
      • Button text changes to "⏳ Sending Alert..."
      • Button becomes DISABLED
      • Cannot click again
   └→ Application sends SOS to server
   └→ Server creates emergency alert
   └→ Server notifies caregiver

4. SUCCESS! ALERT SENT
   └→ Button changes to "✓ Alert Sent!" (green background)
   └→ Success message appears:
      "Your caregiver has been alerted."
   └→ Safety status card turns RED
      Status: "ALERT ACTIVE"
      Icon: "⚠️"
   └→ Message: "Your caregiver has been alerted."

5. AUTO RESET (After 3 seconds)
   └→ Button resets to "🆘 EMERGENCY" (red)
   └→ Button becomes ENABLED again
   └→ Status card stays RED (alert still active)
   └→ Caregiver can see alert on their dashboard

6. CAREGIVER RESPONDS
   └→ Caregiver views alert on their dashboard
   └→ Caregiver can see:
      • Patient name
      • Time alert was sent
      • Status (Active or Resolved)
   └→ Caregiver goes to patient
   └→ Caregiver resolves alert
   └→ Status changes back to "SAFE"
```

### Important Features:
- ✅ **Confirmation required** (prevents accidental alerts)
- ✅ **Caregiver notified immediately** (real-time)
- ✅ **Clear feedback** (button shows success)
- ✅ **Status updates** (safety card shows alert status)
- ✅ **Cannot be dismissed by patient** (caregiver must resolve)
- ✅ **Button resets automatically** (ready for next use)

---

## 🎮 Games - Cognitive Exercise

### Available Games:

#### 1. Memory Match 🧠
- Click to flip cards
- Match pairs of emojis
- Complete all 6 pairs
- Time is tracked
- Score shown at end

#### 2. Attention Test 👁️
- Look at grid of shapes
- Find the one that's different
- Quick reflexes needed
- Shows reaction time

#### 3. Photo / Name Match 📸
- See photo of family member
- Choose correct name from options
- Gets progressively harder
- Points for correct answers

#### 4. Who Is This? 🧑
- Read person's name
- Click correct photo
- Tests memory of relationships
- Shows score at end

---

## 📱 Using on Different Devices

### On Phone/Tablet:
- Buttons are LARGE and easy to tap
- Full screen for games
- Portrait or landscape mode works
- Touch-friendly design
- No keyboard needed for mood/safety

### On Computer:
- Mouse/trackpad to click
- Keyboard can be used for games
- Larger screen shows more information
- Better for family discussions

---

## 🎯 Best Practices

### For Patients:
1. **Check in daily** with your mood
2. **Add notes** about what you did or how you feel
3. **Look at trends** in your mood history
4. **Use emergency button** only when truly needed
5. **Play games regularly** for brain exercise

### For Caregivers:
1. **Check patient alerts** regularly
2. **Respond quickly** to emergency alerts
3. **Review mood trends** to see patterns
4. **Encourage daily mood check-in**
5. **Monitor game progress** to see improvement

---

## ❓ Troubleshooting

### Button doesn't seem to click:
- Make sure button is enabled (not grayed out)
- If grayed out, another action is in progress
- Wait for button to return to normal color
- Try clicking again

### Confirmation not appearing after save:
- Check that you have internet connection
- Look for green alert box below
- May disappear after 5 seconds automatically
- Scroll down to see mood history

### Emergency button won't work:
- Check that browser allows alerts
- Make sure you confirmed the dialog
- Wait for "Sending Alert..." to complete
- If error persists, refresh page and try again

### Mood/Alert doesn't appear on caregiver view:
- Ensure caregiver is logged in
- Caregiver may need to refresh page
- Check network connection
- Contact system administrator if persistent

---

## 🔐 Privacy & Security

- Your mood entries are **private** - only you and caregivers can see
- Emergency alerts go **only to assigned caregivers**
- Notes are **not shared** with other patients
- Data is **encrypted** in transit and storage
- You can **delete old entries** if desired

---

## ✅ Checklist - Everything Working

- [✓] Mood buttons show selection (green highlight)
- [✓] Save button shows "Saving..." state
- [✓] Success confirmation appears with timestamp
- [✓] Mood history displays correctly
- [✓] SOS button shows confirmation dialog
- [✓] Alert button shows "Sending..." state
- [✓] Success message displays "Alert Sent!"
- [✓] Safety status card updates to "ALERT ACTIVE"
- [✓] Button auto-resets after 3 seconds
- [✓] Caregiver can see alerts
- [✓] Games load and play correctly
- [✓] Images display in photo games

---

## 📞 Support

If you experience any issues:
1. Try refreshing the page (Ctrl+R or Cmd+R)
2. Clear browser cache if buttons not updating
3. Check internet connection
4. Contact caregiver or administrator
5. Check system logs for errors

---

**Version 2.0 - Button Acknowledgment Enhanced** ✅  
All features tested and verified working!
