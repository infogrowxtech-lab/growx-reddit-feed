# Growx Tech IT – Reddit Auto Poster (GitHub + IFTTT, free)

Ye system cloud pe chalta hai. PC on rakhne ki zaroorat nahi hai aur Reddit API key bhi nahi chahiye.

## Kaise chalta hai
1. GitHub roz 3 baar (lagbhag 10:15, 14:45, 20:15 IST) check karta hai aur din bhar me **0–2 posts** (mahine me max 26, kyunki IFTTT free plan me 1,000 credits/mahina hain) `docs/feed.xml` (RSS feed) me daalta hai.
2. IFTTT ka applet us feed ko dekhta rehta hai. Jaise hi naya item aata hai, wo use Reddit pe text post kar deta hai.
3. Pehle **14 din** sirf 1 post/day jayega, taaki naya account safe rahe.

## Proofreading
- `queue/` me jo files hain, wahi aage post hongi. Inka order number se chalta hai (001, 002, ...).
- Kisi file ko ✏️ se edit kar sakte ho. Koi post nahi chahiye to us file ko delete kar do.
- Jo post feed me chale gaye, wo `posted/` folder me milenge.

## Rokna
Repo me `PAUSE` naam ki file bana do. Use delete karoge to posting phir chalu ho jayegi.

## Naya post
`queue/031.md`:
```
---
subreddit: smallbusiness
title: Aapka title
---

Post ka text...
```
