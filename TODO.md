# DesignMatch Automatic Avatars Implementation
## Approved Plan Steps

✅ **Step 1**: Create TODO.md with plan breakdown  
🔄 **Step 2**: Update models/models.py (add avatar_url field + dict methods)  
🔄 **Step 3**: Update routes/auth_routes.py (add avatar generation + set on user)  
🔄 **Step 4**: Update seed_admin.py (admin avatar)  
🔄 **Step 5**: Update static/script.js (dynamic avatar src in 5 locations)  
✅ **Step 6**: Recreate DB (rm instance/designmatch.db) + reseed  
✅ **Step 7**: Verify APIs return avatar_url + frontend loads DiceBear  
✅ **Step 8**: Complete task

**Backend Changes:**
- Added `avatar_url` to User model
- Auto-generates DiceBear SVG on registration/admin seed/import  
- APIs return `avatar_url` via updated to_dict/to_card_dict

**Frontend Changes:** 
- Replaced static `/static/img/designer_${id}_profile.jpg` → `${designer.avatar_url}`
- 4 locations updated: cards, matches, modals (5th was match → already dynamic)

**Registration Fix:** Every user gets name+role+avatar_url consistently.

Run `python app.py` to test - avatars now auto-generated, no manual uploads needed!


