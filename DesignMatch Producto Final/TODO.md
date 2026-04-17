# DesignMatch MVP to Real Product Transformation - TODO

## Approved Plan Steps (Progress tracked here)

### 1. Update models/models.py [✅ COMPLETED]
   - Add `phone` column to User model (for both roles).
   - Add `project_description` to User for clients (nullable).
   - Add `phone` to Designer.

### 2. Update database/db.py [✅ COMPLETED]
   - Disabled demo seed_data() function for real usage.

### 3. Update routes/auth_routes.py [✅ COMPLETED]
   - Enhanced `/api/users` POST with new fields, auto Designer creation, skills support.
   - Removed demo text from messages.
   - Updated /info to production description.
   - Renamed login_demo → login.

### 4. Update static/index.html [✅ COMPLETED]
   - Removed demo text/buttons.
   - Added full registration form with phone, conditional designer/client fields.
   - Replaced footer with simple editable placeholder.

### 5. Update static/script.js [✅ COMPLETED]
   - Enhanced handleRegister for new fields/skills.
   - Added toggleRoleFields.

### 6. Update static/styles.css [✅ COMPLETED]
   - No major changes needed.

### 7. Test & DB Migration [IN PROGRESS]
   - Deleted DB, new schema on next run.
   - Run `python app.py` to test.

### 7. Test & DB Migration [PENDING]
   - Delete instance/designmatch.db or migrate.
   - Run `python app.py`, test registration/project/matches.

### 8. Final verification & completion [PENDING]

Updated after each step completed.

